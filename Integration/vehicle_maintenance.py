"""Vehicle Maintenance module for StreetRace Manager.

Checks and repairs cars using inventory and mechanic availability.
"""

from typing import Optional

import crew_availability
import crew_management
import inventory


def inspect_car(car_id: str) -> Optional[dict]:
    """Return car info or None if not found."""
    return inventory.get_car(car_id)


def repair_car(car_id: str) -> bool:
    """Repair a car if a mechanic is available and supplies exist."""
    car = inventory.get_car(car_id)
    if car is None:
        return False

    mechanic_ids = crew_management.list_by_role("mechanic")
    has_available_mechanic = False
    for member_id in mechanic_ids:
        if crew_availability.is_available(member_id):
            has_available_mechanic = True
            break
    if not has_available_mechanic:
        return False

    if not inventory.use_parts("basic_parts", 1):
        return False
    if not inventory.use_tools("wrench", 1):
        return False

    return inventory.update_car_condition(car_id, "ok")
