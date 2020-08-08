from typing import Union

from mutiny.state_interface import StateInterface
from mutiny.actions import ForeignAid, Income, Coup, Steal, Tax, Assassinate, Exchange
from mutiny.exceptions import InvalidMove
from mutiny.game_enum import StateEnum, ActionEnum
from mutiny.states.wait_for_action_response import WaitForActionResponse
from mutiny.constants import COUP_COST, ASSASSINATE_COST


class PlayerTurn(StateInterface):

    # The following pairs of functions both check for the same things
    # however the bottom two raise an exception

    def _is_turn(self, player_id: int) -> bool:
        return self._data.player_turn == player_id

    def _must_coup(self) -> bool:
        return self._data.active_player.must_coup

    # helper function that returns the error message for non-coup actions
    def error_on_not_coup(self, player_id) -> Union[None, str]:
        if not self._is_turn(player_id):
            return "Not {}'s turn".format(self._data.players[player_id].name)
        if self._must_coup():
            return "{} must coup".format(self._data.active_player.name)
        return None

    @property
    def state_name(self) -> StateEnum:
        return StateEnum.START_TURN

    def error_on_noop(self, player_id: int) -> Union[None, str]:
        if self._is_turn(player_id):
            return f"Player {player_id} must make a move on {self.state_name}"
        return None

    def noop(self, player_id: int) -> StateInterface:
        if (error := self.error_on_noop(player_id)):
            raise InvalidMove(error)
        return self

    def error_on_income(self, player_id: int) -> Union[None, str]:
        return self.error_on_not_coup(player_id)

    def income(self, player_id: int) -> StateInterface:
        if (error := self.error_on_income(player_id)):
            raise InvalidMove(error)
        return Income(self._data).resolve()

    def error_on_f_aid(self, player_id: int) -> Union[None, str]:
        return self.error_on_not_coup(player_id)

    def f_aid(self, player_id: int) -> StateInterface:
        if (error := self.error_on_tax(player_id)):
            raise InvalidMove(error)

        queued = ForeignAid(self._data)
        return WaitForActionResponse(data=self._data, action=queued)  # no action role used for fAid

    def error_on_tax(self, player_id: int) -> Union[None, str]:
        return self.error_on_not_coup(player_id)

    def tax(self, player_id: int) -> StateInterface:
        if (error := self.error_on_tax(player_id)):
            raise InvalidMove(error)

        queued = Tax(self._data)
        return WaitForActionResponse(data=self._data, action=queued)

    def error_on_assassinate(self, player_id: int, target_id: int) -> Union[None, str]:
        if (error := self.error_on_not_coup(player_id)):
            return error
        if self._data.active_player.cash < ASSASSINATE_COST:
            return "{} does not have enough cash to assassinate".format(self._data.active_player.name)
        if (error := Assassinate.error_on_init(self._data, target_id)):
            return error
        return None

    def assassinate(self, player_id: int, target_id: int) -> StateInterface:
        if (error := self.error_on_assassinate(player_id, target_id)):
            raise InvalidMove(error)

        queued = Assassinate(self._data, target_id) # NOTE: targeted_action constructor also checks if target is valid
        self._data.active_player.removeCash(ASSASSINATE_COST)
        return WaitForActionResponse(data=self._data, action=queued)

    def error_on_steal(self, player_id: int, target_id: int) -> Union[None, str]:
        if (error := self.error_on_not_coup(player_id)):
            return error
        if (error := Steal.error_on_init(self._data, target_id)):
            return error
        return None

    def steal(self, player_id: int, target_id: int) -> StateInterface:
        if (error := self.error_on_steal(player_id, target_id)):
            raise InvalidMove(error)

        queued = Steal(self._data, target_id)
        return WaitForActionResponse(data=self._data, action=queued)

    def error_on_exchange(self, player_id: int) -> Union[None, str]:
        return self.error_on_not_coup(player_id)

    def exchange(self, player_id: int) -> StateInterface:
        if (error := self.error_on_exchange(player_id)):
            raise InvalidMove(error)

        queued = Exchange(self._data)
        return WaitForActionResponse(data=self._data, action=queued)

    def error_on_coup(self, player_id: int, target_id: int) -> Union[None, str]:
        if not self._is_turn(player_id):
            return "Not {}'s turn".format(self._data.players[player_id].name)
        if (self._data.active_player.cash < COUP_COST):
            return "{} does not have enough cash to coup".format(self._data.active_player.name)
        if (error := Coup.error_on_init(self._data, target_id)):
            return error
        return None

    def coup(self, player_id: int, target_id: int) -> StateInterface:
        if (error := self.error_on_coup(player_id, target_id)):
            raise InvalidMove(error)

        action = Coup(self._data, target_id)
        self._data.active_player.removeCash(COUP_COST)
        return action.resolve() # Returns reveal state with no action queued
