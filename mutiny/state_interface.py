from abc import ABC, abstractmethod
from typing import Union, Tuple, Dict, Optional

# from mutiny.actions import QueuedAction
from mutiny.game_data import GameData
from mutiny.game_enum import StateEnum, RoleEnum
from mutiny.exceptions import InvalidMove

INVALID_TRANSITION = "Cannot %s on %s"

class StateInterface(ABC):
    """ Superclass for ways that GameData can be modified.
    Extend this class to implement game logic. All methods
    that modify game data return a (possibly new) StateInterface
    that wraps it. Essentially a state machine. """

    def __init__(self, *, data: GameData):
        self._data = data
        self._data.state_id += 1

    @property
    def state_id(self) -> int:
        return self._data.state_id

    @property
    @abstractmethod
    def state_name(self) -> StateEnum:
        """ Override to give the current StateEnum. """
        pass

    @property
    def queued_action(self):
        return None

    @property
    def exchanges(self) -> Optional[Tuple[RoleEnum, RoleEnum]]:
        return None

    @property
    def blocking_role(self) -> Optional[RoleEnum]:
        return None

    @property
    def player_to_reveal(self) -> Optional[int]:
        return None

    @property
    def target(self) -> Optional[int]:
        """ This is necessary because target is overloaded to include the blocker for foreign aid. """
        return None

    def to_dict(self, player_id=None) -> Dict:
        """
        Override and use super().to_dict to fill out remaining info in state dictionary (as it would appear in Treason).
        player_id indicates what player is "asking for" the information. Information should be hidden accordingly.
        When player_id is None, all info should be provided.
        Fields to possibly be filled out in implementations include: [action, target, blockingRole, exchangeOptions, playerToReveal]
        """
        d = self._data.to_dict(player_id=player_id)
        d["state"] = {
            "playerIdx": self._data.player_turn,
            "name": self.state_name.value
        }
        return d

    def reset(self) -> "StateInterface":
        import mutiny.states.player_turn
        self._data.reset()
        return mutiny.states.player_turn.PlayerTurn(data=self._data)

    def error_on_noop(self, player_id: int) -> Union[None, str]:
        return INVALID_TRANSITION % ("noop", self.state_name)

    def noop(self, player_id: int) -> "StateInterface":
        """ For Benedict (The AI). """
        raise InvalidMove(self.error_on_noop(player_id))

    def error_on_income(self, player_id: int) -> Union[None, str]:
        return INVALID_TRANSITION % ("income", self.state_name)

    def income(self, player_id: int) -> "StateInterface":
        raise InvalidMove(self.error_on_income(player_id))

    def error_on_f_aid(self, player_id: int) -> Union[None, str]:
        return INVALID_TRANSITION % ("foreign aid", self.state_name)

    def f_aid(self, player_id: int) -> "StateInterface":
        raise InvalidMove(self.error_on_f_aid(player_id))

    def error_on_tax(self, player_id: int) -> Union[None, str]:
        return INVALID_TRANSITION % ("tax", self.state_name)

    def tax(self, player_id: int) -> "StateInterface":
        raise InvalidMove(self.error_on_tax(player_id))

    def error_on_assassinate(self, player_id: int, target_id: int) -> Union[None, str]:
        return INVALID_TRANSITION % ("assassinate", self.state_name)

    def assassinate(self, player_id: int, target_id: int) -> "StateInterface":
        raise InvalidMove(self.error_on_assassinate(player_id, target_id))

    def error_on_steal(self, player_id: int, target_id: int) -> Union[None, str]:
        return INVALID_TRANSITION % ("steal", self.state_name)

    def steal(self, player_id: int, target_id: int) -> "StateInterface":
        raise InvalidMove(self.error_on_steal(player_id, target_id))

    def error_on_coup(self, player_id: int, target_id: int) -> Union[None, str]:
        return INVALID_TRANSITION % ("coup", self.state_name)

    def coup(self, player_id: int, target_id: int) -> "StateInterface":
        raise InvalidMove(self.error_on_coup(player_id, target_id))

    def error_on_exchange(self, player_id: int) -> "StateInterface":
        return INVALID_TRANSITION % ("exchange", self.state_name)

    def exchange(self, player_id: int) -> "StateInterface":
        raise InvalidMove(self.error_on_exchange(player_id))

    def error_on_challenge(self, player_id: int) -> Union[None, str]:
        return INVALID_TRANSITION % ("challenge", self.state_name)

    def challenge(self, player_id: int) -> "StateInterface":
        raise InvalidMove(self.error_on_challenge(player_id))

    def error_on_block(self, player_id: int, blocking_role: RoleEnum) -> Union[None, str]:
        return INVALID_TRANSITION % ("block", self.state_name)

    def block(self, player_id: int, blocking_role: RoleEnum) -> "StateInterface":
        raise InvalidMove(self.error_on_block(player_id, blocking_role))

    def error_on_allow(self, player_id: int) -> Union[None, str]:
        return INVALID_TRANSITION % ("allow", self.state_name)

    def allow(self, player_id: int) -> "StateInterface":
        """ Any form of synchronization should be performed outside of this class. """
        raise InvalidMove(self.error_on_allow(player_id))

    def error_on_reveal(self, player_id: int, influence: RoleEnum) -> Union[None, str]:
        return INVALID_TRANSITION % ("reveal", self.state_name)

    def reveal(self, player_id: int, influence: RoleEnum) -> "StateInterface":
        raise InvalidMove(self.error_on_reveal(player_id, influence))

    def error_on_replace(self, player_id: int, influences: Tuple[RoleEnum, Union[RoleEnum, None]]) -> Union[None, str]:
        return INVALID_TRANSITION % ("replace", self.state_name)

    def replace(self, player_id: int, influences: Tuple[RoleEnum, Union[RoleEnum, None]]) -> "StateInterface":
        raise InvalidMove(self.error_on_replace(player_id, influences))
