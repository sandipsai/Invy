# models.py — every database table as a Python class.
# Each class attribute maps to one column. SQLAlchemy translates
# Python operations on these objects into SQL automatically.

from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey,
    DateTime, Text, Boolean, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base


#  Enums 
# Using Python enums (+ SQLAlchemy's Enum column type) means the database
# will reject any value not in the list — data integrity at the DB level.

class InvoiceStatus(str, enum.Enum):
    DRAFT     = "draft"
    SENT      = "sent"
    VIEWED    = "viewed"   # client opened the payment link
    PARTIAL   = "partial"  # partially paid
    PAID      = "paid"
    OVERDUE   = "overdue"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD   = "credit_card"
    CASH          = "cash"
    CHEQUE        = "cheque"
    OTHER         = "other"


#  Mixin 
# A mixin adds shared columns to multiple models without repeating them.
# Every table gets id, created_at, updated_at for free.

class TimestampMixin:
    id         = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)


#  Models 

class Client(TimestampMixin, Base):
    __tablename__ = "clients"

    name            = Column(String(255), nullable=False)
    email           = Column(String(255), unique=True, nullable=False, index=True)
    phone           = Column(String(50),  default="")
    company         = Column(String(255), default="")  # company they work for
    billing_address = Column(Text, default="")
    shipping_address= Column(Text, default="")         # may differ from billing
    tax_id          = Column(String(100), default="")  # VAT / GST number
    currency        = Column(String(3),   default="USD")
    notes           = Column(Text, default="")
    is_active       = Column(Boolean, default=True)    # soft-delete flag

    invoices = relationship("Invoice", back_populates="client",
                            cascade="all, delete-orphan")


class Invoice(TimestampMixin, Base):
    __tablename__ = "invoices"

    number      = Column(String(20), unique=True, nullable=False, index=True)
    client_id   = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    status      = Column(SAEnum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False)

    issue_date  = Column(String(10), nullable=False)  # ISO date: "YYYY-MM-DD"
    due_date    = Column(String(10), nullable=False)
    paid_date   = Column(String(10), nullable=True)   # set when status → paid

    currency    = Column(String(3), default="USD")
    tax_label   = Column(String(50), default="Tax")   # e.g. "VAT", "GST"
    tax_percent = Column(Float, default=0.0)
    discount_percent = Column(Float, default=0.0)     # invoice-level discount

    # Stored totals — computed on write, read directly without recalculating.
    # Denormalisation trade-off: slight redundancy in exchange for fast reads.
    subtotal    = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    tax_amount  = Column(Float, default=0.0)
    total       = Column(Float, default=0.0)
    amount_paid = Column(Float, default=0.0)          # sum of all payments
    balance_due = Column(Float, default=0.0)          # total - amount_paid

    # Invoice content
    notes       = Column(Text, default="")            # visible to client
    internal_notes = Column(Text, default="")         # private, not on PDF
    terms       = Column(Text, default="")            # payment terms text
    footer      = Column(Text, default="")            # e.g. "Thank you!"
    po_number   = Column(String(100), default="")     # client's purchase order ref

    client   = relationship("Client", back_populates="invoices")
    items    = relationship("InvoiceItem", back_populates="invoice",
                            cascade="all, delete-orphan", order_by="InvoiceItem.id")
    payments = relationship("Payment", back_populates="invoice",
                            cascade="all, delete-orphan")
    activity = relationship("ActivityLog", back_populates="invoice",
                            cascade="all, delete-orphan", order_by="ActivityLog.created_at")


class InvoiceItem(Base):
    """One line on an invoice — a product or service being billed."""
    __tablename__ = "invoice_items"

    id          = Column(Integer, primary_key=True, index=True)
    invoice_id  = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    sort_order  = Column(Integer, default=0)           # controls display order
    description = Column(String(500), nullable=False)
    detail      = Column(Text, default="")             # optional sub-description
    quantity    = Column(Float, nullable=False)
    unit        = Column(String(50), default="")       # e.g. "hrs", "units", "GB"
    unit_price  = Column(Float, nullable=False)
    discount_percent = Column(Float, default=0.0)      # per-item discount
    tax_percent = Column(Float, default=0.0)           # per-item tax override
    line_total  = Column(Float, nullable=False)        # qty × price − discount

    invoice = relationship("Invoice", back_populates="items")


class Payment(TimestampMixin, Base):
    """Records money received against an invoice. Supports partial payments."""
    __tablename__ = "payments"

    invoice_id      = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    amount          = Column(Float, nullable=False)
    method          = Column(SAEnum(PaymentMethod), default=PaymentMethod.BANK_TRANSFER)
    reference       = Column(String(255), default="")  # bank ref, cheque no., etc.
    payment_date    = Column(String(10), nullable=False)  # ISO date
    notes           = Column(Text, default="")

    invoice = relationship("Invoice", back_populates="payments")


class ActivityLog(Base):
    """
    Append-only audit trail for every state change on an invoice.
    Lets you answer: who did what, and when? (crucial for disputes)
    """
    __tablename__ = "activity_log"

    id          = Column(Integer, primary_key=True, index=True)
    invoice_id  = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    event       = Column(String(100), nullable=False)   # e.g. "status_changed"
    description = Column(Text, nullable=False)          # human-readable sentence
    old_value   = Column(String(255), nullable=True)    # before the change
    new_value   = Column(String(255), nullable=True)    # after the change

    invoice = relationship("Invoice", back_populates="activity")


class TaxRate(Base):
    """
    Reusable tax presets — pick one when creating items instead of typing
    the percentage each time.
    """
    __tablename__ = "tax_rates"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)   # e.g. "GST 18%"
    rate        = Column(Float, nullable=False)          # 18.0
    description = Column(String(255), default="")
    is_default  = Column(Boolean, default=False)
    is_active   = Column(Boolean, default=True)


class BusinessProfile(Base):
    """
    The sender's details that appear in the invoice header/PDF.
    v1 supports a single profile (id=1). Multi-tenant later.
    """
    __tablename__ = "business_profile"

    id              = Column(Integer, primary_key=True, index=True)
    business_name   = Column(String(255), nullable=False, default="My Business")
    email           = Column(String(255), default="")
    phone           = Column(String(50),  default="")
    address         = Column(Text, default="")
    tax_id          = Column(String(100), default="")
    logo_url        = Column(String(500), default="")
    website         = Column(String(255), default="")
    default_currency= Column(String(3),   default="USD")
    default_tax_percent = Column(Float,   default=0.0)
    default_payment_terms = Column(Integer, default=30)   # days
    invoice_footer  = Column(Text, default="Thank you for your business!")
    bank_details    = Column(Text, default="")  # shown on invoice for transfers