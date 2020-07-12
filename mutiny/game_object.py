from typing import List
from mutiny.game_enum import CommandEnum, ActionEnum, RoleEnum
from mutiny.game_data import GameData
from mutiny.player import Player
from mutiny.exceptions import InvalidMove


class GameObject:
    "Object to hold game state and control flow of game states"

    def __init__(self, player_names: List[str]):
        from mutiny.states.player_turn import PlayerTurn
        self.players = [Player(name, i) for i,name in enumerate(player_names)]
        self.game_data = GameData(self.players)
        self.game_data.reset()
        self._state_interface = PlayerTurn(data=self.game_data)

    def get_state_id(self):
        return self.game_data.state_id

    def player_is_done(self, player_id: int) -> bool:
        if not self.game_data.player_alive(player_id):
            return True
        if self.game_data.winner_id == player_id:
            return True
        return False

    def to_dict(self,player_id=None):
        return self._state_interface.to_dict(player_id=player_id)

    def reset(self):
        self._state_interface = self._state_interface.reset()

    def command(self, player_id, emission):
        """
        player_id - the player trying to take the action
        emission - a treason style command as a dictionary
        emission["stateId"] - the "time" at which the action taken was relevant
        """
        if emission is None: # NOP
            return

        if not emission["command"]:
            raise RuntimeError

        # check for out of date state id
        if self.get_state_id() != emission["stateId"]:
            return

        if self.player_is_done(player_id):
            raise InvalidMove("Player cannot take any more actions in current game state.")

        command = CommandEnum(emission["command"])

        if command == CommandEnum.ACTION:
            action = ActionEnum(emission["action"])
            if action == ActionEnum.INCOME:
                self._state_interface = self._state_interface.income(player_id)
            if action == ActionEnum.F_AID:
                self._state_interface = self._state_interface.f_aid(player_id)
            if action == ActionEnum.TAX:
                self._state_interface = self._state_interface.tax(player_id)
            if action == ActionEnum.ASSASSINATE:
                target_id = emission["target"]
                self._state_interface = self._state_interface.assassinate(player_id, target_id)
            if action == ActionEnum.STEAL:
                target_id = emission["target"]
                self._state_interface = self._state_interface.steal(player_id, target_id)
            if action == ActionEnum.COUP:
                target_id = emission["target"]
                self._state_interface = self._state_interface.coup(player_id, target_id)
            if action == ActionEnum.EXCHANGE:
                self._state_interface = self._state_interface.exchange(player_id)
        if command == CommandEnum.ALLOW:
            self._state_interface = self._state_interface.allow(player_id)
        if command == CommandEnum.BLOCK:
            blocking_role = RoleEnum(emission["blockingRole"])
            self._state_interface = self._state_interface.block(player_id, blocking_role)
        if command == CommandEnum.CHALLENGE:
            self._state_interface = self._state_interface.challenge(player_id)
        if command == CommandEnum.EXCHANGE:
            influences = tuple(RoleEnum(r) for r in emission["roles"])
            self._state_interface = self._state_interface.replace(player_id, influences)
        if command == CommandEnum.REVEAL:
            reveal_role = RoleEnum(emission["role"])
            self._state_interface = self._state_interface.reveal(player_id, reveal_role)

