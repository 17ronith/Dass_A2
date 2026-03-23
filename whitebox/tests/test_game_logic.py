"""White-box tests for Money-Poly game logic (pytest, no mocking)."""

import random

import pytest

from moneypoly.bank import Bank
from moneypoly.board import Board
from moneypoly.cards import CardDeck
from moneypoly.config import (
    GO_SALARY,
    JAIL_POSITION,
    GO_TO_JAIL_POSITION,
    FREE_PARKING_POSITION,
    INCOME_TAX_POSITION,
    LUXURY_TAX_POSITION,
    INCOME_TAX_AMOUNT,
    LUXURY_TAX_AMOUNT,
    JAIL_FINE,
)
from moneypoly.dice import Dice
from moneypoly.game import Game
from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup


def _make_game(names=("A", "B")):
    return Game(list(names))


@pytest.mark.parametrize("steps, expected_pos, passes_go", [
    (1, 1, False),
    (2, 2, False),
    (39, 39, False),
    (40, 0, True),
    (41, 1, True),
])
def test_player_move_positions_and_go_salary(steps, expected_pos, passes_go):
    player = Player("A")
    player.position = 0
    start_balance = player.balance
    player.move(steps)
    assert player.position == expected_pos
    if passes_go:
        assert player.balance == start_balance + GO_SALARY
    else:
        assert player.balance == start_balance


def test_player_move_awards_salary_when_wrapping_past_go():
    player = Player("A")
    player.position = 39
    start_balance = player.balance
    player.move(2)
    assert player.position == 1
    assert player.balance == start_balance + GO_SALARY


def test_player_go_to_jail_sets_flags():
    player = Player("A")
    player.go_to_jail()
    assert player.position == JAIL_POSITION
    assert player.in_jail is True
    assert player.jail_turns == 0


@pytest.mark.parametrize("amount", [-1, -50])
def test_player_add_money_rejects_negative(amount):
    player = Player("A")
    with pytest.raises(ValueError):
        player.add_money(amount)


@pytest.mark.parametrize("amount", [-1, -50])
def test_player_deduct_money_rejects_negative(amount):
    player = Player("A")
    with pytest.raises(ValueError):
        player.deduct_money(amount)


@pytest.mark.parametrize("balance, expected", [
    (0, True),
    (-1, True),
    (1, False),
])
def test_player_is_bankrupt(balance, expected):
    player = Player("A")
    player.balance = balance
    assert player.is_bankrupt() is expected


@pytest.mark.parametrize("position, expected", [
    (0, "go"),
    (JAIL_POSITION, "jail"),
    (GO_TO_JAIL_POSITION, "go_to_jail"),
    (FREE_PARKING_POSITION, "free_parking"),
    (INCOME_TAX_POSITION, "income_tax"),
    (LUXURY_TAX_POSITION, "luxury_tax"),
    (2, "community_chest"),
    (17, "community_chest"),
    (33, "community_chest"),
    (7, "chance"),
    (22, "chance"),
    (36, "chance"),
    (5, "railroad"),
    (15, "railroad"),
    (25, "railroad"),
    (35, "railroad"),
])
def test_board_tile_types_for_specials(position, expected):
    board = Board()
    assert board.get_tile_type(position) == expected


@pytest.mark.parametrize("position", [1, 3, 6, 8, 9])
def test_board_property_tile_type(position):
    board = Board()
    assert board.get_tile_type(position) == "property"


@pytest.mark.parametrize("position", [12, 28, 32])
def test_board_blank_tile_type(position):
    board = Board()
    assert board.get_tile_type(position) == "blank"


def test_board_is_purchasable_for_unowned_property():
    board = Board()
    prop = board.get_property_at(1)
    assert prop is not None
    assert board.is_purchasable(prop.position) is True


def test_board_is_purchasable_false_for_mortgaged():
    board = Board()
    prop = board.get_property_at(1)
    prop.is_mortgaged = True
    assert board.is_purchasable(prop.position) is False


