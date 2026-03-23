"""Registration module for StreetRace Manager.

Stores crew members and supports basic lookup.
"""

from typing import Dict, List, Optional


_members: Dict[int, Dict[str, Optional[str]]] = {}
_next_id = 1


def register_member(name: str, role: Optional[str] = None) -> Dict[str, Optional[str]]:
    """Register a new crew member and return the created record."""
    global _next_id
    member = {"member_id": _next_id, "name": name, "role": role}
    _members[_next_id] = member
    _next_id += 1
    return member


def get_member(member_id: int) -> Optional[Dict[str, Optional[str]]]:
    """Return a crew member by id, or None if not found."""
    return _members.get(member_id)


def list_members() -> List[Dict[str, Optional[str]]]:
    """Return all registered crew members."""
    return list(_members.values())


def reset_registry() -> None:
    """Clear all registered members (useful for tests)."""
    global _members, _next_id
    _members = {}
    _next_id = 1
