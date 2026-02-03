# Changelog

All notable changes to **timeblocks** will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and follows Semantic Versioning.

---

## [0.1.0] — 2026-01-05

### Added
- Slot and SlotSeries models
- DAILY recurrence
- WEEKLY recurrence with custom weekdays
- WEEKDAY_MON_FRI preset
- Safe slot regeneration (`future` / `all`)
- SlotSeries cancellation
- Locked slot preservation
- Database-agnostic idempotency
- Full test suite for recurrence and services
- Django 3.2+ support

### Guarantees
- Locked slots are never modified
- Regeneration is transactional and idempotent
- Soft-deleted slots are preserved
- All datetimes are normalized to UTC

---

## [0.1.1] - 2026-01-06

### Fixed
- Fixed missing dependency declaration for `python-dateutil`
- Fixed timezone normalization compatibility with Django 4+

---

## [0.1.2] - 2026-01-08

### Added
- Added safe Django admin for SlotSeries and Slot inspection
- Improved developer ergonomics (no behavior changes)

### Notes
- No behavior or API changes
- Safe upgrade from 0.1.1 to 0.1.2

---
## [0.1.3] — 2026-01-08

### Fixed
- README badge rendering on PyPI and GitHub
- Declared supported Python versions via `requires-python`

### Notes
- Metadata-only release
- No behavior or API changes
---

## [0.2.0] — 2026-02-02

### Hardened
- Eliminated booking vs regeneration race conditions
- Eliminated booking vs cancellation race conditions
- Enforced row-level locking for destructive operations
- Improved slot safety under concurrent access

### Performance
- Added production-grade indexes for availability and regeneration

### Notes
- No API changes
- Stronger correctness guarantees under concurrency
- Recommended upgrade for all users

## [0.2.1] — 2026-02-02

### Fixed
- Implemented `WEEKDAYS` recurrence with explicit weekday selection
- Clarified and enforced semantics between `WEEKDAYS` and `WEEKDAY_MON_FRI`

### Notes
- No breaking changes
- No behavior change for existing valid configurations
