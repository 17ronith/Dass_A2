"""Mission Planning module for StreetRace Manager.

Assigns missions and verifies required roles are available.
"""

from typing import Dict, List

import crew_availability
import crew_management
import inventory


_missions: Dict[str, Dict[str, object]] = {}


def create_mission(mission_id: str, required_roles: List[str]) -> None:
    """Create a mission with required roles."""
    _missions[mission_id] = {
        "mission_id": mission_id,
        "required_roles": list(required_roles),
        "assigned_members": [],
        "status": "planned",
    }


def assign_crew(mission_id: str, member_ids: List[int]) -> bool:
    """Assign crew to a mission if roles match requirements."""
    mission = _missions.get(mission_id)
    if mission is None:
        return False

    required_roles = list(mission["required_roles"])
    for member_id in member_ids:
        role = crew_management.get_role(member_id)
        if not crew_availability.is_available(member_id):
            return False
        if role in required_roles:
            required_roles.remove(role)
        else:
            return False

    if required_roles:
        return False

    mission["assigned_members"] = list(member_ids)
    return True


def start_mission(mission_id: str) -> bool:
    """Mark mission as active if it has assigned crew."""
    mission = _missions.get(mission_id)
    if mission is None:
        return False
    if not mission["assigned_members"]:
        return False
    mission["status"] = "active"
    for member_id in mission["assigned_members"]:
        crew_availability.set_available(member_id, False)
    return True


def complete_mission(mission_id: str, reward: int) -> bool:
    """Mark mission as completed and add reward to inventory cash."""
    mission = _missions.get(mission_id)
    if mission is None:
        return False
    if mission["status"] != "active":
        return False
    mission["status"] = "completed"
    for member_id in mission["assigned_members"]:
        crew_availability.set_available(member_id, True)
    inventory.update_cash(reward)
    return True


def reset_missions() -> None:
    """Clear all missions (useful for tests)."""
    _missions.clear()
