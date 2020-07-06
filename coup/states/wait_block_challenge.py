from game_enum import StateEnum, RoleEnum
from game_state import GameState
from actions import QueuedAction, NoOp
from state_interface import StateInterface
from exceptions import InvalidMove

from states.player_turn import PlayerTurn
from states.reveal import resolveReveal


class WaitBlockChallenge(StateInterface):

    def __init__(self,
                 state: GameState,
                 action: QueuedAction,
                 blocker_id: int,
                 block_role: RoleEnum):
        super().__init__(state)
        self._action = action
        self._allow = [False if player.alive else True for player in self._state.players]
        self._allow[blocker_id] = True

        self._blocker_id = blocker_id
        self._block_role = block_role

    @property
    def state_name(self) -> StateEnum:
        return StateEnum.WAIT_BLOCK_CHALLENGE

    def challenge(self, player_id: int) -> StateInterface:
        if self._allow[player_id]:
            raise InvalidMove("Player has already implicitly allowed the block")

        # this is Treason-specific (you can lie about not having the influence in the og game)
        if self._state.players[self._blocker_id].hasAliveInfluence(self._block_role):
            # TODO: Swap the influence for another in the deck
            return resolveReveal(self._state, player_id, NoOp(self._state))
        else:
            return resolveReveal(self._state, self._blocker_id, self._action)

    def allow(self, player_id: int) -> StateInterface:
        # This is an invalid move because the blocker (from the NN) is able to allow his own block
        # Not a runtime error
        if self._allow[player_id]:
            raise InvalidMove("Player has already implicitly allowed the block")
        self._allow[player_id] = True
        if all(self._allow):
            # Action does not resolve
            return PlayerTurn(next(self._state))
        return self
