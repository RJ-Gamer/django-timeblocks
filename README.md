![PyPI](https://img.shields.io/pypi/v/timeblocks)
![Stability](https://img.shields.io/badge/stability-v1.0-success)
![Concurrency](https://img.shields.io/badge/concurrency-safe-success)
![License](https://img.shields.io/pypi/l/timeblocks)

# timeblocks

A reusable Django library for creating and managing time blocks using
**safe, deterministic recurrence rules**.

Designed for scheduling systems where **correctness, idempotency, and
data safety** matter more than flexibility.

---

## Feedback & Community

If you are using `timeblocks` (or evaluating it), I’d love to hear from you.

- ⭐ Star the repo if it saves you time
- 🐛 Open an issue for bugs or edge cases
- 💡 Start a discussion for design questions or suggestions

Even small feedback helps shape the roadmap.

➡️ GitHub Issues & Discussions are always welcome.

---

## Quick Start Example

Create a recurring availability every Monday, Wednesday, and Friday
from 10:00–11:00 UTC for the next 5 occurrences:

```python
from datetime import date, time
from timeblocks.services.series_service import SeriesService
from timeblocks.constants import RecurrenceType, EndType

series = SeriesService.create_series(
    owner=user,
    data={
        "start_date": date(2025, 1, 1),
        "start_time": time(10, 0),
        "end_time": time(11, 0),
        "timezone": "UTC",
        "recurrence_type": RecurrenceType.WEEKDAYS.value,
        "by_weekdays": ["MON", "WED", "FRI"],
        "end_type": EndType.AFTER_OCCURRENCES.value,
        "occurrence_count": 5,
    },
)
```

---

## Examples

Real-world usage examples are available in the [`examples/`](./examples) directory:

- daily and weekly availability
- safe regeneration flows
- cancellation semantics
- monthly and yearly recurrence patterns

The README intentionally shows only the happy path.

---

## Stability & API Guarantees (v1.0+)

Starting from version **1.0.0**, `timeblocks` provides explicit stability guarantees.

### Stable Public API
The following interfaces will not change in backward-incompatible ways
without a MAJOR version bump:

- `Slot` and `SlotSeries` models
- `RecurrenceType` and `EndType` enums
- `SeriesService` public methods

### Internal APIs
Internal helpers, generators, and validation utilities are **not**
part of the public API and may change between minor releases.

### Versioning
`timeblocks` follows semantic versioning:

- **MAJOR** — breaking changes
- **MINOR** — new capabilities
- **PATCH** — bug fixes and correctness improvements

---

## Mental Model (Read This First)

`timeblocks` separates **intent** from **reality**.

- **SlotSeries** represents intent  
  > “This resource should be available every Mon/Wed/Fri from 10–11”

- **Slot** represents reality  
  > A concrete time interval that exists, may be booked, or cancelled

**SlotSeries is the source of truth.  
Slots are generated artifacts.**

Slots must never be treated as configuration.

---

## Supported Recurrence Types

- `NONE` — single occurrence
- `DAILY` — every N days
- `WEEKLY` — specific weekdays
- `WEEKDAY_MON_FRI` — every weekday (preset)
- `WEEKDAYS` — custom weekdays
- `MONTH_NTH` — Nth weekday of the month
- `MONTH_LAST` — last weekday of the month
- `YEARLY` — Nth weekday of a specific month

All declared recurrence types are fully implemented and tested.

---

## What timeblocks Does NOT Do

- booking logic
- payments
- permissions
- notifications
- UI or API views

These belong in your application layer.

---

For questions or design discussions, please use **GitHub Discussions**
instead of Issues.
