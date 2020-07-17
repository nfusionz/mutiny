import unittest

from mutiny.player import Influence
from mutiny.game_object import GameObject
from mutiny.game_enum import CommandEnum, ActionEnum, RoleEnum

from mutiny.actions import ForeignAid, Steal
from mutiny.states.exchange import Exchange
from mutiny.states.player_turn import PlayerTurn
from mutiny.states.reveal import Reveal
from mutiny.states.wait_for_action_response import WaitForActionResponse
from mutiny.states.wait_for_block import WaitForBlock
from mutiny.states.wait_for_block_response import WaitForBlockResponse

from benedict.agents.RandomAgent import random_action
from benedict.GameState import GameState


class TestWaitForBlockResponse(unittest.TestCase):
    def test_faid_block_reveal(self):

        # setup
        players = ["A", "B", "C", "D", "E", "F"]
        self.game = GameObject(players)
        self.game.reset()
        player_turn = self.game.game_data.player_turn
        blocker_id  = (player_turn -1) % len(players)
        for p in range(len(players)):
            self.game.game_data.players[p].hand = (Influence(role=RoleEnum.CONTESSA,revealed=False), Influence(role=RoleEnum.CONTESSA,revealed=False))
        # reveal first card
        state_interface = WaitForBlockResponse(data=self.game.game_data,
                                   action=ForeignAid(self.game.game_data),
                                   blocker_id=blocker_id,
                                   block_role=RoleEnum.DUKE)
        reveal = state_interface.challenge(player_turn)
        self.assertEqual(reveal._reveal_id,blocker_id)
        state_interface = reveal.reveal(blocker_id,RoleEnum.CONTESSA)

        self.assertEqual(self.game.game_data.players[blocker_id].hand[0].role, RoleEnum.CONTESSA)
        self.assertEqual(self.game.game_data.players[blocker_id].hand[0].revealed, True)
        # reveal second card

        player_turn = self.game.game_data.player_turn
        state_interface = WaitForBlockResponse(data=self.game.game_data,
                                   action=ForeignAid(self.game.game_data),
                                   blocker_id=blocker_id,
                                   block_role=RoleEnum.DUKE)
        reveal = state_interface.challenge(player_turn)

        self.assertEqual(self.game.game_data.players[blocker_id].hand[1].role, RoleEnum.CONTESSA)
        self.assertEqual(self.game.game_data.players[blocker_id].hand[1].revealed, True)

    def test_captain_block_success(self):

        players = ["A", "B", "C", "D", "E", "F"]
        self.game = GameObject(players)
        self.game.reset()
        self.game.game_data.player_turn = 0
        player_turn = self.game.game_data.player_turn
        target_id  = 3
        for p in range(len(players)):
            self.game.game_data.players[p].hand = (Influence(role=RoleEnum.CAPTAIN,revealed=False), Influence(role=RoleEnum.CAPTAIN,revealed=False))
        # reveal first card
        state_interface = WaitForBlockResponse(data=self.game.game_data,
                                   action=Steal(self.game.game_data,target_id),
                                   blocker_id=target_id,
                                   block_role=RoleEnum.CAPTAIN)
        reveal = state_interface.challenge(player_turn)
        self.assertEqual(reveal._reveal_id,player_turn)
        state_interface = reveal.reveal(player_turn,RoleEnum.CAPTAIN)

        self.assertEqual(self.game.game_data.players[player_turn].hand[0].role, RoleEnum.CAPTAIN)
        self.assertEqual(self.game.game_data.players[player_turn].hand[0].revealed, True)
        # reveal second card
        self.game.game_data.player_turn = 0

        player_turn = self.game.game_data.player_turn
        state_interface = WaitForBlockResponse(data=self.game.game_data,
                                   action=Steal(self.game.game_data, target_id),
                                   blocker_id=target_id,
                                   block_role=RoleEnum.CAPTAIN)
        reveal = state_interface.challenge(player_turn)

        self.assertEqual(self.game.game_data.players[player_turn].hand[1].role, RoleEnum.CAPTAIN)
        self.assertEqual(self.game.game_data.players[player_turn].hand[1].revealed, True)

    def test_faid_block_with_duke(self):

        # setup
        players = ["A", "B", "C", "D", "E", "F"]
        self.game = GameObject(players)
        self.game.reset()
        self.game.game_data.player_turn = 0
        player_turn = self.game.game_data.player_turn
        blocker_id  = 3
        for p in range(len(players)):
            self.game.game_data.players[p].hand = (Influence(role=RoleEnum.DUKE,revealed=False), Influence(role=RoleEnum.DUKE,revealed=False))
        # reveal first card
        state_interface = WaitForBlockResponse(data=self.game.game_data,
                                   action=ForeignAid(self.game.game_data),
                                   blocker_id=blocker_id,
                                   block_role=RoleEnum.DUKE)
        reveal = state_interface.challenge(player_turn)
        self.assertEqual(reveal._reveal_id,player_turn)
        state_interface = reveal.reveal(player_turn,RoleEnum.DUKE)

        self.assertEqual(self.game.game_data.players[player_turn].hand[0].role, RoleEnum.DUKE)
        self.assertEqual(self.game.game_data.players[player_turn].hand[0].revealed, True)
        # reveal second card
        self.game.game_data.player_turn = 0

        player_turn = self.game.game_data.player_turn
        state_interface = WaitForBlockResponse(data=self.game.game_data,
                                   action=ForeignAid(self.game.game_data),
                                   blocker_id=blocker_id,
                                   block_role=RoleEnum.DUKE)
        reveal = state_interface.challenge(player_turn)

        self.assertEqual(self.game.game_data.players[player_turn].hand[1].role, RoleEnum.DUKE)
        self.assertEqual(self.game.game_data.players[player_turn].hand[1].revealed, True)



if __name__ == '__main__':
    unittest.main()
