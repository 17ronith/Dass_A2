"""Inventory module for StreetRace Manager.

Tracks cars, parts, tools, and cash balance.
"""

from typing import Dict, List, Optional


_cars: Dict[str, Dict[str, str]] = {}
_parts: Dict[str, int] = {}
_tools: Dict[str, int] = {}
_cash = 0


def add_car(car_id: str, condition: str = "ok") -> None:
    """Add a car to the inventory."""
    _cars[car_id] = {"car_id": car_id, "condition": condition}


def get_car(car_id: str) -> Optional[Dict[str, str]]:
    """Return car info by id, or None if not found."""
    return _cars.get(car_id)


def list_cars() -> List[Dict[str, str]]:
    """Return all cars in inventory."""
    return list(_cars.values())


def update_car_condition(car_id: str, condition: str) -> bool:
    """Update the condition of a car. Returns True on success."""
    if car_id not in _cars:
        return False
    _cars[car_id]["condition"] = condition
    return True


def add_parts(part: str, qty: int) -> None:
    """Add spare parts."""
    _parts[part] = _parts.get(part, 0) + qty


def use_parts(part: str, qty: int) -> bool:
    """Consume spare parts. Returns True if enough stock."""
    current = _parts.get(part, 0)
    if current < qty:
        return False
    _parts[part] = current - qty
    return True


def add_tools(tool: str, qty: int) -> None:
    """Add tools."""
    _tools[tool] = _tools.get(tool, 0) + qty


def use_tools(tool: str, qty: int) -> bool:
    """Consume tools. Returns True if enough stock."""
    current = _tools.get(tool, 0)
    if current < qty:
        return False
    _tools[tool] = current - qty
    return True


def get_cash() -> int:
    """Return current cash balance."""
    return _cash


def update_cash(amount: int) -> int:
    """Update cash balance by amount and return new balance."""
    global _cash
    _cash += amount
    return _cash


def reset_inventory() -> None:
    """Clear inventory state (useful for tests)."""
    global _cars, _parts, _tools, _cash
    _cars = {}
    _parts = {}
    _tools = {}
    _cash = 0
