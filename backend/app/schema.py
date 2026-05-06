#   *Create  schema  = what the caller sends in the request body
#   *Update  schema  = same but every field optional (PATCH semantics)
#   *Out     schema  = what we send back in the response
#

from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional
from datetime import datetime, date
from .models import InvoiceStatus, PaymentMethod


# Shared helpers 

class OrmBase(BaseModel):
    """All 'Out' schemas inherit this so from_attributes is always on."""
    model_config = {"from_attributes": True}


#  Business Profile 

class BusinessProfileUpdate(BaseModel):
    business_name:          Optional[str]   = None
    email:                  Optional[str]   = None
    phone:                  Optional[str]   = None
    address:                Optional[str]   = None
    tax_id:                 Optional[str]   = None
    logo_url:               Optional[str]   = None
    website:                Optional[str]   = None
    default_currency:       Optional[str]   = None
    default_tax_percent:    Optional[float] = None
    default_payment_terms:  Optional[int]   = None
    invoice_footer:         Optional[str]   = None
    bank_details:           Optional[str]   = None

class BusinessProfileOut(OrmBase):
    id: int
    business_name: str
    email: str
    phone: str
    address: str
    tax_id: str
    logo_url: str
    website: str
    default_currency: str
    default_tax_percent: float
    default_payment_terms: int
    invoice_footer: str
    bank_details: str


# Tax Rates 

class TaxRateCreate(BaseModel):
    name:        str
    rate:        float
    description: Optional[str]  = ""
    is_default:  Optional[bool] = False

    @field_validator("rate")
    @classmethod
    def rate_must_be_positive(cls, v):
        if v < 0 or v > 100:
            raise ValueError("Tax rate must be between 0 and 100")
        return v

class TaxRateOut(OrmBase):
    id:          int
    name:        str
    rate:        float
    description: str
    is_default:  bool
    is_active:   bool


# Clients
class ClientCreate(BaseModel):
    name:             str
    email:            EmailStr
    phone:            Optional[str] = ""
    company:          Optional[str] = ""
    billing_address:  Optional[str] = ""
    shipping_address: Optional[str] = ""
    tax_id:           Optional[str] = ""
    currency:         Optional[str] = "USD"
    notes:            Optional[str] = ""

class ClientUpdate(BaseModel):
    # Every field is Optional - caller can patch just the fields they want
    name:             Optional[str] = None
    email:            Optional[EmailStr] = None
    phone:            Optional[str] = None
    company:          Optional[str] = None
    billing_address:  Optional[str] = None
    shipping_address: Optional[str] = None
    tax_id:           Optional[str] = None
    currency:         Optional[str] = None
    notes:            Optional[str] = None
    is_active:        Optional[bool] = None

class ClientOut(OrmBase):
    id:               int
    name:             str
    email:            str
    phone:            str
    company:          str
    billing_address:  str
    shipping_address: str
    tax_id:           str
    currency:         str
    notes:            str
    is_active:        bool
    created_at:       datetime
    updated_at:       datetime
    # Aggregates - computed and attached in the route, not from ORM
    total_invoiced:   Optional[float] = 0.0
    total_paid:       Optional[float] = 0.0
    outstanding:      Optional[float] = 0.0
    invoice_count:    Optional[int]   = 0


# Invoice Items 

class InvoiceItemCreate(BaseModel):
    description:      str
    detail:           Optional[str]   = ""
    quantity:         float
    unit:             Optional[str]   = ""
    unit_price:       float
    discount_percent: Optional[float] = 0.0
    tax_percent:      Optional[float] = None  # None = inherit invoice-level tax
    sort_order:       Optional[int]   = 0

    @field_validator("quantity", "unit_price")
    @classmethod
    def must_be_positive(cls, v):
        if v < 0:
            raise ValueError("Must be ≥ 0")
        return v

class InvoiceItemOut(OrmBase):
    id:               int
    sort_order:       int
    description:      str
    detail:           str
    quantity:         float
    unit:             str
    unit_price:       float
    discount_percent: float
    tax_percent:      float
    line_total:       float


#Payments 

