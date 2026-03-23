Assignment Question: 

 Integration Testing (40 marks)
You will design, implement, and test a command-line system called StreetRace Manager. This system supports managing underground street races, crew members, vehicles, and mis- sions. You will build the system module-by-module, commit each completed component to Git with meaningful messages, and then integrate and test the combined system.
Each module must be correctly designed and implemented on its own before integration, and all interactions between modules should function as expected in the final system.
Your system must include the following modules: • Registration module
• Crew Management module
• Inventory module
• Race Management module • Results module
• Mission Planning module
You are also required to design at least two additional modules of your choice. Clearly describe these extra modules in your report.
Your implementation should satisfy the following behaviors:
• Registration: Registers new crew members, storing name and role.
2
• Crew Management: Manages roles (e.g., driver, mechanic, strategist) and records skill levels for each.
• Inventory: Tracks cars, spare parts, tools, and the cash balance.
• Race Management: Creates races and selects appropriate drivers and cars from the
system.
• Results: Records race outcomes, updates rankings, and handles prize money.
• Mission Planning: Assigns missions (e.g., delivery, rescue) and verifies required roles are available.
Module interactions must follow sensible business rules, for example:
• A crew member must be registered before a role can be assigned.
• Only crew members with the driver role may be entered in a race.
• If a car is damaged during a race, a mission requiring a mechanic must check for availability before proceeding.
• Race results should update the cash balance in the Inventory.
• Missions cannot start if required roles are unavailable.
Ensure modules work together correctly and verify data flow and interaction between com-
ponents rather than only their individual functionality.
2.1 Call Graph
Create a Call Graph showing all function calls within and between modules.
Requirements:
• Draw the graph by hand.
• Each node should represent a single function.
• Arrows must show which function calls another. • Clearly show calls between modules.
• Submit a clear image as part of your report.
2.2 Integration Test Design
Design test cases that validate how different modules interact with one another. Each test case should include:
• What scenario is being tested • Which modules are involved
3

• The expected result
• The actual result after testing
• Any errors or logical issues found
Your test cases should cover integrations illustrated in the Call Graph. Common integration scenarios include (but are not limited to):
• Registering a driver and then entering the driver into a race
• Attempting to enter a race without a registered driver
• Completing a race and verifying results and prize money update the inventory • Assigning a mission and ensuring correct crew roles are validated
Explain in simple language why each test case is needed, and what errors (if any) were detected and fixed. 


This is a practice assignment question. Tell me how to proceed with this in an orderly fashion.

Module: Registration
Functions

register_member(name, role)
get_member(member_id)
list_members()
Calls

register_member() → Crew Management assign_role(member_id, role)
Module: Crew Management
Functions

assign_role(member_id, role)
set_skill(member_id, role, level)
get_role(member_id)
is_role_available(role)
list_by_role(role)
Calls

assign_role() → Registration get_member(member_id)
is_role_available() → Crew Availability is_available(member_id)
list_by_role() → Registration list_members()

Module: Inventory
Functions

add_car(car_id, condition)
get_car(car_id)
list_cars()
update_car_condition(car_id, condition)
add_parts(part, qty)
use_parts(part, qty)
add_tools(tool, qty)
use_tools(tool, qty)
get_cash()
update_cash(amount)
Calls

(no cross‑module calls)

Module: Race Management
Functions

create_race(race_id, required_role="driver")
select_driver(race_id, member_id)
assign_car(race_id, car_id)
start_race(race_id)
Calls

select_driver() → Crew Management get_role(member_id)
select_driver() → Crew Availability is_available(member_id)
assign_car() → Inventory get_car(car_id)
start_race() → Results record_result(race_id, outcome, prize_money, car_damage)
Module: Results
Functions

record_result(race_id, outcome, prize_money, car_damage)
update_rankings(member_id, outcome)
list_rankings()
Calls

record_result() → Inventory update_cash(prize_money)
record_result() → Inventory update_car_condition(car_id, condition)
record_result() → Crew Availability set_unavailable(member_id, false)
record_result() → update_rankings(member_id, outcome)

Module: Mission Planning
Functions

create_mission(mission_id, required_roles)
assign_crew(mission_id, member_ids)
start_mission(mission_id)
complete_mission(mission_id, reward)
Calls

assign_crew() → Crew Management get_role(member_id)
assign_crew() → Crew Availability is_available(member_id)
start_mission() → Crew Availability set_unavailable(member_id, true)
complete_mission() → Inventory update_cash(reward)
complete_mission() → Crew Availability set_unavailable(member_id, false)

Additional Module 1: Vehicle Maintenance
Functions

inspect_car(car_id)
repair_car(car_id)
Calls

inspect_car() → Inventory get_car(car_id)
repair_car() → Inventory use_parts(part, qty)
repair_car() → Inventory use_tools(tool, qty)
repair_car() → Inventory update_car_condition(car_id, "ok")
repair_car() → Crew Management list_by_role("mechanic")
repair_car() → Crew Availability is_available(member_id)

Additional Module 2: Crew Availability
Functions

set_available(member_id, is_available)
is_available(member_id)
list_available_by_role(role)
Calls

list_available_by_role() → Crew Management list_by_role(role)




Here’s what each test in your script does:

Register driver then enter race
Validates that a registered member with the driver role can be selected and a valid car can be assigned. It checks Registration → Crew Management → Inventory → Race Management interaction.

Enter race without driver
Attempts to select a non‑driver (mechanic). Verifies that Race Management rejects the member based on Crew Management role data.

Race results update inventory
Runs a race and confirms Results updates Inventory: cash increases and car condition changes. This checks Race Management → Results → Inventory flow.

Mission assignment and start
Creates a mission requiring driver+mechanic, assigns both, starts the mission, and verifies Crew Availability becomes false for those members. This checks Mission Planning → Crew Management → Crew Availability.

Vehicle repair with mechanic
Repairs a damaged car and confirms parts/tools are consumed and condition returns to ok. This checks Vehicle Maintenance → Crew Management → Crew Availability → Inventory.

New test cases:

Unavailable driver cannot enter race
Damaged car cannot be assigned
Mission completion restores availability and cash


