from actions import QueuedAction, NoOp
from exceptions import InvalidMove
from game_enum import StateEnum, RoleEnum
from game_state import GameState
from state_interface import StateInterface
from states.reveal import resolveReveal
from states.wait_for_block import WaitForBlock


class WaitForActionResponse(StateInterface):

    def __init__(self, state: GameState, action: QueuedAction, action_role: RoleEnum):
        super().__init__(state)
        self._action = action
        self._role = action
        self._allow = [False if player.alive else True for player in self._state.players]
        self._allow[self._state.player_turn] = True

    @property
    def state_name(self) -> StateEnum:
        return StateEnum.WAIT_FOR_ACTION_RESPONSE

    def challenge(self, player_id: int) -> StateInterface:
        if self._allow[player_id]:
            raise InvalidMove("Player has implicitly allowed the action")

        if self._state.players[self._state.player_turn].hasAliveInfluence(self._role):
            # Challenger loses an influence, action may or may not resolve
            return resolveReveal(self._state, player_id, self._action, query_block_next=True)
        else:
            # Claimant loses an influence, action does not resolve (except for the initial cost)
            return resolveReveal(self._state, self._state.player_turn, NoOp(self._state))

    def block(self, player_id: int, blocking_role: RoleEnum) -> StateInterface:
        return WaitForBlock(self._state, self._action).block(player_id, blocking_role)

    def allow(self, player_id: int) -> StateInterface:
        if self._allow[player_id]:
            raise InvalidMove("Player has already implicitly allowed the action")
        self._allow[player_id] = True

        # No one has challenged or blocked, so the action resolves
        # Blocks are done on this turn, unless a challenge occurs
        if all(self._allow): return self._action.resolve()
        return self

