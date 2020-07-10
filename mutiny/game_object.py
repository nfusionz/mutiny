from game_enum import CommandEnum, ActionEnum, RoleEnum
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

    def command(self, player_id, emission, state_id):
        """
        player_id - the player trying to take the action
        emission - a treason style command as a dictionary
        state_id - the "time" at which the action taken was relevant
        """
        if not emission["command"]:
            raise Error

        # check for out of date state id
        if self.get_state_id != state_id:
            return

        command = CommandEnum(emission["command"])

        if command == CommandEnum.ACTION:
            action = ActionRole(emission["action"])
            if action == ActionEnum.INCOME:
                self._state_interface.income(self, player_id)
            if action == ActionEnum.F_AID:
                self._state_interface.f_aid(player_id)
            if action == ActionEnum.TAX:
                self._state_interface.tax(player_id)
            if action == ActionEnum.ASSASSINATE:
                target_id = emission["target"]
                self._state_interface.assassinate(player_id, target_id)
            if action == ActionEnum.STEAL:
                target_id = emission["target"]
                self._state_interface.steal(player_id, target_id)
            if action == ActionEnum.COUP:
                target_id = emission["target"]
                self._state_interface.coup(self, player_id, target_id)
            if action == ActionEnum.EXCHANGE:
                self._state_interface.exchange(self, player_id)
        if command == CommandEnum.ALLOW:
            self._state_interface.allow(player_id)
        if command == CommandEnum.BLOCK:
            blocking_role = emission["blockingRole"]
            self._state_interface.block(self, player_id, blocking_role)
        if command == CommandEnum.CHALLENGE:
            self._state_interface.challenge(player_id)
        if command == CommandEnum.EXCHANGE:
            influences = [RoleEnum(r) for r in emission["roles"]
            self._state_interface.replace(player_id)
        if command == CommandEnum.REVEAL:
            reveal_role = RoleEnum(emission["role"])
            self._state_interface.reveal(player_id, reveal_role)

