"""Results module for StreetRace Manager.

Records race outcomes, updates rankings, and handles prize money.
"""

from typing import Dict, List

import crew_availability
import inventory


_rankings: Dict[int, int] = {}
_results: List[Dict[str, object]] = []


def record_result(
    race_id: str,
    member_id: int,
    car_id: str,
    outcome: str,
    prize_money: int,
    car_damage: str,
) -> None:
    """Record a race result and update related systems."""
    _results.append(
        {
            "race_id": race_id,
            "member_id": member_id,
            "car_id": car_id,
            "outcome": outcome,
            "prize_money": prize_money,
            "car_damage": car_damage,
        }
    )
    update_rankings(member_id, outcome)
    inventory.update_cash(prize_money)
    inventory.update_car_condition(car_id, car_damage)
    crew_availability.set_available(member_id, True)


def update_rankings(member_id: int, outcome: str) -> None:
    """Update rankings based on outcome (win adds +3, loss +0)."""
    points = 3 if outcome == "win" else 0
    _rankings[member_id] = _rankings.get(member_id, 0) + points


def list_rankings() -> Dict[int, int]:
    """Return the rankings table."""
    return dict(_rankings)


def list_results() -> List[Dict[str, object]]:
    """Return all recorded results."""
    return list(_results)


def reset_results() -> None:
    """Clear all results and rankings (useful for tests)."""
    _rankings.clear()
    _results.clear()
