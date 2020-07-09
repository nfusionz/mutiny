from game_state import GameState
from game_enum import StateEnum
from state_interface import StateInterface
from exceptions import InvalidMove

from actions import ForeignAid, Income, Coup, Steal, Tax, Assassinate, Exchange


class PlayerTurn(StateInterface):

    def _checkTurn(self, player_id: int) -> None:
        if self._state.player_turn != player_id:
            raise InvalidMove("Not {}'s turn".format(self._state.players[player_id].name))

    def _checkCoup(self) -> None:
        if self._player.must_coup:
            raise InvalidMove("{} must coup".format(self._player.name))

    @property
    def state_name(self) -> StateEnum:
        return StateEnum.START_TURN

    def income(self, player_id: int) -> StateInterface:
        self._checkTurn(player_id)
        self._checkCoup()
        return Income(self._state).resolve()

    def fAid(self, player_id: int) -> StateInterface:
        self._checkTurn(player_id)
        self._checkCoup()

        queued = ForeignAid(self._state)
        return WaitForActionResponse(state=self._state, action=queued) # no action role used for fAid

    def tax(self, player_id: int) -> StateInterface:
        self._checkTurn(player_id)
        self._checkCoup()

        queued = Tax(self._state)
        return WaitForActionResponse(state=self._state, action=queued)

    def assassinate(self, player_id: int, target_id: int) -> StateInterface:
        self._checkTurn(player_id)
        self._checkCoup()

        queued = Assassinate(self._state, target_id)
        # TODO: On a challenge, return ChallengeReveal (the only way to get to a action_block for this)
        # - This is because you can block on a challenge phase :(
        return WaitForActionResponse(state=self._state, action=queued)

    def steal(self, player_id: int, target_id: int) -> StateInterface:
        self._checkTurn(player_id)
        self._checkCoup()

        queued = Steal(self._state, target_id)
        # TODO: Return action_challenge phase with Steal queued
        # TODO: On a challenge, return ChallengeReveal  (the only way to get to a action_block for this)
        # TODO: ChallengeReveal should have NoOp or Resolve queued depending on whether it was correct
        # TODO: ChallengeReveal then checks whether action is blockable, returning ActionBlock
        # TODO: On Block, return BlockChallenge with Resolve queued
        # TODO: On a challenge, return Reveal with NoOp or Resolve queued
        # - BlockChallengeReveal does not check if action is blockable
        # TODO: Resolve
        return WaitForActionResponse(state=self._state, action=queued)

    def exchange(self, player_id: int) -> StateInterface:
        self._checkTurn(player_id)
        self._checkCoup()

        queued = Exchange(self._state)

        return WaitForActionResponse(state=self._state, action=queued)

    def coup(self, player_id: int, target_id: int) -> StateInterface:
        self._checkTurn(player_id)
        return Coup(self._state, target_id).resolve()  # Returns reveal state with no action queued
