import unittest

from mutiny.game_data import GameData
from mutiny.player import Player

from mutiny.actions import NoOp
from mutiny.states.player_turn import *
from mutiny.states.reveal import *


class RevealTest(unittest.TestCase):

    def setUp(self) -> None:
        self.players = ["A", "B", "C", "D", "E", "F"]

    def test_noop_reveal_first_card(self) -> None:
        data = GameData([Player(name, i) for i, name in enumerate(self.players)])
        data.player_turn = 0
        data.reset()

        state = Reveal(data=data, reveal_id=0, action=NoOp(data))
        new_state = state.reveal(0, data.players[0].hand[0].role)

        self.assertIsInstance(new_state, PlayerTurn,
                              "Reveal with NoOp should have returned a PlayerTurn")
        self.assertTrue(data.players[0].hand[0].revealed,
                        "Player 0 should have his first influence revealed")
        self.assertFalse(data.players[1].hand[1].revealed,
                         "Player 0 should not have his second influence revealed")
        for i in range(1, len(self.players)):
            self.assertFalse(data.players[i].hand[0].revealed,
                             "Player {} should not have influence 0 modified".format(i))
            self.assertFalse(data.players[i].hand[0].revealed,
                             "Player {} should not have influence 1 modified".format(i))


if __name__ == '__main__':
    unittest.main()
