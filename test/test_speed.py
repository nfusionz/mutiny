import unittest

from mutiny.game_object import GameObject
from mutiny.exceptions import InvalidMove

from benedict.agents.RandomAgent import random_action
from benedict.GameState import GameState


class SpeedTest(unittest.TestCase):

    def test_go_fast(self):
        players = ["A", "B", "C", "D", "E", "F"]
        for i in range(1000):
            game = GameObject(players)
            steps = 0
            while not game.game_is_over():
                steps += 1
                # get observations
                states = []
                for p in range(6):
                    states.append(GameState.from_dict(game.to_dict(p)))
                # act on observations
                for p in range(6):
                    turn = random_action(states[p]) # random_action knows to NOOP when dead
                    game.command(p, states[p].stateId, turn)
                    # TODO: Write regression test for noop when you're not targeted on WaitForBlockResponse
                if steps > 10**5:
                    raise RuntimeError("Something has gone horribly wrong! Steps exceeded 10^5")
                    return


if __name__ == '__main__':
    unittest.main()
