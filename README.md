![PyPI](https://img.shields.io/pypi/v/timeblocks)
![Stability](https://img.shields.io/badge/stability-v1.0-success)
![Concurrency](https://img.shields.io/badge/concurrency-safe-success)
![License](https://img.shields.io/pypi/l/timeblocks)


# Timeblocks

A reusable Django library for creating and managing time blocks using
safe, deterministic recurrence rules.

Designed for scheduling systems where **correctness, idempotency, and
data safety** matter.

---


## Stability & API Guarantees (v1.0+)

Starting from version **1.0.0**, `timeblocks` provides the following guarantees:

### Stable Public API
The following interfaces are considered stable and will not change
in backward-incompatible ways without a MAJOR version bump:

- `Slot` and `SlotSeries` models
- `RecurrenceType` and `EndType` enums
- `SeriesService` public methods

### Internal APIs
Internal helpers, generators, and validation utilities are **not**
part of the public API and may change between minor releases.

### Versioning
`timeblocks` follows semantic versioning:

- **MAJOR** — breaking changes
- **MINOR** — new features or recurrence types
- **PATCH** — bug fixes and correctness improvements

---

## Why timeblocks?

Most scheduling implementations break when:

- recurrence rules change
- slots are regenerated
- bookings must be preserved
- timezones drift
- duplicate slots appear
- concurrent actions occur (booking vs updates)

**timeblocks** solves these problems by enforcing strict invariants:

- slots are generated from immutable templates
- destructive operations are explicit and scoped
- locked (booked) slots are never modified
- regeneration is safe and idempotent
- all datetime values are normalized to UTC
- concurrency is handled explicitly, not implicitly

---

## Mental Model (Read This First)

`timeblocks` separates **intent** from **reality**.

- **SlotSeries** represents *intent*  
  > “This resource should be available every Mon/Wed/Fri from 10–11”

- **Slot** represents *reality*  
  > A concrete time interval that exists, may be booked, or may be cancelled

This separation is intentional and fundamental.

**SlotSeries is the source of truth.  
Slots are generated artifacts.**

Slots must never be treated as authoritative configuration.

---

## Core Concepts

### SlotSeries (template)

A `SlotSeries` defines *how* slots should exist:

- start date
- time window
- recurrence rule
- termination condition

It does **not** represent bookings or history.

### Slot (instance)

A `Slot` is a concrete time interval generated from a series.

Slots may be:

- open
- locked (e.g. booked)
- soft-deleted (historical)

Once a slot is locked, it becomes immutable.

---

## Lifecycle Semantics

A typical lifecycle looks like this:

1. A `SlotSeries` is created
2. Concrete `Slot` rows are generated
3. Some slots become locked (e.g. booked)
4. The series may be regenerated or cancelled
5. Historical slots are preserved

Important rules:

- Regeneration **never modifies locked slots**
- Cancellation **never deletes historical data**
- Slots are soft-deleted, never hard-deleted
- Operations are safe to retry (idempotent)

---

## Supported Recurrence Types

- `NONE` — single occurrence
- `DAILY` — every N days
- `WEEKLY` — specific weekdays (e.g. Mon/Wed/Fri)
- `WEEKDAY_MON_FRI` — Every weekday (Monday–Friday, preset)
- `WEEKDAYS` — Custom weekdays (e.g. Mon/Wed/Fri)
- `MONTH_NTH` — Nth weekday of the month (e.g. first Monday, third Friday)
- `MONTH_LAST` — Last weekday of the month (e.g. last Friday)
- `YEARLY` — Nth weekday of a specific month (e.g. first Monday of January)

Additional recurrence types can be added safely without breaking
existing data.

---

## Installation

```bash
pip install timeblocks
```

Add to Django settings:

```python
INSTALLED_APPS = [
    ...
    "django.contrib.contenttypes",
    "timeblocks",
]
```

Run migrations:

```bash
python manage.py migrate
```

---

## Basic Usage

```python
from datetime import date, time
from timeblocks.services.series_service import SeriesService

series = SeriesService.create_series(
    owner=user,
    data={
        "start_date": date(2025, 1, 1),
        "start_time": time(9, 0),
        "end_time": time(10, 0),
        "timezone": "UTC",
        "recurrence_type": "DAILY",
        "interval": 1,
        "end_type": "AFTER_OCCURRENCES",
        "occurrence_count": 5,
    },
)
```

This will create:

* one `SlotSeries`
* five `Slot` rows
* all timestamps normalized to UTC

---

## Regenerating Slots

When a recurrence rule changes, regenerate safely:

```python
from timeblocks.services.series_service import SeriesService

SeriesService.regenerate_series(
    series=series,
    scope="future",  # or "all"
)
```

### Regeneration Rules

* locked slots are never touched
* soft-deleted slots are preserved
* scope controls blast radius
* operation is atomic and idempotent

---

## Cancelling a Series

```python
from timeblocks.services.series_service import SeriesService

SeriesService.cancel_series(series=series)
```

Effects:

* series is deactivated
* future unlocked slots are soft-deleted
* past and locked slots remain intact

---

## Invariants & Guarantees

`timeblocks` enforces the following invariants at all times:

* a slot can never be booked twice
* locked slots are immutable
* regeneration is scoped and deterministic
* cancellation preserves historical data
* destructive operations are explicit
* all writes are transactional
* all datetime values are normalized to UTC

Violation of these invariants is considered a bug.

---

## Concurrency & Safety

`timeblocks` is designed to be safe under concurrent access.

Key principles:

* booking must use row-level locking (`select_for_update`)
* regeneration and cancellation lock affected rows before mutation
* destructive operations never race with bookings

**Do not** implement booking or regeneration logic outside the provided
services unless you fully understand the concurrency implications.

---

## Common Gotchas & Best Practices

### ❗ Django Context Required

`timeblocks` is a Django app. Models and services must be used
inside a configured Django environment (e.g. `manage.py shell`).

### ❗ Soft Deletes

Slots are soft-deleted. Always query active availability with:

```python
Slot.objects.filter(is_deleted=False)
```

### ❗ Do Not Edit Slots Directly

Slots are generated artifacts. Always mutate schedules via
`SlotSeries` and service methods.

Use `WEEKDAY_MON_FRI` for a fixed Monday–Friday schedule.
Use `WEEKDAYS` when you need custom weekday selection.
`MONTH_NTH` supports only week_of_month values 1–4.

Rules like "5th Monday" are intentionally unsupported.

`MONTH_LAST` always refers to the final occurrence of a weekday in a month, not a fixed week number.

`YEARLY` recurrence does not support fixed calendar dates (e.g. Jan 15).
Use `MONTH_NTH` with interval=12 if exact dates are required.

---

## What timeblocks Does NOT Do

* booking logic
* payments
* permissions
* notifications
* UI or API views

These belong in your application layer.

---

## Compatibility

* Django >= 3.2
* Python >= 3.8
* Database-agnostic (PostgreSQL, MySQL, SQLite)

---

## Versioning & Upgrades

`timeblocks` follows semantic versioning.

* PATCH releases fix bugs without changing behavior
* MINOR releases add new recurrence types or capabilities
* MAJOR releases may change behavior or contracts

Breaking changes are always documented in the changelog.