def test_board_is_purchasable_false_for_owned():
    board = Board()
    prop = board.get_property_at(1)
    prop.owner = Player("Owner")
    assert board.is_purchasable(prop.position) is False


def test_properties_owned_by():
    board = Board()
    owner = Player("Owner")
    prop = board.get_property_at(1)
    prop.owner = owner
    assert board.properties_owned_by(owner) == [prop]


def test_unowned_properties_counts_all_unowned():
    board = Board()
    assert len(board.unowned_properties()) == len(board.properties)


def test_card_deck_draw_cycles():
    deck = CardDeck([{"description": "A", "action": "collect", "value": 1}])
    first = deck.draw()
    second = deck.draw()
    assert first == second


def test_card_deck_peek_does_not_advance():
    deck = CardDeck([{"description": "A", "action": "collect", "value": 1}])
    first = deck.peek()
    second = deck.peek()
    assert first == second


def test_card_deck_reshuffle_resets_index():
    deck = CardDeck([
        {"description": "A", "action": "collect", "value": 1},
        {"description": "B", "action": "collect", "value": 2},
    ])
    deck.draw()
    deck.reshuffle()
    assert deck.index == 0


def test_card_deck_cards_remaining_empty_returns_zero():
    deck = CardDeck([])
    assert deck.cards_remaining() == 0


def test_bank_collect_and_payout_update_balance():
    bank = Bank()
    start = bank.get_balance()
    bank.collect(50)
    assert bank.get_balance() == start + 50
    bank.pay_out(20)
    assert bank.get_balance() == start + 30


def test_bank_pay_out_insufficient_raises():
    bank = Bank()
    with pytest.raises(ValueError):
        bank.pay_out(bank.get_balance() + 1)


def test_bank_collect_ignores_negative_amounts():
    bank = Bank()
    start = bank.get_balance()
    bank.collect(-100)
    assert bank.get_balance() == start


def test_bank_give_loan_records_loan():
    bank = Bank()
    player = Player("A")
    start = bank.get_balance()
    bank.give_loan(player, 50)
    assert bank.loan_count() == 1
    assert bank.total_loans_issued() == 50
    assert bank.get_balance() == start - 50


def test_property_mortgage_and_unmortgage_flow():
    prop = Property("A", 1, 100, 10)
    payout = prop.mortgage()
    assert payout == 50
    assert prop.is_mortgaged is True
    cost = prop.unmortgage()
    assert cost == int(50 * 1.1)
    assert prop.is_mortgaged is False


def test_property_get_rent_mortgaged_zero():
    prop = Property("A", 1, 100, 10)
    prop.is_mortgaged = True
    assert prop.get_rent() == 0


def test_property_group_all_owned_by_requires_full_set():
    group = PropertyGroup("Blue", "blue")
    prop1 = Property("A", 1, 100, 10, group)
    prop2 = Property("B", 2, 120, 12, group)
    owner = Player("Owner")
    prop1.owner = owner
    assert group.all_owned_by(owner) is False
    prop2.owner = owner
    assert group.all_owned_by(owner) is True


def test_board_railroad_positions_have_properties():
    board = Board()
    assert board.get_property_at(5) is not None
    assert board.get_property_at(15) is not None
    assert board.get_property_at(25) is not None
    assert board.get_property_at(35) is not None


def test_property_group_counts_and_size():
    group = PropertyGroup("Blue", "blue")
    prop1 = Property("A", 1, 100, 10, group)
    prop2 = Property("B", 2, 120, 12, group)
    owner = Player("Owner")
    prop1.owner = owner
    prop2.owner = owner
    counts = group.get_owner_counts()
    assert counts[owner] == 2
    assert group.size() == 2


def test_game_find_winner_highest_net_worth():
    game = _make_game(["A", "B"])
    game.players[0].balance = 100
    game.players[1].balance = 500
    winner = game.find_winner()
    assert winner.name == "B"


