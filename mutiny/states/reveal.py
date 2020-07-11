from typing import Dict

from mutiny.actions import QueuedAction, NoOp
from mutiny.game_enum import StateEnum, RoleEnum
from mutiny.game_data import GameData
from mutiny.state_interface import StateInterface
from mutiny.exceptions import InvalidMove

from mutiny.states.wait_for_block import WaitForBlock


def resolve_reveal(*, data: GameData,
                   player_id: int,
                   action: QueuedAction,
                   query_block_next: bool = False) -> StateInterface:
    """
    If player has one influence left, reveal the last influence and resolve action.
    If player has two influence left, return Reveal phase with queued action.
    If query block_next, instead return a WaitBlock state.
    """
    reveal_player = data.players[player_id]
    if reveal_player.influence_count > 1:
        return Reveal(data=data,
                      reveal_id=player_id,
                      action=action,
                      query_block_next=query_block_next)

    # Immediately resolve reveal
    reveal_player.reveal()

    # If target has not allowed / blocked action yet
    if query_block_next and action.can_be_blocked:
        return WaitForBlock(data=data, action=action)

    # Else, immediately resolve action
    if action.still_valid:
        return action.resolve()

    # Else, next turn
    return NoOp(data).resolve()


class Reveal(StateInterface):
    """
    It is better to used the resolveReveal method.
    Set query_block_next for the next state to be WaitBlock.
    """

    def __init__(self, *,
                 data: GameData,
                 reveal_id: int,
                 action: QueuedAction,
                 query_block_next: bool = False):
        super().__init__(data=data)
        self._reveal_id = reveal_id
        self._reveal_player = data.players[reveal_id]
        self._action = action
        self._block_next = query_block_next

    @property
    def state_name(self) -> StateEnum:
        return StateEnum.REVEAL

    def to_dict(self, player_id=None) -> Dict:
        d = super().to_dict(player_id)
        d["state"]["action"] = self._action.action_name
        if self._action.target is not None:
            d["state"]["target"] = self._action.target
        # TODO: blockingRole?
        d["state"]["playerToReveal"] = self._reveal_player
        return d

    def reveal(self, player_id: int, influence: RoleEnum) -> StateInterface:
        if player_id != self._reveal_id:
            raise InvalidMove("Wrong player to reveal")
        if not self._reveal_player.hasAliveInfluence(influence):
            raise InvalidMove("Player does not have {}".format(influence))

        self._reveal_player.reveal(influence)
        # If target has not allowed / blocked action yet
        if self._block_next and self._action.can_be_blocked:
            return WaitForBlock(data=self._data,
                                action=self._action)
        # Else, resolve action
        if self._action.still_valid:
            return self._action.resolve()
        return NoOp(self._data).resolve()
