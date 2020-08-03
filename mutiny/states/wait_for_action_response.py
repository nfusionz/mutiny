from typing import Dict

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

    def noop(self, player_id: int) -> StateInterface:
        # If player has not already implicitly allowed
        if not self._allow[player_id]:
            raise InvalidMove(f"Player {player_id} must allow, block, or challenge on {self.state_name}")
        return self

    def to_dict(self, player_id=None) -> Dict:
        d = super().to_dict(player_id)
        d["state"]["action"] = self._action.action_name.value
        if self._action.target is not None:
            d["state"]["target"] = self._action.target
        return d

    def can_challenge(self, player_id: int) -> bool:
        if self._allow[player_id]:
            return False
        if not self._action.can_be_challenged:
            return False
        return True

    def challenge(self, player_id: int) -> StateInterface:
        if self._allow[player_id]:
            raise InvalidMove("Player has implicitly allowed the action")
        if not self._action.can_be_challenged:
            raise InvalidMove("Current action can not be challenged")

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

    def can_block(self, player_id: int, blocking_role: RoleEnum) -> bool:
        # Note this is twice duplicated code :) im sorry
        if not self._action.can_be_blocked:
            return False
        if self._allow[player_id]:
            return False
        if blocking_role not in BLOCKING_ROLES[self._action.action_name]:
            return False
        if blocking_role != RoleEnum.DUKE and player_id != self._action.target:
            return False
        return True

    def block(self, player_id: int, blocking_role: RoleEnum) -> StateInterface:
        if not self._action.can_be_blocked:
            raise InvalidMove("Current action can not be blocked")

        # Note this is duplicated code
        if self._allow[player_id]:
            raise InvalidMove("Player has already implicitly allowed the action")
        if blocking_role not in BLOCKING_ROLES[self._action.action_name]:
            raise InvalidMove("Cannot block {} with {}".format(self._action.action_name, blocking_role))
        if blocking_role != RoleEnum.DUKE and player_id != self._action.target:
            raise InvalidMove("Cannot block if you are not the target")

        return WaitForBlockResponse(data=self._data,
                                    action=self._action,
                                    blocker_id=player_id,
                                    block_role=blocking_role)

    def can_allow(self, player_id: int) -> bool:
        return not self._allow[player_id]

    def allow(self, player_id: int) -> StateInterface:
        if self._allow[player_id]:
            raise InvalidMove("Player has already implicitly allowed the action")
        self._allow[player_id] = True

        # No one has challenged or blocked, so the action resolves
        # Blocks are done on this turn, unless a challenge occurs
        if all(self._allow): return self._action.resolve()
        return self

