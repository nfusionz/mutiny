from typing import Dict, Union, Optional

from mutiny.game_enum import StateEnum, RoleEnum
from mutiny.game_data import GameData
from mutiny.actions import QueuedAction, NoOp
from mutiny.state_interface import StateInterface
from mutiny.exceptions import InvalidMove

import mutiny.states.player_turn
import mutiny.states.reveal


class WaitForBlockResponse(StateInterface):

    def __init__(self, *,
                 data: GameData,
                 action: QueuedAction,
                 blocker_id: int,
                 block_role: RoleEnum):
        super().__init__(data=data)
        self._action = action
        self._allow = [False if player.alive else True for player in self._data.players]
        self._allow[blocker_id] = True

        self._blocker_id = blocker_id
        self._block_role = block_role

    @property
    def state_name(self) -> StateEnum:
        return StateEnum.WAIT_FOR_BLOCK_RESPONSE

    @property
    def queued_action(self) -> QueuedAction:
        return self._action

    @property
    def target(self) -> int:
        return self._blocker_id

    @property
    def blocking_role(self) -> Optional[RoleEnum]:
        return self._block_role

    def to_dict(self, player_id=None) -> Dict:
        d = super().to_dict(player_id)
        d["state"]["action"] = self._action.action_name.value
        # person in the target field is necessarily the blocker
        d["state"]["target"] = self._blocker_id
        d["state"]["blockingRole"] = self._block_role.value
        return d

    def error_on_noop(self, player_id: int) -> Union[None, str]:
        if not self._allow[player_id]:
            return f"Player {player_id} must allow or challenge on {self.state_name}"
        return None

    def noop(self, player_id: int) -> StateInterface:
        # If player has not already implicitly allowed
        if (error := self.error_on_noop(player_id)):
            raise InvalidMove(error)
        return self

    def error_on_challenge(self, player_id: int) -> Union[None, str]:
        if self._allow[player_id]:
            return "Player has already implicitly allowed the block"
        return None

    def challenge(self, player_id: int) -> StateInterface:
        if (error := self.error_on_challenge(player_id)):
            raise InvalidMove(error)

        # this is Treason-specific (you can lie about not having the influence in the og game)
        if self._data.players[self._blocker_id].hasAliveInfluence(self._block_role):
            self._data.deck.append(self._block_role)
            self._data.shuffle_deck()
            self._data.players[self._blocker_id].replace(self._block_role, self._data.deck.pop())

            return mutiny.states.reveal.resolve_reveal(data=self._data,
                                                       player_id=player_id,
                                                       action=NoOp(self._data))
        else:
            return mutiny.states.reveal.resolve_reveal(data=self._data,
                                                       player_id=self._blocker_id,
                                                       action=self._action)

    def error_on_allow(self, player_id: int) -> Union[None, str]:
        # This is an invalid move because the blocker (from the NN) is able to allow his own block
        # Not a runtime error
        if self._allow[player_id]:
            return "Player has already implicitly allowed the block"
        return None

    def allow(self, player_id: int) -> StateInterface:
        if (error := self.error_on_allow(player_id)):
            raise InvalidMove(error)

        self._allow[player_id] = True
        if all(self._allow):
            # Action does not resolve
            return mutiny.states.player_turn.PlayerTurn(data=self._data.next_turn())
        return self
