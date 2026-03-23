"""Crew Management module for StreetRace Manager.
    
Manages roles and skill levels for registered crew members.
"""

from typing import Dict, List, Optional

import registration


_roles: Dict[int, str] = {}
_skills: Dict[int, Dict[str, int]] = {}


def assign_role(member_id: int, role: str) -> bool:
    """Assign a role to a registered member. Returns True on success."""
    if registration.get_member(member_id) is None:
        return False
    _roles[member_id] = role
    return True


def set_skill(member_id: int, role: str, level: int) -> bool:
    """Set skill level for a role. Member must be registered and have the role."""
    if registration.get_member(member_id) is None:
        return False
    if _roles.get(member_id) != role:
        return False
    if member_id not in _skills:
        _skills[member_id] = {}
    _skills[member_id][role] = level
    return True


def get_role(member_id: int) -> Optional[str]:
    """Return the role for a member, or None if not assigned."""
    return _roles.get(member_id)


def is_role_available(role: str) -> bool:
    """Return True if at least one registered member has the role."""
    for member_id in _roles:
        if _roles.get(member_id) == role:
            return True
    return False


def list_by_role(role: str) -> List[int]:
    """Return member IDs who have the given role."""
    return [member_id for member_id, r in _roles.items() if r == role]


def reset_roles() -> None:
    """Clear all roles and skills (useful for tests)."""
    _roles.clear()
    _skills.clear()
