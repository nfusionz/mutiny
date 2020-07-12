import unittest

from mutiny.states.player_turn import *
from mutiny.states.wait_for_action_response import *
from mutiny.states.wait_for_block import *
from mutiny.states.wait_for_block_response import *
from mutiny.states.reveal import *
from mutiny.player import Player
from mutiny.game_data import GameData
from mutiny.game_enum import *
from mutiny.exceptions import InvalidMove


class PlayerTurnTest(unittest.TestCase):
    def setUp(self):
        players = [Player(i, name) for i, name in enumerate(["A", "B", "C", "D", "E", "F"])]
        self.game_data = GameData(players)
        self.game_data.reset()
        self.game_data.player_turn = 0
        self.state = PlayerTurn(data = self.game_data)

    # BASIC ACTIONS
    def test_income(self):
        next_state = self.state.income(0)
        self.assertTrue(isinstance(next_state, PlayerTurn))
        self.assertTrue(self.game_data.players[0].cash, 3)

    def test_foreign_aid(self):
        next_state = self.state.f_aid(0)
        self.assertTrue(isinstance(next_state, WaitForActionResponse))
        self.assertEqual(next_state._action.action_name, ActionEnum.F_AID)
        
    def test_tax(self):
        next_state = self.state.tax(0)
        self.assertTrue(isinstance(next_state, WaitForActionResponse))
        self.assertEqual(next_state._action.action_name, ActionEnum.TAX)

    def test_assassinate(self):
        self.game_data.active_player.addCash(1) # 3 cash now
        next_state = self.state.assassinate(0, 1)
        self.assertTrue(isinstance(next_state, WaitForActionResponse))
        self.assertEqual(next_state._action.action_name, ActionEnum.ASSASSINATE)
        self.assertEqual(self.game_data.active_player.cash, 0)

    def test_steal(self):
        next_state = self.state.steal(0, 1)
        self.assertTrue(isinstance(next_state, WaitForActionResponse))
        self.assertEqual(next_state._action.action_name, ActionEnum.STEAL)

    def test_exchange(self):
        next_state = self.state.exchange(0)
        self.assertTrue(isinstance(next_state, WaitForActionResponse))
        self.assertEqual(next_state._action.action_name, ActionEnum.EXCHANGE)

    def test_coup(self):
        self.game_data.active_player.addCash(5) # 7 cash now
        next_state = self.state.coup(0, 1)
        self.assertEqual(self.game_data.players[0].cash, 0)
        self.assertTrue(isinstance(next_state, Reveal))
        self.assertEqual(next_state._action.action_name, ActionEnum.COUP)
        self.assertEqual(next_state._reveal_id, 1)

    # EDGE CASES
    def test_wrong_playerturn(self):
        self.assertRaises(InvalidMove, self.state.income, 1)

    def test_next_turn_looparound(self):
        self.game_data.player_turn = 5
        next_state = self.state.income(5)
        self.assertEqual(self.game_data.player_turn, 0)

    def test_assassinate_low_cash(self):
        self.assertRaises(InvalidMove, self.state.assassinate, 0, 1)

    def test_coup_low_cash(self):
        self.game_data.active_player.addCash(4) # 6 cash now
        self.assertRaises(InvalidMove, self.state.coup, 0, 1)

    def test_must_coup(self):
        self.game_data.active_player.addCash(8) # 10 cash now
        self.assertRaises(InvalidMove, self.state.income, 0)

    def test_invalid_action(self):
        self.assertRaises(InvalidMove, self.state.allow, 0)


if __name__ == '__main__':
    unittest.main()
