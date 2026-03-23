# White-Box Test Case List (Pytest)

1. Dice roll totals stay within 2-12.
2. Dice die1 stays within 1-6.
3. Dice die2 stays within 1-6.
4. Dice reset clears doubles streak.
5. Player move by 1 updates position to 1.
6. Player move by 2 updates position to 2.
7. Player move by 39 updates position to 39.
8. Player move by 40 lands on Go (position 0).
9. Player move by 41 wraps to position 1.
10. Player landing on Go collects salary.
11. Player move without Go does not collect salary.
12. Player go_to_jail sets position to Jail.
13. Player go_to_jail sets in_jail True.
14. Player go_to_jail resets jail_turns to 0.
15. add_money rejects negative inputs.
16. deduct_money rejects negative inputs.
17. is_bankrupt True at balance 0.
18. is_bankrupt True at negative balance.
19. is_bankrupt False at positive balance.
20. Board tile type for Go is "go".
21. Board tile type for Jail is "jail".
22. Board tile type for Go To Jail is "go_to_jail".
23. Board tile type for Free Parking is "free_parking".
24. Board tile type for Income Tax is "income_tax".
25. Board tile type for Luxury Tax is "luxury_tax".
26. Board tile type for Community Chest at 2.
27. Board tile type for Community Chest at 17.
28. Board tile type for Community Chest at 33.
29. Board tile type for Chance at 7.
30. Board tile type for Chance at 22.
31. Board tile type for Chance at 36.
32. Board tile type for Railroad at 5.
33. Board tile type for Railroad at 15.
34. Board tile type for Railroad at 25.
35. Board tile type for Railroad at 35.
36. Board tile type for property at position 1.
37. Board tile type for property at position 3.
38. Board tile type for property at position 6.
39. Board tile type for blank at position 12.
40. Board tile type for blank at position 28.
41. Board tile type for blank at position 32.
42. is_purchasable True for unowned, unmortgaged property.
43. is_purchasable False for mortgaged property.
44. is_purchasable False for owned property.
45. properties_owned_by returns only owned properties.
46. unowned_properties returns all when none owned.
47. CardDeck draw cycles with single card.
48. CardDeck peek does not advance index.
49. CardDeck reshuffle resets index.
50. Bank collect increases balance.
51. Bank pay_out decreases balance.
52. Bank pay_out raises on insufficient funds.
53. Bank give_loan increments loan count.
54. Bank total_loans_issued sums amounts.
55. Property mortgage returns payout and flags mortgaged.
56. Property unmortgage returns cost and clears flag.
57. Property get_rent returns 0 when mortgaged.
58. PropertyGroup all_owned_by False for partial ownership.
59. PropertyGroup all_owned_by True for full ownership.
60. PropertyGroup get_owner_counts totals correctly.
61. PropertyGroup size reports number of properties.
62. Game find_winner returns highest net worth.
63. Game buy_property succeeds with exact balance.
64. Game pay_rent transfers rent to owner.
65. Game _check_bankruptcy removes player from game.
66. Game _check_bankruptcy clears property ownership.
67. Game _apply_card collect increases player balance.
68. Game _apply_card pay decreases player balance.
69. Game _apply_card jail sets in_jail True.
70. Game _apply_card jail_free increments jail card count.
71. Game _apply_card birthday transfers from others.
72. Game _apply_card collect_from_all transfers from others.
73. Game _apply_card move_to passes Go and pays salary.
74. _move_and_resolve applies income tax.
75. _move_and_resolve applies luxury tax.
76. _move_and_resolve free parking makes no change.
77. _move_and_resolve go_to_jail sends player to jail.
78. _move_and_resolve chance collect card increases balance.
79. _move_and_resolve community chest collect card increases balance.
80. Player collects Go salary when passing Go (wrap).
81. Bank collect ignores negative amounts.
82. Bank give_loan reduces bank funds.
83. CardDeck cards_remaining on empty deck returns 0.
84. Railroad positions are modeled as properties.
85. Unmortgage fails if player cannot pay and keeps property mortgaged.