def test_game_buy_property_allows_exact_balance():
    game = _make_game(["A"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    player.balance = prop.price
    success = game.buy_property(player, prop)
    assert success is True
    assert prop.owner == player
    assert prop in player.properties


def test_game_pay_rent_transfers_to_owner():
    game = _make_game(["A", "B"])
    payer = game.players[0]
    owner = game.players[1]
    prop = game.board.get_property_at(1)
    prop.owner = owner
    owner.add_property(prop)
    payer.balance = 200
    owner.balance = 100
    rent = prop.get_rent()
    game.pay_rent(payer, prop)
    assert payer.balance == 200 - rent
    assert owner.balance == 100 + rent


def test_game_unmortgage_property_keeps_mortgaged_on_insufficient_funds():
    game = _make_game(["A"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    prop.owner = player
    prop.is_mortgaged = True
    player.balance = 0
    success = game.unmortgage_property(player, prop)
    assert success is False
    assert prop.is_mortgaged is True


def test_game_check_bankruptcy_removes_player_and_properties():
    game = _make_game(["A", "B"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    prop.owner = player
    player.properties.append(prop)
    player.balance = 0
    game._check_bankruptcy(player)
    assert player not in game.players
    assert prop.owner is None
    assert player.properties == []


@pytest.mark.parametrize("action, value", [
    ("collect", 50),
    ("pay", 25),
    ("jail", 0),
    ("jail_free", 0),
    ("birthday", 10),
    ("collect_from_all", 5),
])
def test_game_apply_card_actions(action, value):
    game = _make_game(["A", "B"])
    player = game.players[0]
    other = game.players[1]
    player.balance = 100
    other.balance = 100
    card = {"description": "", "action": action, "value": value}
    game._apply_card(player, card)
    if action == "collect":
        assert player.balance == 100 + value
    elif action == "pay":
        assert player.balance == 100 - value
    elif action == "jail":
        assert player.in_jail is True
    elif action == "jail_free":
        assert player.get_out_of_jail_cards == 1
    elif action == "birthday":
        assert player.balance == 110
        assert other.balance == 90
    elif action == "collect_from_all":
        assert player.balance == 105
        assert other.balance == 95


def test_game_apply_card_move_to_passes_go():
    game = _make_game(["A"])
    player = game.players[0]
    player.position = 39
    card = {"description": "", "action": "move_to", "value": 0}
    game._apply_card(player, card)
    assert player.position == 0
    assert player.balance == 1500 + GO_SALARY


@pytest.mark.parametrize("position, expected_delta, expected_jail", [
    (INCOME_TAX_POSITION, -INCOME_TAX_AMOUNT, False),
    (LUXURY_TAX_POSITION, -LUXURY_TAX_AMOUNT, False),
    (FREE_PARKING_POSITION, 0, False),
    (GO_TO_JAIL_POSITION, 0, True),
])
def test_game_move_and_resolve_special_tiles(position, expected_delta, expected_jail):
    game = _make_game(["A"])
    player = game.players[0]
    player.position = position - 1
    start_balance = player.balance
    game._move_and_resolve(player, 1)
    assert player.balance == start_balance + expected_delta
    assert player.in_jail is expected_jail


def test_game_move_and_resolve_chance_collect():
    game = _make_game(["A"])
    game.chance_deck = CardDeck([
        {"description": "", "action": "collect", "value": 10}
    ])
    player = game.players[0]
    player.position = 6
    start = player.balance
    game._move_and_resolve(player, 1)
    assert player.balance == start + 10


def test_game_move_and_resolve_community_collect():
    game = _make_game(["A"])
    game.community_deck = CardDeck([
        {"description": "", "action": "collect", "value": 15}
    ])
    player = game.players[0]
    player.position = 1
    start = player.balance
    game._move_and_resolve(player, 1)
    assert player.balance == start + 15


def test_dice_roll_range_and_reset():
    dice = Dice()
    random.seed(0)
    for _ in range(20):
        total = dice.roll()
        assert 1 <= dice.die1 <= 6
        assert 1 <= dice.die2 <= 6
        assert 2 <= total <= 12
    dice.reset()
    assert dice.doubles_streak == 0
