from actions import QueuedAction, NoOp
from game_enum import StateEnum, RoleEnum
from game_state import GameState
from state_interface import StateInterface
from exceptions import InvalidMove

from states.wait_for_block import WaitForBlock


def resolveReveal(state: GameState,
                  player_id: int,
                  action: QueuedAction,
                  query_block_next: bool = False) -> StateInterface:
    """
    If player has one influence left, reveal the last influence and resolve action.
    If player has two influence left, return Reveal phase with queued action.
    If query block_next, instead return a WaitBlock state.
    """
    reveal_player = state.players[player_id]
    if reveal_player.influence_count > 1:
        return Reveal(state, player_id, action, query_block_next)

    # Immediately resolve reveal
    reveal_player.reveal()

    # If target has not allowed / blocked action yet
    if query_block_next and action.can_be_blocked:
        return WaitForBlock(state, action)

    # Else, immediately resolve action
    if action.still_valid:
        return action.resolve()

    # Else, next turn
    return NoOp(state).resolve()


class Reveal(StateInterface):
    """
    It is better to used the resolveReveal method.
    Set query_block_next for the next state to be WaitBlock.
    """

    def __init__(self,
                 state: GameState,
                 reveal_id: int,
                 action: QueuedAction,
                 query_block_next: bool = False):
        super().__init__(state)
        self._reveal_id = reveal_id
        self._reveal_player = state.players[reveal_id]
        self._action = action
        self._block_next = query_block_next

    @property
    def state_name(self) -> StateEnum:
        return StateEnum.REVEAL

    def reveal(self, player_id: int, influence: RoleEnum) -> StateInterface:
        if player_id != self._reveal_id:
            raise InvalidMove("Wrong player to reveal")
        if not self._reveal_player.hasAliveInfluence(influence):
            raise InvalidMove("Player does not have {}".format(influence))

        self._reveal_player.reveal(influence)
        # If target has not allowed / blocked action yet
        if self._block_next and self._action.can_be_blocked:
            return WaitForBlock(self._state, self._action)
        # Else, resolve action
        if self._action.still_valid:
            return self._action.resolve()
        return NoOp(self._state).resolve()