class PaymentCreate(BaseModel):
    amount:       float
    method:       Optional[PaymentMethod] = PaymentMethod.BANK_TRANSFER
    reference:    Optional[str]  = ""
    payment_date: str             # "YYYY-MM-DD"
    notes:        Optional[str]  = ""

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Payment amount must be greater than 0")
        return v

    @field_validator("payment_date")
    @classmethod
    def valid_date(cls, v):
        # Will raise ValueError if format is wrong — Pydantic surfaces this
        # as a 422 response to the caller automatically
        date.fromisoformat(v)
        return v

class PaymentOut(OrmBase):
    id:           int
    invoice_id:   int
    amount:       float
    method:       PaymentMethod
    reference:    str
    payment_date: str
    notes:        str
    created_at:   datetime


# Activity Log 

class ActivityLogOut(OrmBase):
    id:          int
    event:       str
    description: str
    old_value:   Optional[str]
    new_value:   Optional[str]
    created_at:  datetime


# Invoices 

class InvoiceCreate(BaseModel):
    client_id:        int
    issue_date:       str
    due_date:         str
    currency:         Optional[str]   = "USD"
    tax_label:        Optional[str]   = "Tax"
    tax_percent:      Optional[float] = 0.0
    discount_percent: Optional[float] = 0.0
    notes:            Optional[str]   = ""
    internal_notes:   Optional[str]   = ""
    terms:            Optional[str]   = ""
    footer:           Optional[str]   = ""
    po_number:        Optional[str]   = ""
    items:            list[InvoiceItemCreate]

    @field_validator("items")
    @classmethod
    def must_have_at_least_one_item(cls, v):
        if not v:
            raise ValueError("Invoice must have at least one line item")
        return v

    @model_validator(mode="after")
    def due_date_after_issue(self):
        # Ensures business logic: you can't have a due date in the past
        # relative to the issue date
        if self.issue_date and self.due_date:
            if self.due_date < self.issue_date:
                raise ValueError("due_date must be on or after issue_date")
        return self

class InvoiceUpdate(BaseModel):
    # All optional — used for editing a draft invoice
    client_id:        Optional[int]   = None
    issue_date:       Optional[str]   = None
    due_date:         Optional[str]   = None
    currency:         Optional[str]   = None
    tax_label:        Optional[str]   = None
    tax_percent:      Optional[float] = None
    discount_percent: Optional[float] = None
    notes:            Optional[str]   = None
    internal_notes:   Optional[str]   = None
    terms:            Optional[str]   = None
    footer:           Optional[str]   = None
    po_number:        Optional[str]   = None
    items:            Optional[list[InvoiceItemCreate]] = None

class StatusUpdate(BaseModel):
    status: InvoiceStatus

class InvoiceOut(OrmBase):
    id:               int
    number:           str
    client_id:        int
    client:           ClientOut
    status:           InvoiceStatus
    issue_date:       str
    due_date:         str
    paid_date:        Optional[str]
    currency:         str
    tax_label:        str
    tax_percent:      float
    discount_percent: float
    subtotal:         float
    discount_amount:  float
    tax_amount:       float
    total:            float
    amount_paid:      float
    balance_due:      float
    notes:            str
    internal_notes:   str
    terms:            str
    footer:           str
    po_number:        str
    items:            list[InvoiceItemOut]
    payments:         list[PaymentOut]
    activity:         list[ActivityLogOut]
    created_at:       datetime
    updated_at:       datetime

class InvoiceListOut(OrmBase):
    """Lighter version for list endpoints — omits items, payments, activity."""
    id:          int
    number:      str
    client_id:   int
    client:      ClientOut
    status:      InvoiceStatus
    issue_date:  str
    due_date:    str
    currency:    str
    total:       float
    amount_paid: float
    balance_due: float
    created_at:  datetime


# Dashboard 

class DashboardStats(BaseModel):
    total_clients:      int
    total_invoices:     int
    total_revenue:      float    # sum of all paid invoices
    outstanding_amount: float    # sum of sent/viewed/partial
    overdue_amount:     float
    draft_count:        int
    sent_count:         int
    paid_count:         int
    overdue_count:      float
    # Recent activity
    recent_invoices:    list[InvoiceListOut]