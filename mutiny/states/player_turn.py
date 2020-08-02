from mutiny.state_interface import StateInterface
from mutiny.actions import ForeignAid, Income, Coup, Steal, Tax, Assassinate, Exchange
from mutiny.exceptions import InvalidMove
from mutiny.game_enum import StateEnum
from mutiny.states.wait_for_action_response import WaitForActionResponse
from mutiny.constants import COUP_COST, ASSASSINATE_COST


class PlayerTurn(StateInterface):

    # The following pairs of functions both check for the same things
    # however the bottom two raise an exception

    def _is_turn(self, player_id: int):
        return self._data.player_turn == player_id

    def _must_coup(self) -> bool:
        return self._data.active_player.must_coup

    def can_make_non_coup(self, player_id: int):
        if not self._is_turn(player_id) or self._must_coup():
            return False
        return True

    def _checkTurn(self, player_id: int) -> None:
        if not self._is_turn(player_id):
            raise InvalidMove("Not {}'s turn".format(self._data.players[player_id].name))

    def _checkCoup(self) -> None:
        if self._must_coup():
            raise InvalidMove("{} must coup".format(self._data.active_player.name))



    @property
    def state_name(self) -> StateEnum:
        return StateEnum.START_TURN

    def can_noop(self, player_id: int) -> bool:
        return not self._is_turn(player_id)

    def noop(self, player_id: int) -> StateInterface:
        if not self.can_noop(player_id):
            raise InvalidMove(f"Player {player_id} must make a move on {self.state_name}")
        return self

    def can_income(self, player_id: int) -> bool:
        return can_make_non_coup(player_id)

    def income(self, player_id: int) -> StateInterface:
        self._checkTurn(player_id)
        self._checkCoup()
        return Income(self._data).resolve()

    def can_f_aid(self, player_id: int) -> bool:
        return can_make_non_coup(player_id)

    def f_aid(self, player_id: int) -> StateInterface:
        self._checkTurn(player_id)
        self._checkCoup()

        queued = ForeignAid(self._data)
        return WaitForActionResponse(data=self._data, action=queued)  # no action role used for fAid

    def can_tax(self, player_id: int) -> bool:
        return can_make_non_coup(player_id)

    def tax(self, player_id: int) -> StateInterface:
        self._checkTurn(player_id)
        self._checkCoup()

        queued = Tax(self._data)
        return WaitForActionResponse(data=self._data, action=queued)

    def can_assassinate(self, player_id: int, target_id: int) -> bool:
        return can_make_non_coup(player_id) and self._data.active_player.cash >= ASSASSINATE_COST

    def assassinate(self, player_id: int, target_id: int) -> StateInterface:
        self._checkTurn(player_id)
        self._checkCoup()
        if self._data.active_player.cash < ASSASSINATE_COST:
            raise InvalidMove("{} does not have enough cash to assassinate".format(self._data.active_player.name))
        queued = Assassinate(self._data, target_id) # constructor checks if target is valid

        self._data.active_player.removeCash(ASSASSINATE_COST)
        return WaitForActionResponse(data=self._data, action=queued)

    def can_steal(self, player_id: int, target_id: int) -> bool:
        return can_make_non_coup(player_id)

    def steal(self, player_id: int, target_id: int) -> StateInterface:
        self._checkTurn(player_id)
        self._checkCoup()
        queued = Steal(self._data, target_id)

        return WaitForActionResponse(data=self._data, action=queued)

    def can_exchange(self, player_id: int) -> bool:
        return can_make_non_coup(player_id)

    def exchange(self, player_id: int) -> StateInterface:
        self._checkTurn(player_id)
        self._checkCoup()

        queued = Exchange(self._data)
        return WaitForActionResponse(data=self._data, action=queued)


    def can_coup(self, player_id: int, target_id: int) -> bool:
        return can_make_non_coup(player_id) and self._data.active_player.cash >= COUP_COST


    def coup(self, player_id: int, target_id: int) -> StateInterface:
        self._checkTurn(player_id)
        if self._data.active_player.cash < COUP_COST:
            raise InvalidMove("{} does not have enough cash to coup".format(self._data.active_player.name))
        action = Coup(self._data, target_id) # constructor checks if target is valid

        self._data.active_player.removeCash(COUP_COST)
        return action.resolve() # Returns reveal state with no action queued
