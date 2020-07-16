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


class TestExchange(unittest.TestCase):

    def test_no_new_cards(self):
        players = ["A", "B", "C", "D", "E", "F"]
        self.game = GameObject(players)
        self.game.reset()

        player_turn = self.game.game_data.player_turn
        self.game.command(player_turn, self.game.game_data.state_id, {
            "command": CommandEnum.ACTION,
            "action": ActionEnum.EXCHANGE,
            "stateId": self.game.game_data.state_id,
        })
        other_players = list(range(len(self.game.players)))
        other_players.remove(player_turn)
        for i in other_players:
            self.game.command(i, self.game.game_data.state_id, {
                "command" : CommandEnum.ALLOW,
                "stateId" : self.game.game_data.state_id
                })

        self.assertEqual(self.game._state_interface.__class__, Exchange)
        self.game.command(player_turn, self.game.game_data.state_id, {
                "command" : CommandEnum.EXCHANGE,
                "roles":  [i.role for i in self.game.game_data.players[player_turn].hand],
                "stateId" : self.game.game_data.state_id
                })

        self.assertEqual(self.game._state_interface.__class__, PlayerTurn)
        self.assertEqual(self.game.game_data.players[player_turn].influence_count, 2) # player got their money
        self.assertEqual(self.game.game_data.player_turn, (player_turn + 1) % 6) # it is the next player's turn

    def test_new_cards(self):
        players = ["A", "B", "C", "D", "E", "F"]
        self.game = GameObject(players)
        self.game.reset()

        player_turn = self.game.game_data.player_turn
        self.game.command(player_turn, self.game.game_data.state_id, {
            "command": CommandEnum.ACTION,
            "action": ActionEnum.EXCHANGE,
            "stateId": self.game.game_data.state_id,
        })
        other_players = list(range(len(self.game.players)))
        other_players.remove(player_turn)
        for i in other_players:
            self.game.command(i, self.game.game_data.state_id, {
                "command" : CommandEnum.ALLOW,
                "stateId" : self.game.game_data.state_id
                })

        self.assertEqual(self.game._state_interface.__class__, Exchange)
        self.game.command(player_turn, self.game.game_data.state_id, {
                "command" : CommandEnum.EXCHANGE,
                "roles":  [i.value for i in self.game._state_interface.exchange_options],
                "stateId" : self.game.game_data.state_id
                })

        self.assertEqual(self.game._state_interface.__class__, PlayerTurn)
        self.assertEqual(self.game.game_data.players[player_turn].influence_count, 2) # player got their money
        self.assertEqual(self.game.game_data.player_turn, (player_turn + 1) % 6) # it is the next player's turn

    def test_new_cards_with_one_inf(self):
        players = ["A", "B", "C", "D", "E", "F"]
        self.game = GameObject(players)
        self.game.reset()

        player_turn = self.game.game_data.player_turn
        self.game.game_data.players[player_turn].hand[0].revealed = True
        self.game.command(player_turn, self.game.game_data.state_id, {
            "command": CommandEnum.ACTION,
            "action": ActionEnum.EXCHANGE,
            "stateId": self.game.game_data.state_id,
        })
        other_players = list(range(len(self.game.players)))
        other_players.remove(player_turn)
        for i in other_players:
            self.game.command(i, self.game.game_data.state_id, {
                "command" : CommandEnum.ALLOW,
                "stateId" : self.game.game_data.state_id
                })

        self.assertEqual(self.game._state_interface.__class__, Exchange)
        self.game.command(player_turn, self.game.game_data.state_id, {
                "command" : CommandEnum.EXCHANGE,
                "roles":  self.game._state_interface.exchange_options[0:1],
                "stateId" : self.game.game_data.state_id
                })

        self.assertEqual(self.game._state_interface.__class__, PlayerTurn)
        self.assertEqual(self.game.game_data.players[player_turn].influence_count, 1) # player got their money
        self.assertEqual(self.game.game_data.player_turn, (player_turn + 1) % 6) # it is the next player's turn

if __name__ == '__main__':
    unittest.main()
