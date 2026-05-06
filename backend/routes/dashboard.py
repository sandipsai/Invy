# routes/dashboard.py — aggregated stats for the home screen

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=schemas.DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    """
    Single endpoint that returns everything the dashboard page needs.
    Avoids the frontend making 6 separate requests on load.
    """
    invoices = db.query(models.Invoice).all()

    paid = [i for i in invoices if i.status == models.InvoiceStatus.PAID]
    sent = [i for i in invoices if i.status == models.InvoiceStatus.SENT]
    viewed = [i for i in invoices if i.status == models.InvoiceStatus.VIEWED]
    partial = [i for i in invoices if i.status == models.InvoiceStatus.PARTIAL]
    overdue = [i for i in invoices if i.status == models.InvoiceStatus.OVERDUE]
    drafts = [i for i in invoices if i.status == models.InvoiceStatus.DRAFT]

    recent = (
        db.query(models.Invoice)
        .order_by(models.Invoice.created_at.desc())
        .limit(10)
        .all()
    )

    return schemas.DashboardStats(
        total_clients=db.query(models.Client)
        .filter(models.Client.is_active == True)
        .count(),
        total_invoices=len(invoices),
        total_revenue=round(sum(i.amount_paid for i in paid), 2),
        outstanding_amount=round(
            sum(i.balance_due for i in sent + viewed + partial), 2
        ),
        overdue_amount=round(sum(i.balance_due for i in overdue), 2),
        draft_count=len(drafts),
        sent_count=len(sent) + len(viewed),
        paid_count=len(paid),
        overdue_count=len(overdue),
        recent_invoices=recent,
    )
