# 🧾 Invoice Management System

A full-stack invoice management application designed to model real-world billing workflows, built with FastAPI and SvelteKit.

---

## Core Features

### Dashboard

* Aggregated financial metrics (revenue, outstanding, overdue)
* Invoice status breakdown
* Recent activity snapshot

### Client Management

* Create, update, and soft-delete clients
* Per-client financial summaries (invoiced, paid, outstanding)

### Invoice System

* Multi-line item invoices
* Automatic calculation of subtotal, tax, discount, and total
* Unique invoice numbering
* Status lifecycle management:

  * `draft → sent → viewed → partial → paid`
  * with support for `overdue` and `cancelled`

### Payments

* Record partial and full payments
* Automatic balance updates
* Auto-transition to `paid` when fully settled

### Audit Trail

* Append-only activity log for invoice changes
* Preserves historical state and actions

---
