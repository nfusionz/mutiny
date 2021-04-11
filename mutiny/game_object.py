from typing import List, Dict, Union, Optional, Tuple

from mutiny.actions import QueuedAction
from mutiny.game_enum import CommandEnum, ActionEnum, RoleEnum, StateEnum
from mutiny.game_data import GameData
from mutiny.player import Player
from mutiny.exceptions import InvalidMove

DEBUG_LOG = False

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

    def get_players(self):
        return self.game_data.players

    @property
    def get_queued_action(self) -> Optional[QueuedAction]:
        return self._state_interface.queued_action

    @property
    def get_exchanges(self) -> Optional[Tuple[RoleEnum, RoleEnum]]:
        return self._state_interface.exchanges

    @property
    def get_blocking_role(self) -> Optional[RoleEnum]:
        return self._state_interface.blocking_role

    @property
    def get_player_to_reveal(self) -> Optional[int]:
        return self._state_interface.player_to_reveal

    def player_is_done(self, player_id: int) -> bool:
        if not self.game_data.player_alive(player_id):
            return True
        if self.game_data.winner_id == player_id:
            return True
        return False

    def game_is_over(self):
        return self.game_data.winner_id is not None
        # return all([self.player_is_done(p) for p in range(len(self.players))])

    @property
    def get_state_name(self) -> StateEnum:
        return self._state_interface.state_name

    @property
    def get_player_turn(self) -> int:
        return self.game_data.player_turn

    @property
    def get_target(self) -> Optional[int]:
        return self._state_interface.target

    def to_dict(self,player_id=None):
        return self._state_interface.to_dict(player_id=player_id)

    def reset(self):
        self._state_interface = self._state_interface.reset()

    def command(self, player_id: int, state_id: int, emission: Dict):
        """
        player_id - the player trying to take the action
        emission - a treason style command as a dictionary
        emission["stateId"] - the "time" at which the action taken was relevant
        """
        # check for out of date state id
        if self.get_state_id() != state_id:
            return

        if not emission or not emission["command"]:
            raise RuntimeError

        command = CommandEnum(emission["command"])

        if command == CommandEnum.NOOP:
            self._state_interface = self._state_interface.noop(player_id)
            return

        if self.player_is_done(player_id):
            raise InvalidMove("Player cannot take any more actions in current game state.")

        if command == CommandEnum.ACTION:
            if DEBUG_LOG:
                print(f"{player_id} {emission['action']} " + (f"{emission['target']}" if "target" in emission.keys() else ""))
            action = ActionEnum(emission["action"])
            target_id = emission["target"] if "target" in emission else None
            if action == ActionEnum.INCOME:
                self._state_interface = self._state_interface.income(player_id)
            if action == ActionEnum.F_AID:
                self._state_interface = self._state_interface.f_aid(player_id)
            if action == ActionEnum.TAX:
                self._state_interface = self._state_interface.tax(player_id)
            if action == ActionEnum.ASSASSINATE:
                self._state_interface = self._state_interface.assassinate(player_id, target_id)
            if action == ActionEnum.STEAL:
                self._state_interface = self._state_interface.steal(player_id, target_id)
            if action == ActionEnum.COUP:
                self._state_interface = self._state_interface.coup(player_id, target_id)
            if action == ActionEnum.EXCHANGE:
                self._state_interface = self._state_interface.exchange(player_id)

        if command == CommandEnum.ALLOW:
            self._state_interface = self._state_interface.allow(player_id)

        if command == CommandEnum.BLOCK:
            try:
                blocking_role = RoleEnum(emission["blockingRole"])
            except ValueError:
                # This happens when Benedict tries to block on a state that is blockable
                # vector_to_emission (see nnio in benedict) assumes that the state is blockable
                # If not, it will give an UNKNOWN for the blocking role
                raise InvalidMove("Must block with a valid influence")

            self._state_interface = self._state_interface.block(player_id, blocking_role)

        if command == CommandEnum.CHALLENGE:
            self._state_interface = self._state_interface.challenge(player_id)

        if command == CommandEnum.EXCHANGE:
            try:
                influences = tuple(RoleEnum(r) for r in emission["roles"])
            except ValueError:
                raise InvalidMove("Must replace with valid influences")

            self._state_interface = self._state_interface.replace(player_id, influences)

        if command == CommandEnum.REVEAL:
            try:
                reveal_role = RoleEnum(emission["role"])
            except ValueError:
                raise InvalidMove("Must reveal a valid influence")

            self._state_interface = self._state_interface.reveal(player_id, reveal_role)
