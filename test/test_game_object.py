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

    def test_assassin_block(self):
        for i in range(6):
            player_turn = self.game.game_data.player_turn
            self.game.command(player_turn, {
                "command": CommandEnum.ACTION,
                "action": ActionEnum.INCOME,
                "stateId": self.game.game_data.state_id,
            })
        player_turn = self.game.game_data.player_turn
        target = (player_turn + 1) % len(self.game.game_data.players)
        self.game.command(player_turn, {
            "command" : CommandEnum.ACTION,
            "action"  : ActionEnum.ASSASSINATE,
            "target"  : target,
            "stateId" : self.game.game_data.state_id
        })
        self.game.command(target, {
            "command" : CommandEnum.BLOCK,
            "blockingRole": RoleEnum.CONTESSA,
            "target"  : target,
            "stateId" : self.game.game_data.state_id
        })
        for i in range(len(self.game.game_data.players)):
            if i != target:
                self.game.command(i,{
                    "command" : CommandEnum.ALLOW,
                    "stateId" : self.game.game_data.state_id
                })

        self.assertEqual(self.game._state_interface.__class__, PlayerTurn)

        self.assertEqual(self.game.game_data.players[target].influence_count,2) # target not dead
        self.assertEqual(self.game.game_data.players[player_turn].cash, 0) # player still loses money
        self.assertEqual(self.game.game_data.player_turn, (player_turn + 1) % 6) # it is the next player's turn

    def test_assassin_succeed(self):
        for i in range(6):
            player_turn = self.game.game_data.player_turn
            self.game.command(player_turn, {
                "command": CommandEnum.ACTION,
                "action": ActionEnum.INCOME,
                "stateId": self.game.game_data.state_id,
            })
        player_turn = self.game.game_data.player_turn
        target = (player_turn + 1) % len(self.game.game_data.players)
        self.game.command(player_turn, {
            "command" : CommandEnum.ACTION,
            "action"  : ActionEnum.ASSASSINATE,
            "target"  : target,
            "stateId" : self.game.game_data.state_id
            })
        for i in range(len(self.game.game_data.players)):
            if i != player_turn:
                self.game.command(i,{
                    "command" : CommandEnum.ALLOW,
                    "stateId" : self.game.game_data.state_id
                    })
        self.game.command(target, {
            "command" : CommandEnum.REVEAL,
            "role"    : self.game.game_data.players[target].hand[0].role,
            "stateId" : self.game.game_data.state_id
            })
        self.assertEqual(self.game._state_interface.__class__, PlayerTurn)

        self.assertEqual(self.game.game_data.players[target].influence_count,1) # target ded
        self.assertEqual(self.game.game_data.players[player_turn].cash, 0) # player lost money
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

    def test_more_actions(self):
        pass

class PlayRandomGameTest(BaseGameObjectTest):

    def test_run_through_game(self):
        """A modified version of step() from Benedict"""
        #return
        self.dones = {p for p in range(len(self.game.players))}
        steps=0
        while self.dones:
            steps+=1
            #print(self.game.to_dict(None), '\n')
            states = []
            for p in range(len(self.game.players)):
                states.append(GameState.from_dict(self.game.to_dict(p)))

            for p in range(len(self.game.players)):
                if self.game.player_is_done(p):
                    # print(f"removed {p}")  # <- does get called :)
                    if p in self.dones:
                        self.dones.remove(p)
                else:
                    turn = random_action(states[p])
                    #print(p, turn, '\n')
                    self.game.command(p, turn)
            if steps > 1000000:
                print(f"exitting at {steps} steps, dones={self.dones}")
                return


if __name__ == "__main__":
    unittest.main()
