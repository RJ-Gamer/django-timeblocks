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
