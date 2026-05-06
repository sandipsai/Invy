# routes/clients.py — all /clients endpoints

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..utils import attach_client_stats

router = APIRouter(prefix="/clients", tags=["Clients"])


def _get_or_404(client_id: int, db: Session) -> models.Client:
    """Fetch a client or raise 404. DRY helper used by multiple routes."""
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


def _enrich(client: models.Client) -> schemas.ClientOut:
    """Convert ORM object → schema, injecting computed stats."""
    out = schemas.ClientOut.model_validate(client)
    out.__dict__.update(attach_client_stats(client))
    return out


@router.get("/", response_model=list[schemas.ClientOut])
def list_clients(
    search: str = Query(default="", description="Filter by name, email, or company"),
    is_active: bool = Query(default=True),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    """
    List all clients with optional search and pagination.
    'skip' and 'limit' are the standard pagination pattern:
    page 1 = skip=0 limit=50, page 2 = skip=50 limit=50, etc.
    """
    q = db.query(models.Client).filter(models.Client.is_active == is_active)
    if search:
        pattern = f"%{search}%"
        # or_() lets us search across multiple columns in one query
        q = q.filter(
            or_(
                models.Client.name.ilike(pattern),
                models.Client.email.ilike(pattern),
                models.Client.company.ilike(pattern),
            )
        )
    clients = q.order_by(models.Client.name).offset(skip).limit(limit).all()
    return [_enrich(c) for c in clients]


@router.get("/{client_id}", response_model=schemas.ClientOut)
def get_client(client_id: int, db: Session = Depends(get_db)):
    return _enrich(_get_or_404(client_id, db))


@router.post("/", response_model=schemas.ClientOut, status_code=201)
def create_client(data: schemas.ClientCreate, db: Session = Depends(get_db)):
    # Check uniqueness before inserting — friendlier than a DB IntegrityError
    if db.query(models.Client).filter(models.Client.email == data.email).first():
        raise HTTPException(
            status_code=409, detail="A client with this email already exists"
        )
    client = models.Client(**data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return _enrich(client)


@router.patch("/{client_id}", response_model=schemas.ClientOut)
def update_client(
    client_id: int, data: schemas.ClientUpdate, db: Session = Depends(get_db)
):
    client = _get_or_404(client_id, db)
    # model_dump(exclude_unset=True) only returns fields the caller actually sent,
    # so fields omitted from the request body are not overwritten with None.
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    db.commit()
    db.refresh(client)
    return _enrich(client)


@router.delete("/{client_id}", status_code=204)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = _get_or_404(client_id, db)
    # Soft-delete: mark inactive rather than destroying data.
    # Invoices referencing this client remain intact and queryable.
    client.is_active = False
    db.commit()


@router.get("/{client_id}/invoices", response_model=list[schemas.InvoiceListOut])
def get_client_invoices(client_id: int, db: Session = Depends(get_db)):
    """All invoices for a specific client — useful for the client detail page."""
    _get_or_404(client_id, db)
    invoices = (
        db.query(models.Invoice)
        .filter(models.Invoice.client_id == client_id)
        .order_by(models.Invoice.created_at.desc())
        .all()
    )
    return invoices
