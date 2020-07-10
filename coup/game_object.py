from benedict.coup.game_state import GameState
from benedict.coup.states.player_turn import PlayerTurn

class GameObject:
    "Object to hold game state and control flow of game states"

    def __init__(self, players):
        self.game_state = GameState()
        self.game_state.players = players
        self.game_state.reset()
        self._state_interface = PlayerTurn(game_state)

    def get_state_id(self):
        return self.game_state.state_id

    def reset(self):
        return self._state_interface.reset()

    def command(self,player action, id):
        raise NotImplementedError

