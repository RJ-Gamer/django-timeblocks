# timeblocks

A reusable Django library for creating and managing time blocks using
safe, deterministic recurrence rules.

Designed for scheduling systems where **correctness, idempotency, and
data safety** matter.

---

## Why timeblocks?

Most scheduling implementations break when:

- recurrence rules change
- slots are regenerated
- bookings must be preserved
- timezones drift
- duplicate slots appear

**timeblocks** solves these problems by enforcing strict invariants:

- slots are generated from immutable templates
- destructive operations are explicit and scoped
- locked (booked) slots are never modified
- regeneration is safe and idempotent
- all datetime values are normalized to UTC

---

## Core Concepts

### SlotSeries (template)

A `SlotSeries` defines *how* slots should exist:

- start date
- time window
- recurrence rule
- termination condition

It does **not** generate slots by itself.

### Slot (instance)

A `Slot` is a concrete time interval generated from a series.

Slots may be:

- open
- locked (e.g. booked)
- soft-deleted (historical)

---

## Supported Recurrence Types

- `NONE` — single occurrence
- `DAILY` — every N days
- `WEEKLY` — specific weekdays (e.g. Mon/Wed/Fri)
- `WEEKDAY_MON_FRI` — Monday to Friday

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
* operation is atomic

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

## Safety Guarantees

`timeblocks` enforces the following invariants:

* no duplicate slots per series
* locked slots are immutable
* destructive operations are explicit
* all writes are transactional
* no database-specific constraints are required

---

## Common Gotchas & Best Practices

### ❗ Django Context Required
`timeblocks` is a Django app. Models and services must be used
inside a configured Django environment (e.g. `manage.py shell`).

### ❗ Soft Deletes
Slots are soft-deleted. Always query with:

```python
Slot.objects.filter(is_deleted=False)
```

---
## What timeblocks Does NOT Do

* booking logic
* permissions
* notifications
* UI or API views

These belong in your application layer.

---

## Public API Stability

The following interfaces are considered stable starting from v1.0:

- Slot, SlotSeries models
- SeriesService public methods
- Published enums and query helpers

Internal modules and helpers are not part of the public API
and may change without notice.

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
