from abc import ABC, abstractmethod
from typing import Union, Tuple, Dict

from mutiny.game_data import GameData
from mutiny.game_enum import StateEnum, RoleEnum
from mutiny.exceptions import InvalidMove


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

    @abstractmethod
    def can_noop(self, player_id: int) -> bool:
        return False

    def noop(self, player_id: int) -> "StateInterface":
        """ For Benedict (The AI). """
        pass

    def can_income(self, player_id: int) -> bool:
        return False

    def income(self, player_id: int) -> "StateInterface":
        raise InvalidMove("Cannot take income on {}".format(self.state_name))

    def can_faid(self, player_id: int) -> bool:
        return False

    def f_aid(self, player_id: int) -> "StateInterface":
        raise InvalidMove("Cannot take foreign aid on {}".format(self.state_name))

    def can_tax(self, player_id: int) -> bool:
        return False

    def tax(self, player_id: int) -> "StateInterface":
        raise InvalidMove("Cannot tax on {}".format(self.state_name))

    def can_assassinate(self, player_id: int, target_id: int) -> bool:
        return False

    def assassinate(self, player_id: int, target_id: int) -> "StateInterface":
        raise InvalidMove("Cannot assassinate on {}".format(self.state_name))

    def can_steal(self, player_id: int) -> bool:
        return False

    def steal(self, player_id: int, target_id: int) -> "StateInterface":
        raise InvalidMove("Cannot steal on {}".format(self.state_name))

    def can_coup(self, player_id: int, target_id: int) -> bool:
        return False

    def coup(self, player_id: int, target_id: int) -> "StateInterface":
        raise InvalidMove("Cannot coup on {}".format(self.state_name))

    def can_exchange(self, player_id: int) -> "StateInterface":
        return False

    def exchange(self, player_id: int) -> "StateInterface":
        raise InvalidMove("Cannot perform exchange action on {}".format(self.state_name))

    def can_challenge(self, player_id: int) -> bool:
        return False

    def challenge(self, player_id: int) -> "StateInterface":
        raise InvalidMove("Cannot challenge on {}".format(self.state_name))

    def can_block(self, player_id: int, blocking_role: RoleEnum) -> bool:
        return False

    def block(self, player_id: int, blocking_role: RoleEnum) -> "StateInterface":
        raise InvalidMove("Cannot block on {}".format(self.state_name))

    def can_allow(self, player_id: int) -> bool:
        return False

    def allow(self, player_id: int) -> "StateInterface":
        """ Any form of synchronization should be performed outside of this class. """
        raise InvalidMove("Cannot allow on {}".format(self.state_name))

    def can_reveal(self, player_id: int, influence: RoleEnum) -> bool:
        return False

    def reveal(self, player_id: int, influence: RoleEnum) -> "StateInterface":
        raise InvalidMove("Cannot reveal on {}".format(self.state_name))

    def replace(self, player_id: int, influences: Tuple[RoleEnum, Union[RoleEnum, None]]) -> bool:
        return False

    def replace(self, player_id: int, influences: Tuple[RoleEnum, Union[RoleEnum, None]]) -> "StateInterface":
        raise InvalidMove("Cannot replace cards on {}".format(self.state_name))
