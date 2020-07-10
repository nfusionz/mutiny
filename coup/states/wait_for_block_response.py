from typing import Dict

from game_enum import StateEnum, RoleEnum
from game_state import GameState
from actions import QueuedAction, NoOp
from state_interface import StateInterface
from exceptions import InvalidMove

from states.player_turn import PlayerTurn
from states.reveal import resolve_reveal


class WaitForBlockResponse(StateInterface):

    def __init__(self, *,
                 state: GameState,
                 action: QueuedAction,
                 blocker_id: int,
                 block_role: RoleEnum):
        super().__init__(state=state)
        self._action = action
        self._allow = [False if player.alive else True for player in self._state.players]
        self._allow[blocker_id] = True

        self._blocker_id = blocker_id
        self._block_role = block_role

    @property
    def state_name(self) -> StateEnum:
        return StateEnum.WAIT_FOR_BLOCK_RESPONSE

    def to_dict(self, player_id=None) -> Dict:
        d = super().to_dict(player_id)
        d["state"]["action"] = self._action.action_name
        # person in the target field is necessarily the blocker
        d["state"]["target"] = self._blocker_id 
        d["state"]["blockingRole"] = self._block_role.value
        return d

    def challenge(self, player_id: int) -> StateInterface:
        if self._allow[player_id]:
            raise InvalidMove("Player has already implicitly allowed the block")

        # this is Treason-specific (you can lie about not having the influence in the og game)
        if self._state.players[self._blocker_id].hasAliveInfluence(self._block_role):
            # TODO: Swap the influence for another in the deck
            return resolve_reveal(state=self._state,
                                  player_id=player_id,
                                  action=NoOp(self._state))
        else:
            return resolve_reveal(state=self._state,
                                  player_id=self._blocker_id,
                                  action=self._action)

    def allow(self, player_id: int) -> StateInterface:
        # This is an invalid move because the blocker (from the NN) is able to allow his own block
        # Not a runtime error
        if self._allow[player_id]:
            raise InvalidMove("Player has already implicitly allowed the block")
        self._allow[player_id] = True
        if all(self._allow):
            # Action does not resolve
            return PlayerTurn(state=next(self._state))
        return self
