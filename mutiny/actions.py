from abc import ABC, abstractmethod
from typing import Union

from mutiny.game_data import GameData
from mutiny.game_enum import ActionEnum, RoleEnum
from mutiny.exceptions import InvalidMove
from mutiny.constants import *
import mutiny.states
from mutiny.state_interface import StateInterface


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
        if self._data.player_turn == target_id:
            raise InvalidMove("Can not target yourself")

        self._target_id = target_id

    @property
    def can_be_blocked(self) -> bool:
        return self._data.players[self._target_id].alive

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
        return mutiny.states.reveal.resolve_reveal(data=self._data, player_id=self._target_id, action=NoOp(self._data))

    @property
    def action_name(self) -> ActionEnum:
        return ActionEnum.ASSASSINATE

    @property
    def action_role(self) -> RoleEnum:
        return RoleEnum.ASSASSIN

    @property
    def can_be_challenged(self) -> bool:
        return True


class Coup(QueuedTargetAction):

    def resolve(self) -> StateInterface:
        return mutiny.states.reveal.resolve_reveal(data=self._data, player_id=self._target_id, action=NoOp(self._data))

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
        target = self._data.players[self._target_id]
        steal_amount = min(target.cash, STEAL_TRADE) # TODO: does treason permit stealing 0 cash?
        target.removeCash(steal_amount)
        self._data.active_player.addCash(steal_amount)
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
    def still_valid(self) -> bool:
        return self._data.active_player.alive


class Exchange(QueuedAction):

    def resolve(self) -> StateInterface:
        # Return exchange phase
        # pick two cards from the top of the deck for exchange options
        deck = self._data.deck
        op1 = deck.pop()
        op2 = deck.pop()
        import mutiny.states.exchange
        return mutiny.states.exchange.Exchange(data=self._data, exchange_options=(op1, op2))

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
