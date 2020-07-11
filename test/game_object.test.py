import unittest

from mutiny.game_object import GameObject
from mutiny.game_enum import CommandEnum, ActionEnum, RoleEnum

from mutiny.states.exchange import Exchange
from mutiny.states.player_turn import PlayerTurn
from mutiny.states.reveal import Reveal
from mutiny.states.wait_for_action_response import WaitForActionResponse
from mutiny.states.wait_for_block import WaitForBlock
from mutiny.states.wait_for_block_response import WaitForBlockResponse

class BaseGameObjectTest:
    class GameObjectTest(unittest.TestCase):
        def setUp(self):
            players = ["A", "B", "C", "D", "E", "F"]
            self.game = GameObject(players)
            self.game.reset()

        def test_checkDefaultState(self):
            self.assertEqual(self.game._state_interface.__class__, PlayerTurn)

class PlayActionTest(BaseGameObjectTest.GameObjectTest):
    def test_income(self):
        player_turn = self.game.game_data.player_turn
        self.game.command(player_turn, {
            "command": CommandEnum.ACTION,
            "action": ActionEnum.INCOME,            
            "stateId": self.game.game_data.state_id,
        })
        self.assertEqual(self.game._state_interface.__class__, PlayerTurn)
        self.assertEqual(self.game.game_data.players[player_turn].cash, 3) # player got their money
        self.assertEqual(self.game.game_data.player_turn, (player_turn + 1) % 6) # it is the next player's turn
    
    def test_foreign_aid(self):
        pass
    
    def test_tax(self):
        pass
    
    def test_more_actions(self):
        pass

class ActionResponseTest(BaseGameObjectTest.GameObjectTest):
    pass

class ExchangeTest(BaseGameObjectTest.GameObjectTest):
    pass


if __name__ == "__main__":
    unittest.main()
