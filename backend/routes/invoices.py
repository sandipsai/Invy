# routes/invoices.py - the core of the application

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..utils import (
    calculate_invoice_totals,
    compute_line_total,
    generate_invoice_number,
    log_activity,
    recalculate_payment_status,
)

router = APIRouter(prefix="/invoices", tags=["Invoices"])


# Status transition rules
# Defines which status changes are legal. Prevents nonsensical transitions
# like going from "paid" back to "draft" or "cancelled" to "sent".

ALLOWED_TRANSITIONS: dict[models.InvoiceStatus, set[models.InvoiceStatus]] = {
    models.InvoiceStatus.DRAFT: {
        models.InvoiceStatus.SENT,
        models.InvoiceStatus.CANCELLED,
    },
    models.InvoiceStatus.SENT: {
        models.InvoiceStatus.VIEWED,
        models.InvoiceStatus.PAID,
        models.InvoiceStatus.OVERDUE,
        models.InvoiceStatus.CANCELLED,
    },
    models.InvoiceStatus.VIEWED: {
        models.InvoiceStatus.PAID,
        models.InvoiceStatus.PARTIAL,
        models.InvoiceStatus.OVERDUE,
        models.InvoiceStatus.CANCELLED,
    },
    models.InvoiceStatus.PARTIAL: {
        models.InvoiceStatus.PAID,
        models.InvoiceStatus.OVERDUE,
        models.InvoiceStatus.CANCELLED,
    },
    models.InvoiceStatus.OVERDUE: {
        models.InvoiceStatus.PAID,
        models.InvoiceStatus.PARTIAL,
        models.InvoiceStatus.CANCELLED,
    },
    models.InvoiceStatus.PAID: set(),  # terminal — no transitions out
    models.InvoiceStatus.CANCELLED: set(),  # terminal
}


def _get_or_404(invoice_id: int, db: Session) -> models.Invoice:
    inv = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv


def _build_items(
    db: Session,
    invoice: models.Invoice,
    items_data: list[schemas.InvoiceItemCreate],
    invoice_tax_percent: float,
) -> None:
    """
    Delete existing items and replace with new ones.
    Used on both create and update. Rebuilds line_total for every item.
    """
    # Delete old items first (only relevant on update)
    for existing in invoice.items:
        db.delete(existing)
    db.flush()  # flush deletions before inserting new rows

    for i, item_data in enumerate(items_data):
        # If per-item tax not set, fall back to invoice-level tax
        item_tax = (
            item_data.tax_percent
            if item_data.tax_percent is not None
            else invoice_tax_percent
        )
        line = compute_line_total(
            item_data.quantity, item_data.unit_price, item_data.discount_percent or 0
        )
        db.add(
            models.InvoiceItem(
                invoice_id=invoice.id,
                sort_order=item_data.sort_order if item_data.sort_order else i,
                description=item_data.description,
                detail=item_data.detail or "",
                quantity=item_data.quantity,
                unit=item_data.unit or "",
                unit_price=item_data.unit_price,
                discount_percent=item_data.discount_percent or 0.0,
                tax_percent=item_tax,
                line_total=line,
            )
        )


# List / Search


