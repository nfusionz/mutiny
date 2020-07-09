from abc import ABC, abstractmethod
from typing import Union

from game_state import GameState
from game_enum import ActionEnum, RoleEnum
from state_interface import StateInterface
from exceptions import InvalidMove
from constants import F_AID_GAIN, INCOME_GAIN, TAX_GAIN, STEAL_TRADE

from states.player_turn import PlayerTurn


class QueuedAction(ABC):
    """ An base class for actions to resolve. """

    def __init__(self, state: GameState):
        # TODO: Probably should be moved into the resolve method
        # Because the entire state of the application is based on sharing one gameState object :(
        self._state = state

    @abstractmethod
    def resolve(self) -> StateInterface:
        """ Override this method. Does not check if still valid. """
        # TODO: Check if player still alive in Reveal phases
        pass

    @property
    def target(self) -> Union[int, None]:
        """ Override. """
        return None

    @property
    def still_valid(self) -> bool:
        """
        Override this property if you need more than checking if the
        action player is still valid.
        """
        return self._state.player_alive(self._state.player_turn)

    @property
    @abstractmethod
    def action_name(self) -> ActionEnum:
        pass

    @property
    def action_role(self) -> Union[RoleEnum, None]:
        """
        Override this method to return the role "required" to take the associated action.
        Should be None for income, foreign aid, coup.
        """
        return None

    @property
    @abstractmethod
    def can_be_challenged(self) -> bool:
        pass

    @property
    @abstractmethod
    def can_be_blocked(self) -> bool:
        """ Note that you can block on a challenge phase. :( """
        pass



class QueuedTargetAction(QueuedAction):

    def __init__(self, state: GameState, target_id: int):
        if not self._state.player_alive(target_id):
            # Probably don't do this.
            raise InvalidMove("Target is invalid")
        super().__init__(state)
        self._target_id = target_id

    @property
    def target(self) -> Union[int, None]:
        return self._target_id

    @property
    def still_valid(self):
        return super().still_valid and self._state.player_alive(self._target_id)


class NoOp(QueuedAction):
    """ If an action fails, or after a reveal or coup state. """

    def resolve(self) -> StateInterface:
        return PlayerTurn(next(self._state))

    @property
    def still_valid(self) -> bool:
        return True

    @property
    def action_name(self) -> ActionEnum:
        return ActionEnum.NOP

    @property
    def can_be_challenged(self) -> bool:
        return False

    @property
    def can_be_blocked(self) -> bool:
        return False


class Income(QueuedAction):

    def resolve(self) -> StateInterface:
        self._state.players[self._state.player_turn].addCash(INCOME_GAIN)
        return PlayerTurn(next(self._state))

    @abstractmethod
    def action_name(self) -> ActionEnum:
        return ActionEnum.INCOME

    @property
    def can_be_challenged(self) -> bool:
        raise False

    @property
    def can_be_blocked(self) -> bool:
        return False


class ForeignAid(QueuedAction):

    def resolve(self) -> StateInterface:
        self._state.players[self._state.player_turn].addCash(F_AID_GAIN)
        return PlayerTurn(next(self._state))

    @abstractmethod
    def action_name(self) -> ActionEnum:
        return ActionEnum.F_AID

    @property
    def can_be_challenged(self) -> bool:
        return False

    @property
    def can_be_blocked(self) -> bool:
        return True


class Tax(QueuedAction):

    def resolve(self) -> StateInterface:
        self._state.players[self._state.player_turn].addCash(TAX_GAIN)
        return PlayerTurn(next(self._state))

    @abstractmethod
    def action_name(self) -> ActionEnum:
        return ActionEnum.TAX

    @property
    def action_role(self) -> RoleEnum:
        return RoleEnum.DUKE

    @property
    def can_be_challenged(self) -> bool:
        return True

    @property
    def can_be_blocked(self) -> bool:
        return False


class Assassinate(QueuedTargetAction):

    def resolve(self) -> StateInterface:
        if self._state.players[self._target_id].influence_count >= 2:
            pass  # TODO: Return reveal phase with NoOp action
        self._state.players[self._target_id].reveal()
        return PlayerTurn(next(self._state))

    @abstractmethod
    def action_name(self) -> ActionEnum:
        return ActionEnum.ASSASSINATE

    @property
    def action_role(self) -> RoleEnum:
        return RoleEnum.ASSASSIN

    @property
    def can_be_challenged(self) -> bool:
        return True

    @property
    def can_be_blocked(self) -> bool:
        return True


class Coup(QueuedTargetAction):

    def resolve(self) -> StateInterface:
        if self._state.players[self._target_id].influence_count == 2:
            pass  # TODO: Return reveal phase with NoOp action
        self._state.players[self._target_id].reveal()
        return PlayerTurn(next(self._state))

    @abstractmethod
    def action_name(self) -> ActionEnum:
        return ActionEnum.COUP

    @property
    def can_be_challenged(self) -> bool:
        return False

    @property
    def can_be_blocked(self) -> bool:
        return False


class Steal(QueuedTargetAction):

    def resolve(self) -> StateInterface:
        self._state.players[self._target_id].removeCash(STEAL_TRADE)
        self._state.players[self._state.player_turn].addCash(STEAL_TRADE)
        return PlayerTurn(next(self._state))

    @abstractmethod
    def action_name(self) -> ActionEnum:
        return ActionEnum.STEAL

    @property
    def action_role(self) -> RoleEnum:
        return RoleEnum.CAPTAIN

    @property
    def can_be_challenged(self) -> bool:
        return True

    @property
    def can_be_blocked(self) -> bool:
        return True


class Exchange(QueuedAction):

    def resolve(self) -> StateInterface:
        # Return exchange phase
        # pick two cards from the top of the deck for exchange options
        deck = self._state.deck
        op1 = deck.pop()
        op2 = deck.pop()
        return states.Exchange(state=self._state, exchange_options=[op1, op2])

    @abstractmethod
    def action_name(self) -> ActionEnum:
        return ActionEnum.EXCHANGE

    @property
    def action_role(self) -> RoleEnum:
        return RoleEnum.AMBASSADOR

    @property
    def can_be_challenged(self) -> bool:
        return True

    @property
    def can_be_blocked(self) -> bool:
        return False
