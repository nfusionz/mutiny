import unittest

from mutiny.player import Player
from mutiny.states.player_turn import PlayerTurn
from mutiny.states.reveal import Reveal

from mutiny.game_data import GameData
from mutiny.actions import NoOp


class RevealTest(unittest.TestCase):

    def setUp(self) -> None:
        self.players = ["A", "B", "C", "D", "E", "F"]

    def test_noop_reveal_card(self) -> None:
        for influence in range(0, 2):
            with self.subTest(influence=influence):
                data = GameData([Player(name, i) for i, name in enumerate(self.players)])
                data.reset()
                data.player_turn = 0
                state = Reveal(data=data, reveal_id=0, action=NoOp(data))

                player_hand = data.players[0].hand
                influence_to_reveal = player_hand[influence].role
                new_state = state.reveal(0, influence_to_reveal)

                self.assertIsInstance(new_state, PlayerTurn)
                self.assertEqual(data.player_turn, 1)
                self.assertEqual(data.state_id, 2)  # Make sure the state_id advances once
                if player_hand[0].role == influence_to_reveal:
                    # For revealing influence 1, there is a case with double influence where this can occur
                    self.assertTrue(data.players[0].hand[0].revealed)
                    self.assertFalse(data.players[1].hand[1].revealed)
                else:
                    self.assertTrue(data.players[0].hand[1].revealed)
                    self.assertFalse(data.players[1].hand[0].revealed)

                for i in range(1, len(self.players)):
                    self.assertFalse(data.players[i].hand[0].revealed)
                    self.assertFalse(data.players[i].hand[1].revealed)


if __name__ == '__main__':
    unittest.main()
