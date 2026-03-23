"""Simple integration test script for StreetRace Manager.

Prints scenario, modules involved, expected vs actual results, and notes.
"""

import crew_availability
import crew_management
import inventory
import mission_planning
import race_management
import registration
import results
import vehicle_maintenance


def reset_all() -> None:
    registration.reset_registry()
    crew_management.reset_roles()
    crew_availability.reset_availability()
    inventory.reset_inventory()
    race_management.reset_races()
    results.reset_results()
    mission_planning.reset_missions()


def print_case(title: str, modules: str, expected: str, actual: str, notes: str) -> None:
    print(title)
    print("Modules:", modules)
    print("Expected:", expected)
    print("Actual:", actual)
    print("Notes:", notes)
    print()


def case_register_and_enter_race() -> None:
    reset_all()
    driver = registration.register_member("Asha", "driver")
    crew_management.assign_role(driver["member_id"], "driver")

    inventory.add_car("car_1", "ok")
    race_management.create_race("race_1")

    driver_ok = race_management.select_driver("race_1", driver["member_id"])
    car_ok = race_management.assign_car("race_1", "car_1")

    expected = "Driver accepted and car assigned"
    actual = f"driver_ok={driver_ok}, car_ok={car_ok}"
    print_case(
        "Register driver then enter race",
        "Registration, Crew Management, Inventory, Race Management",
        expected,
        actual,
        "Validates role check and inventory car lookup.",
    )


def case_enter_race_without_driver() -> None:
    reset_all()
    member = registration.register_member("Lee", "mechanic")
    crew_management.assign_role(member["member_id"], "mechanic")

    race_management.create_race("race_1")
    driver_ok = race_management.select_driver("race_1", member["member_id"])

    expected = "Driver rejected because role is not driver"
    actual = f"driver_ok={driver_ok}"
    print_case(
        "Enter race without driver",
        "Registration, Crew Management, Race Management",
        expected,
        actual,
        "Checks role validation for race drivers.",
    )


def case_race_results_update_inventory() -> None:
    reset_all()
    driver = registration.register_member("Mira", "driver")
    crew_management.assign_role(driver["member_id"], "driver")
    inventory.add_car("car_1", "ok")

    race_management.create_race("race_1")
    race_management.select_driver("race_1", driver["member_id"])
    race_management.assign_car("race_1", "car_1")
    race_management.start_race("race_1", "win", 500, "damaged")

    cash = inventory.get_cash()
    car = inventory.get_car("car_1")

    expected = "Cash increases and car condition becomes damaged"
    actual = f"cash={cash}, car_condition={car.get('condition')}"
    print_case(
        "Race results update inventory",
        "Race Management, Results, Inventory",
        expected,
        actual,
        "Ensures results pipeline updates cash and car condition.",
    )


def case_mission_roles_and_availability() -> None:
    reset_all()
    driver = registration.register_member("Asha", "driver")
    mechanic = registration.register_member("Dev", "mechanic")
    crew_management.assign_role(driver["member_id"], "driver")
    crew_management.assign_role(mechanic["member_id"], "mechanic")

    mission_planning.create_mission("mission_1", ["driver", "mechanic"])
    assigned_ok = mission_planning.assign_crew(
        "mission_1", [driver["member_id"], mechanic["member_id"]]
    )
    started_ok = mission_planning.start_mission("mission_1")

    driver_available = crew_availability.is_available(driver["member_id"])
    mechanic_available = crew_availability.is_available(mechanic["member_id"])

    expected = "Mission assigns and start sets crew unavailable"
    actual = (
        f"assigned_ok={assigned_ok}, started_ok={started_ok}, "
        f"driver_available={driver_available}, mechanic_available={mechanic_available}"
    )
    print_case(
        "Mission assignment and start",
        "Mission Planning, Crew Management, Crew Availability",
        expected,
        actual,
        "Checks required roles and availability transitions.",
    )


def case_vehicle_repair_requires_mechanic() -> None:
    reset_all()
    mechanic = registration.register_member("Dev", "mechanic")
    crew_management.assign_role(mechanic["member_id"], "mechanic")

    inventory.add_car("car_1", "damaged")
    inventory.add_parts("basic_parts", 1)
    inventory.add_tools("wrench", 1)

    repaired_ok = vehicle_maintenance.repair_car("car_1")
    car = inventory.get_car("car_1")

    expected = "Repair succeeds and car condition becomes ok"
    actual = f"repaired_ok={repaired_ok}, car_condition={car.get('condition')}"
    print_case(
        "Vehicle repair with mechanic",
        "Vehicle Maintenance, Inventory, Crew Availability, Crew Management",
        expected,
        actual,
        "Confirms mechanic availability and inventory usage.",
    )


def case_unavailable_driver_blocked() -> None:
    reset_all()
    driver = registration.register_member("Zed", "driver")
    crew_management.assign_role(driver["member_id"], "driver")
    crew_availability.set_available(driver["member_id"], False)

    race_management.create_race("race_1")
    driver_ok = race_management.select_driver("race_1", driver["member_id"])

    expected = "Driver rejected because not available"
    actual = f"driver_ok={driver_ok}"
    print_case(
        "Unavailable driver cannot enter race",
        "Crew Availability, Race Management, Crew Management",
        expected,
        actual,
        "Validates availability check before race entry.",
    )


def case_damaged_car_blocked() -> None:
    reset_all()
    driver = registration.register_member("Mira", "driver")
    crew_management.assign_role(driver["member_id"], "driver")

    inventory.add_car("car_1", "damaged")
    race_management.create_race("race_1")

    race_management.select_driver("race_1", driver["member_id"])
    car_ok = race_management.assign_car("race_1", "car_1")

    expected = "Car rejected because condition is damaged"
    actual = f"car_ok={car_ok}"
    print_case(
        "Damaged car cannot be assigned",
        "Inventory, Race Management",
        expected,
        actual,
        "Checks car condition rule before race entry.",
    )


def case_mission_complete_restores_availability() -> None:
    reset_all()
    driver = registration.register_member("Asha", "driver")
    crew_management.assign_role(driver["member_id"], "driver")

    mission_planning.create_mission("mission_1", ["driver"])
    mission_planning.assign_crew("mission_1", [driver["member_id"]])
    mission_planning.start_mission("mission_1")
    mission_planning.complete_mission("mission_1", 150)

    driver_available = crew_availability.is_available(driver["member_id"])
    cash = inventory.get_cash()

    expected = "Driver available again and cash increased"
    actual = f"driver_available={driver_available}, cash={cash}"
    print_case(
        "Mission completion restores availability",
        "Mission Planning, Crew Availability, Inventory",
        expected,
        actual,
        "Verifies end of mission updates availability and reward.",
    )


def main() -> None:
    case_register_and_enter_race()
    case_enter_race_without_driver()
    case_race_results_update_inventory()
    case_mission_roles_and_availability()
    case_vehicle_repair_requires_mechanic()
    case_unavailable_driver_blocked()
    case_damaged_car_blocked()
    case_mission_complete_restores_availability()


if __name__ == "__main__":
    main()