@router.get("/", response_model=list[schemas.InvoiceListOut])
def list_invoices(
    status: str = Query(default="", description="Filter by status"),
    client_id: int = Query(default=0, description="Filter by client"),
    search: str = Query(default="", description="Search invoice number or client name"),
    from_date: str = Query(default="", description="Issue date ≥ (YYYY-MM-DD)"),
    to_date: str = Query(default="", description="Issue date ≤ (YYYY-MM-DD)"),
    overdue_only: bool = Query(default=False),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(models.Invoice)

    if status:
        q = q.filter(models.Invoice.status == status)
    if client_id:
        q = q.filter(models.Invoice.client_id == client_id)
    if from_date:
        q = q.filter(models.Invoice.issue_date >= from_date)
    if to_date:
        q = q.filter(models.Invoice.issue_date <= to_date)
    if overdue_only:
        q = q.filter(models.Invoice.status == models.InvoiceStatus.OVERDUE)
    if search:
        # Join client table so we can search by client name too
        q = q.join(models.Client).filter(
            or_(
                models.Invoice.number.ilike(f"%{search}%"),
                models.Client.name.ilike(f"%{search}%"),
                models.Invoice.po_number.ilike(f"%{search}%"),
            )
        )

    return q.order_by(models.Invoice.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{invoice_id}", response_model=schemas.InvoiceOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    return _get_or_404(invoice_id, db)


# Create


@router.post("/", response_model=schemas.InvoiceOut, status_code=201)
def create_invoice(data: schemas.InvoiceCreate, db: Session = Depends(get_db)):
    # Verify client exists
    client = (
        db.query(models.Client)
        .filter(
            models.Client.id == data.client_id,
            models.Client.is_active == True,
        )
        .first()
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found or inactive")

    # Compute totals from the submitted items
    totals = calculate_invoice_totals(
        [i.model_dump() for i in data.items],
        data.tax_percent or 0,
        data.discount_percent or 0,
    )

    invoice = models.Invoice(
        number=generate_invoice_number(db),
        client_id=data.client_id,
        issue_date=data.issue_date,
        due_date=data.due_date,
        currency=data.currency or client.currency,
        tax_label=data.tax_label or "Tax",
        tax_percent=data.tax_percent or 0.0,
        discount_percent=data.discount_percent or 0.0,
        notes=data.notes or "",
        internal_notes=data.internal_notes or "",
        terms=data.terms or "",
        footer=data.footer or "",
        po_number=data.po_number or "",
        balance_due=totals["total"],
        **totals,
    )
    db.add(invoice)
    db.flush()  # get invoice.id before building items

    _build_items(db, invoice, data.items, invoice.tax_percent)

    log_activity(
        db, invoice.id, "created", f"Invoice {invoice.number} created as draft"
    )

    db.commit()
    db.refresh(invoice)
    return invoice


# Update (draft only)


@router.put("/{invoice_id}", response_model=schemas.InvoiceOut)
def update_invoice(
    invoice_id: int, data: schemas.InvoiceUpdate, db: Session = Depends(get_db)
):
    invoice = _get_or_404(invoice_id, db)

    # Only allow editing drafts — once sent, create a credit note instead
    if invoice.status != models.InvoiceStatus.DRAFT:
        raise HTTPException(
            status_code=409,
            detail="Only draft invoices can be edited. Change status first or create a credit note.",
        )

    # Apply scalar field updates
    update_fields = data.model_dump(exclude_unset=True, exclude={"items"})
    for field, value in update_fields.items():
        setattr(invoice, field, value)

    # Rebuild items if provided
    if data.items is not None:
        _build_items(db, invoice, data.items, invoice.tax_percent)
        # Recompute totals after item change
        db.flush()
        totals = calculate_invoice_totals(
            invoice.items, invoice.tax_percent, invoice.discount_percent
        )
        for field, value in totals.items():
            setattr(invoice, field, value)
        invoice.balance_due = invoice.total - invoice.amount_paid

    log_activity(db, invoice.id, "updated", "Invoice details updated")
    db.commit()
    db.refresh(invoice)
    return invoice


# Status transition


@router.patch("/{invoice_id}/status", response_model=schemas.InvoiceOut)
def change_status(
    invoice_id: int,
    data: schemas.StatusUpdate,
    db: Session = Depends(get_db),
):
    invoice = _get_or_404(invoice_id, db)
    new_status = data.status

    # Enforce the state machine
    if new_status not in ALLOWED_TRANSITIONS.get(invoice.status, set()):
        raise HTTPException(
            status_code=409,
            detail=f"Cannot transition from '{invoice.status.value}' to '{new_status.value}'",
        )

    old_status = invoice.status.value
    invoice.status = new_status

    if new_status == models.InvoiceStatus.PAID and not invoice.paid_date:
        invoice.paid_date = date.today().isoformat()

    log_activity(
        db,
        invoice.id,
        "status_changed",
        f"Status changed from {old_status} to {new_status.value}",
        old_value=old_status,
        new_value=new_status.value,
    )
    db.commit()
    db.refresh(invoice)
    return invoice


# Payments


@router.post(
    "/{invoice_id}/payments", response_model=schemas.PaymentOut, status_code=201
)
def record_payment(
    invoice_id: int,
    data: schemas.PaymentCreate,
    db: Session = Depends(get_db),
):
    invoice = _get_or_404(invoice_id, db)

    if invoice.status in (models.InvoiceStatus.DRAFT, models.InvoiceStatus.CANCELLED):
        raise HTTPException(
            status_code=409,
            detail="Cannot record payment on a draft or cancelled invoice",
        )

    if data.amount > invoice.balance_due + 0.001:  # small epsilon for float rounding
        raise HTTPException(
            status_code=400,
            detail=f"Payment amount ({data.amount}) exceeds balance due ({invoice.balance_due})",
        )

    payment = models.Payment(
        invoice_id=invoice_id,
        amount=data.amount,
        method=data.method,
        reference=data.reference or "",
        payment_date=data.payment_date,
        notes=data.notes or "",
    )
    db.add(payment)
    db.flush()

    # Recompute invoice totals and auto-advance status
    recalculate_payment_status(invoice)

    log_activity(
        db,
        invoice_id,
        "payment_recorded",
        f"Payment of {invoice.currency} {data.amount} recorded via {data.method.value}",
        new_value=str(data.amount),
    )
    db.commit()
    db.refresh(payment)
    return payment


@router.delete("/{invoice_id}/payments/{payment_id}", status_code=204)
def delete_payment(invoice_id: int, payment_id: int, db: Session = Depends(get_db)):
    invoice = _get_or_404(invoice_id, db)
    payment = (
        db.query(models.Payment)
        .filter(
            models.Payment.id == payment_id,
            models.Payment.invoice_id == invoice_id,
        )
        .first()
    )
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    db.delete(payment)
    db.flush()
    recalculate_payment_status(invoice)
    log_activity(
        db, invoice_id, "payment_deleted", f"Payment of {payment.amount} removed"
    )
    db.commit()


# Duplicate


@router.post(
    "/{invoice_id}/duplicate", response_model=schemas.InvoiceOut, status_code=201
)
def duplicate_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """
    Create a new draft invoice with the same client, items and settings.
    Useful when billing the same client monthly.
    """
    source = _get_or_404(invoice_id, db)
    today = date.today().isoformat()

    new_inv = models.Invoice(
        number=generate_invoice_number(db),
        client_id=source.client_id,
        status=models.InvoiceStatus.DRAFT,
        issue_date=today,
        due_date=today,  # caller should update via PUT after duplication
        currency=source.currency,
        tax_label=source.tax_label,
        tax_percent=source.tax_percent,
        discount_percent=source.discount_percent,
        notes=source.notes,
        internal_notes=source.internal_notes,
        terms=source.terms,
        footer=source.footer,
        po_number=source.po_number,
        subtotal=source.subtotal,
        discount_amount=source.discount_amount,
        tax_amount=source.tax_amount,
        total=source.total,
        balance_due=source.total,
    )
    db.add(new_inv)
    db.flush()

    for item in source.items:
        db.add(
            models.InvoiceItem(
                invoice_id=new_inv.id,
                sort_order=item.sort_order,
                description=item.description,
                detail=item.detail,
                quantity=item.quantity,
                unit=item.unit,
                unit_price=item.unit_price,
                discount_percent=item.discount_percent,
                tax_percent=item.tax_percent,
                line_total=item.line_total,
            )
        )

    log_activity(db, new_inv.id, "created", f"Duplicated from invoice {source.number}")
    db.commit()
    db.refresh(new_inv)
    return new_inv


# Delete (draft only)


@router.delete("/{invoice_id}", status_code=204)
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = _get_or_404(invoice_id, db)
    if invoice.status != models.InvoiceStatus.DRAFT:
        raise HTTPException(
            status_code=409,
            detail="Only draft invoices can be deleted. Cancel the invoice first.",
        )
    db.delete(invoice)
    db.commit()
