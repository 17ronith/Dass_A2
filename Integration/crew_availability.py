"""Crew Availability module for StreetRace Manager.

Tracks whether crew members are available for tasks.
"""

from typing import Dict, List

import crew_management


_availability: Dict[int, bool] = {}


def set_available(member_id: int, is_available: bool) -> None:
    """Set availability status for a member."""
    _availability[member_id] = is_available


def is_available(member_id: int) -> bool:
    """Return availability status for a member (default True)."""
    return _availability.get(member_id, True)


def list_available_by_role(role: str) -> List[int]:
    """Return available member IDs who have the given role."""
    member_ids = crew_management.list_by_role(role)
    return [member_id for member_id in member_ids if is_available(member_id)]


def reset_availability() -> None:
    """Clear availability table (useful for tests)."""
    _availability.clear()
