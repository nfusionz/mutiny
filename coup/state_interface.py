from abc import ABC, abstractmethod
from typing import Union, Tuple

from game_state import GameState
from game_enum import StateEnum, RoleEnum
from exceptions import InvalidMove


class StateInterface(ABC):
    """ Superclass for ways that GameState can be modified.
    Extend this class to implement game logic. All methods
    that modify game state return a (possibly new) StateInterface
    that wraps it. Essentially a state machine. """

    def __init__(self, state: GameState):
        self._state = state
        self._player = state.players[state.player_turn]

    @property
    @abstractmethod
    def state_name(self) -> StateEnum:
        """ Override to give the current StateEnum. """
        pass

    def income(self, player_id: int) -> "StateInterface":
        raise InvalidMove("Cannot take income on {}".format(self.state_name))

    def fAid(self, player_id: int) -> "StateInterface":
        raise InvalidMove("Cannot take foreign aid on {}".format(self.state_name))

    def tax(self, player_id: int) -> "StateInterface":
        raise InvalidMove("Cannot tax on {}".format(self.state_name))

    def assassinate(self, player_id: int, target_id: int) -> "StateInterface":
        raise InvalidMove("Cannot assassinate on {}".format(self.state_name))

    def steal(self, player_id: int, target_id: int) -> "StateInterface":
        raise InvalidMove("Cannot steal on {}".format(self.state_name))

    def coup(self, player_id: int, target_id: int) -> "StateInterface":
        raise InvalidMove("Cannot coup on {}".format(self.state_name))

    def exchange(self, player_id: int) -> "StateInterface":
        raise InvalidMove("Cannot perform exchange action on {}".format(self.state_name))

    def challenge(self, player_id: int) -> "StateInterface":
        raise InvalidMove("Cannot challenge on {}".format(self.state_name))

    def block(self, player_id: int, blocking_role: RoleEnum) -> "StateInterface":
        raise InvalidMove("Cannot block on {}".format(self.state_name))

    def allow(self, player_id: int) -> "StateInterface":
        """ Any form of synchronization should be performed outside of this class. """
        raise InvalidMove("Cannot allow on {}".format(self.state_name))

    def reveal(self, player_id: int, influence: RoleEnum) -> "StateInterface":
        raise InvalidMove("Cannot reveal on {}".format(self.state_name))

    def replace(self, player_id: int, influences: Tuple[RoleEnum, Union[RoleEnum, None]]) -> "StateInterface":
        raise InvalidMove("Cannot replace cards on {}".format(self.state_name))
