"""Race Management module for StreetRace Manager.

Creates races and assigns drivers and cars.
"""

from typing import Dict, Optional

import crew_availability
import crew_management
import inventory


_races: Dict[str, Dict[str, Optional[str]]] = {}


def create_race(race_id: str, required_role: str = "driver") -> None:
    """Create a race entry."""
    _races[race_id] = {
        "race_id": race_id,
        "required_role": required_role,
        "driver_id": None,
        "car_id": None,
    }


def select_driver(race_id: str, member_id: int) -> bool:
    """Assign a driver to a race if the member has the required role."""
    race = _races.get(race_id)
    if race is None:
        return False
    if crew_management.get_role(member_id) != race["required_role"]:
        return False
    if not crew_availability.is_available(member_id):
        return False
    race["driver_id"] = member_id
    return True


def assign_car(race_id: str, car_id: str) -> bool:
    """Assign a car to a race if the car exists in inventory."""
    race = _races.get(race_id)
    if race is None:
        return False
    car = inventory.get_car(car_id)
    if car is None:
        return False
    if car.get("condition") == "damaged":
        return False
    race["car_id"] = car_id
    return True


def start_race(race_id: str, outcome: str, prize_money: int, car_damage: str) -> bool:
    """Start a race and record the result in the Results module."""
    race = _races.get(race_id)
    if race is None:
        return False
    if race["driver_id"] is None or race["car_id"] is None:
        return False
    import results

    results.record_result(
        race_id=race_id,
        member_id=race["driver_id"],
        car_id=race["car_id"],
        outcome=outcome,
        prize_money=prize_money,
        car_damage=car_damage,
    )
    return True


def reset_races() -> None:
    """Clear all races (useful for tests)."""
    _races.clear()
