from abc import ABC, abstractmethod
from typing import Union

from mutiny.game_data import GameData
from mutiny.game_enum import ActionEnum, RoleEnum
from mutiny.state_interface import StateInterface
from mutiny.exceptions import InvalidMove
from mutiny.constants import F_AID_GAIN, INCOME_GAIN, TAX_GAIN, STEAL_TRADE

import mutiny.states.player_turn
from mutiny.states import exchange as exchange


class QueuedAction(ABC):
    """ An base class for actions to resolve. """

    def __init__(self, data: GameData):
        # TODO: Probably should be moved into the resolve method
        # Because the entire state of the application is based on sharing one GameData object :)
        self._data = data

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
        return self._data.player_alive(self._data.player_turn)

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

    def __init__(self, data: GameData, target_id: int):
        super().__init__(data)
        if not self._data.player_alive(target_id):
            # Probably don't do this.
            raise InvalidMove("Target is invalid")
        self._target_id = target_id

    @property
    def target(self) -> Union[int, None]:
        return self._target_id

    @property
    def still_valid(self):
        return super().still_valid and self._data.player_alive(self._target_id)


class NoOp(QueuedAction):
    """ If an action fails, or after a reveal or coup state. """

    def resolve(self) -> StateInterface:
        return mutiny.states.player_turn.PlayerTurn(data=self._data.next_turn())

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
        self._data.players[self._data.player_turn].addCash(INCOME_GAIN)
        return mutiny.states.player_turn.PlayerTurn(data=self._data.next_turn())

    @property
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
        self._data.players[self._data.player_turn].addCash(F_AID_GAIN)
        return mutiny.states.player_turn.PlayerTurn(data=self._data.next_turn())

    @property
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
        self._data.players[self._data.player_turn].addCash(TAX_GAIN)
        return mutiny.states.player_turn.PlayerTurn(data=self._data.next_turn())

    @property
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
        if self._data.players[self._target_id].influence_count >= 2:
            pass  # TODO: Return reveal phase with NoOp action
        self._data.players[self._target_id].reveal()
        return mutiny.states.player_turn.PlayerTurn(data=self._data.next_turn())

    @property
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
        if self._data.players[self._target_id].influence_count == 2:
            pass  # TODO: Return reveal phase with NoOp action
        self._data.players[self._target_id].reveal()
        return mutiny.states.player_turn.PlayerTurn(data=self._data.next_turn())

    @property
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
        self._data.players[self._target_id].removeCash(STEAL_TRADE)
        self._data.players[self._data.player_turn].addCash(STEAL_TRADE)
        return mutiny.states.player_turn.PlayerTurn(data=self._data.next_turn())

    @property
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
        deck = self._data.deck
        op1 = deck.pop()
        op2 = deck.pop()
        return exchange.Exchange(data=self._data, exchange_options=(op1, op2))

    @property
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
