import gym

from ray.rllib.env.multi_agent_env import MultiAgentEnv
from ray.rllib.tests.test_rollout_worker import MockEnv, MockEnv2
from benedict.coup.gamestate import GameState

from benedict.coup.game.object import GameObject

def dict_to_nn(action_dict):
    """Converts StateInterface output dictionary to neural network input"""
    raise NotImplementedError

def nn_to_dict(action_nn):
    """Converts neural network output to StateInterface input dictionary"""
    raise NotImplementedError

class PyTreasonEnv(MultiAgentEnv):

    def __init__(self, num_agents, stop_on_state_id=1000):
        """Spawn agents here"""
        self.agents = ["agent_{}".format(i) for i in range(num)]
        self.dones = set()
        self.game = GameObject(self.agents)
        self.stop_on_state_id = stop_on_state_id

        def discretize(arr):
            return [Discrete(x) for x in arr]
        cash = [Box(low=np.array([0]),high=np.array([12]),dtype=np.int8)]
        other_player_cards = discretize([6,6])
        observation_space = Tuple(
                discretize([5, 2, 5, 2]) +
                cash +
                other_player_cards + cash +
                other_player_cards + cash +
                other_player_cards + cash +
                other_player_cards + cash +
                other_player_cards + cash +
                discretize([6, 6, 7, 6, 2, 5, 5, 6])
                )

        action_space = MultiDiscrete([7, 7, 5, 2, 5, 5, 5])

    def reset(self):
        """reset agents and env here"""
        # assumes tune handles resetting policy
        self.dones = set()
        return dict_to_nn(self.game.reset())

    def step(self, action_nn):
        """action_nn is a dictionary of nn actions. Returns a dictionay of nn obs"""
        rewards, obs, done = {}, {}, {}
        for player, action in enumerate(action_nn):

            if self.game.get_state_id() >= self.stop_on_state_id:
                rewards[player] = -50
                done   [player] = True
                continue

            done[player] = False
            try:
                game.command(player, nn_to_dict(action), self)
                rewards[player] = 0.01
            except InvalidMove:
                rewards[player] = -100
        obs = {}
        for player in action_nn.keys():
            [player] = dict_to_nn(hide_info(game.to_dict()))

        return obs, rewards, done, None
