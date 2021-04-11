from typing import Dict, Union

from mutiny.actions import Assassinate, QueuedAction, NoOp
from mutiny.exceptions import InvalidMove
from mutiny.game_enum import StateEnum, RoleEnum, ActionEnum
from mutiny.game_data import GameData
from mutiny.state_interface import StateInterface
from mutiny.states.reveal import resolve_reveal
from mutiny.states.wait_for_block_response import WaitForBlockResponse
from mutiny.constants import ASSASSINATE_COST

BLOCKING_ROLES = {
    ActionEnum.F_AID: {RoleEnum.DUKE},
    ActionEnum.STEAL: {RoleEnum.AMBASSADOR, RoleEnum.CAPTAIN},
    ActionEnum.ASSASSINATE: {RoleEnum.CONTESSA},
}


class WaitForActionResponse(StateInterface):

    def __init__(self, *,
                 data: GameData,
                 action: QueuedAction):
        super().__init__(data=data)
        self._action = action
        self._allow = [False if player.alive else True for player in self._data.players]
        self._allow[self._data.player_turn] = True

    @property
    def state_name(self) -> StateEnum:
        return StateEnum.WAIT_FOR_ACTION_RESPONSE

    @property
    def queued_action(self) -> QueuedAction:
        return self._action

    @property
    def target(self) -> int:
        return self._action.target

    def to_dict(self, player_id=None) -> Dict:
        d = super().to_dict(player_id)
        d["state"]["action"] = self._action.action_name.value
        if self._action.target is not None:
            d["state"]["target"] = self._action.target
        return d

    def error_on_noop(self, player_id: int) -> Union[None, str]:
        if not self._allow[player_id]:
            return f"Player {player_id} must allow, block, or challenge on {self.state_name}"
        return None        

    def noop(self, player_id: int) -> StateInterface:
        # If player has not already implicitly allowed
        if (error := self.error_on_noop(player_id)):
            raise InvalidMove(error)
        return self

    def error_on_challenge(self, player_id: int) -> Union[None, str]:
        if self._allow[player_id]:
            return "Player has already or implicitly allowed the action"
        if not self._action.can_be_challenged:
            return "Current action can not be challenged"
        return None

    def challenge(self, player_id: int) -> StateInterface:
        if (error := self.error_on_challenge(player_id)):
            raise InvalidMove(error)

        if self._data.players[self._data.player_turn].hasAliveInfluence(self._action.action_role):
            self._data.deck.append(self._action.action_role)
            self._data.shuffle_deck()
            self._data.players[self._data.player_turn].replace(self._action.action_role, self._data.deck.pop())

            # Challenger loses an influence, action may or may not resolve
            return resolve_reveal(data=self._data,
                                  player_id=player_id,
                                  action=self._action,
                                  query_block_next=True)
        else:
            # Claimant loses an influence, action does not resolve (except for the initial cost)
            if isinstance(self._action, Assassinate):
                self._data.active_player.addCash(ASSASSINATE_COST)
            return resolve_reveal(data=self._data,
                                  player_id=self._data.player_turn,
                                  action=NoOp(self._data))

    def error_on_block(self, player_id: int, blocking_role: RoleEnum) -> Union[None, str]:
        # Note this is twice duplicated code :) im sorry
        if not self._action.can_be_blocked:
            return "Current action can not be blocked"
        if self._allow[player_id]:
            return "Player has already or implicitly allowed the action"
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
            return "Player has already or implicitly allowed the action"
        return None

    def allow(self, player_id: int) -> StateInterface:
        if (error := self.error_on_allow(player_id)):
            raise InvalidMove(error)

        # No one has challenged or blocked, so the action resolves
        # Blocks are done on this turn, unless a challenge occurs
        self._allow[player_id] = True
        if all(self._allow): return self._action.resolve()
        return self

