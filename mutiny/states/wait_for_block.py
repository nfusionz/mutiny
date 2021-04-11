from typing import Dict, Union

from mutiny.actions import QueuedAction, QueuedTargetAction
from mutiny.game_enum import ActionEnum, StateEnum, RoleEnum
from mutiny.game_data import GameData
from mutiny.state_interface import StateInterface
from mutiny.exceptions import InvalidMove

from mutiny.states.wait_for_block_response import WaitForBlockResponse

# TODO: Probably should be moved into actions logic somehow
BLOCKING_ROLES = {
    ActionEnum.F_AID: {RoleEnum.DUKE},
    ActionEnum.STEAL: {RoleEnum.AMBASSADOR, RoleEnum.CAPTAIN},
    ActionEnum.ASSASSINATE: {RoleEnum.CONTESSA},
}


class WaitForBlock(StateInterface):
    """
    Only accessible after a failed action challenge.
    """

    def __init__(self, *,
                 data: GameData,
                 action: QueuedAction):
        super().__init__(data=data)
        self._action = action
        self._allow = [False if player.alive else True for player in self._data.players]
        self._allow[self._data.player_turn] = True

    def to_dict(self, player_id=None) -> Dict:
        d = super().to_dict(player_id)
        d["state"]["action"] = self._action.action_name.value
        if self._action.target is not None:
            d["state"]["target"] = self._action.target
        return d

    @property
    def state_name(self) -> StateEnum:
        return StateEnum.WAIT_FOR_BLOCK

    @property
    def queued_action(self) -> QueuedAction:
        return self._action

    @property
    def target(self) -> int:
        return self._action.target

    def error_on_noop(self, player_id: int) -> Union[None, str]:
        # If player has not already implicitly allowed
        if not self._allow[player_id] and (self._action.action_name == ActionEnum.F_AID or self._action.target == player_id):
            # Can only block duke, or block something targeted at you
            return f"Player {player_id} must allow or block on {self.state_name}"
        return None

    def noop(self, player_id: int) -> StateInterface:
        if (error := self.error_on_noop(player_id)):
            raise InvalidMove(error)
        return self

    def error_on_block(self, player_id: int, blocking_role: RoleEnum) -> Union[None, str]:
        if self._allow[player_id]:
            return "Player has already implicitly allowed the action"
        if blocking_role not in BLOCKING_ROLES[self._action.action_name]:
            return "Cannot block {} with {}".format(self._action.action_name, blocking_role)
        if blocking_role != RoleEnum.DUKE and player_id != self._action.target:
            return "Cannot block if you are not the target"
        return None

    def block(self, player_id: int, blocking_role: RoleEnum) -> StateInterface:
        if (error := self.error_on_block(player_id, blocking_role)):
            raise InvalidMove(error)

        return WaitForBlockResponse(data=self._data,
                                    action=self._action,
                                    blocker_id=player_id,
                                    block_role=blocking_role)

    def error_on_allow(self, player_id: int) -> Union[None, str]:
        if self._allow[player_id]:
            return "Player has already implicitly allowed the action"
        return None

    def allow(self, player_id: int) -> StateInterface:
        if (error := self.error_on_allow(player_id)):
            raise InvalidMove(error)

        # targeted actions only require permission of the target after a challenge
        self._allow[player_id] = True
        if isinstance(self._action, QueuedTargetAction) and self._allow[self._action.target]:
            return self._action.resolve()
        if all(self._allow):
            return self._action.resolve()
        return self
