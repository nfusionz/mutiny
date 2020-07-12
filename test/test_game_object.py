import unittest

from mutiny.game_object import GameObject
from mutiny.game_enum import CommandEnum, ActionEnum, RoleEnum

from mutiny.states.exchange import Exchange
from mutiny.states.player_turn import PlayerTurn
from mutiny.states.reveal import Reveal
from mutiny.states.wait_for_action_response import WaitForActionResponse
from mutiny.states.wait_for_block import WaitForBlock
from mutiny.states.wait_for_block_response import WaitForBlockResponse

from benedict.agents.RandomAgent import random_action
from benedict.GameState import GameState

class BaseGameObjectTest(unittest.TestCase):

    def setUp(self):
        players = ["A", "B", "C", "D", "E", "F"]
        self.game = GameObject(players)
        self.game.reset()

class GameObjectTest(BaseGameObjectTest):
    # def setUp(self):
    #     players = ["A", "B", "C", "D", "E", "F"]
    #     self.game = GameObject(players)
    #     self.game.reset()

    def test_checkDefaultState(self):
        self.assertEqual(self.game._state_interface.__class__, PlayerTurn)

class PlayActionTest(BaseGameObjectTest):
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

    def test_foreign_aid_allow(self):
        player_turn = self.game.game_data.player_turn
        self.game.command(player_turn, {
            "command": CommandEnum.ACTION,
            "action": ActionEnum.F_AID,
            "stateId": self.game.game_data.state_id,
        })
        other_players = list(range(len(self.game.players)))
        other_players.remove(player_turn)
        for i in other_players:
            self.game.command(i,{
                "command" : CommandEnum.ALLOW,
                "stateId" : self.game.game_data.state_id
                })
        self.assertEqual(self.game._state_interface.__class__, PlayerTurn)
        self.assertEqual(self.game.game_data.players[player_turn].cash, 4) # player got their money
        self.assertEqual(self.game.game_data.player_turn, (player_turn + 1) % 6) # it is the next player's turn
        pass

    def test_foreign_aid_block_allow(self):
        player_turn = self.game.game_data.player_turn
        self.game.command(player_turn, {
            "command": CommandEnum.ACTION,
            "action": ActionEnum.F_AID,
            "stateId": self.game.game_data.state_id,
        })
        other_players = list(range(len(self.game.players)))
        other_players.remove(player_turn)
        old_state_id = self.game.game_data.state_id
        self.game.command(other_players[0], {
            "command" : CommandEnum.BLOCK,
            "blockingRole": RoleEnum.DUKE,
            "stateId": self.game.game_data.state_id
            })
        for i in list(range(len(self.game.players))):
            if i == other_players[0]:
                continue
            self.game.command(i, {
                "command": CommandEnum.ALLOW,
                "stateId": self.game.game_data.state_id
                })
        self.assertEqual(self.game._state_interface.__class__, PlayerTurn)
        self.assertEqual(self.game.game_data.players[player_turn].cash, 2) # player got their money
        self.assertEqual(self.game.game_data.player_turn, (player_turn + 1) % 6) # it is the next player's turn
        pass

    def test_tax(self):
        player_turn = self.game.game_data.player_turn
        self.game.command(player_turn, {
            "command": CommandEnum.ACTION,
            "action": ActionEnum.TAX,
            "stateId": self.game.game_data.state_id,
        })
        other_players = list(range(len(self.game.players)))
        other_players.remove(player_turn)
        for i in other_players:
            self.game.command(i,{
                "command" : CommandEnum.ALLOW,
                "stateId" : self.game.game_data.state_id
                })
        self.assertEqual(self.game._state_interface.__class__, PlayerTurn)
        self.assertEqual(self.game.game_data.players[player_turn].cash, 5) # player got their money
        self.assertEqual(self.game.game_data.player_turn, (player_turn + 1) % 6) # it is the next player's turn
        pass
        pass

    def test_more_actions(self):
        pass

class PlayRandomGameTest(BaseGameObjectTest):

    def test_run_through_game(self):
        """A modified version of step() from Benedict"""
        return
        self.dones = {p for p in range(len(self.game.players))}
        while self.dones:
            print(self.game.to_dict(None), '\n')
            states = []
            for p in range(len(self.game.players)):
                states.append(GameState.from_dict(self.game.to_dict(p)))

            for p in range(len(self.game.players)):
                if self.game.player_is_done(p):
                    if p in self.dones:
                        self.dones.remove(p)
                else:
                    turn = random_action(states[p])
                    print(p, turn, '\n')
                    self.game.command(p, turn)
            print(self.dones)
            print('\n\n')

# class ActionResponseTest(BaseGameObjectTest):
#     pass
#
# class ExchangeTest(BaseGameObjectTest):
#     pass


if __name__ == "__main__":
    unittest.main()
