from actions import QueuedAction
from game_enum import ActionEnum, StateEnum, RoleEnum
from game_state import GameState
from state_interface import StateInterface
from exceptions import InvalidMove

from states.wait_block_challenge import WaitBlockChallenge

# TODO: Probably should be moved into actions logic somehow
BLOCKING_ROLES = {
    ActionEnum.F_AID: {RoleEnum.DUKE},
    ActionEnum.STEAL: {RoleEnum.AMBASSADOR, RoleEnum.CAPTAIN},
    ActionEnum.ASSASSINATE: {RoleEnum.CONTESSA},
}


class WaitBlock(StateInterface):
    """
    Only accessible after a failed action challenge.
    """

    def __init__(self, state: GameState, action: QueuedAction):
        super().__init__(state)
        self._action = action
        self._allow = [False if player.alive else True for player in self._state.players]
        self._allow[self._state.player_turn] = True

    @property
    def state_name(self) -> StateEnum:
        return StateEnum.WAIT_BLOCK

    def block(self, player_id: int, blocking_role: RoleEnum) -> StateInterface:
        if self._allow[player_id]:
            raise InvalidMove("Player has already implicitly allowed the action")
        if blocking_role not in BLOCKING_ROLES[self._action.action_name]:
            raise InvalidMove("Cannot block {} with {}".format(self._action.action_name, blocking_role))
        if blocking_role != RoleEnum.DUKE and player_id != self._action.target:
            raise InvalidMove("Cannot block if you are not the target")

        return WaitBlockChallenge(self._state, self._action, player_id, blocking_role)

    def allow(self, player_id: int) -> StateInterface:
        if self._allow[player_id]:
            raise InvalidMove("Player has already implicitly allowed the action")
        self._allow[player_id] = True

        if all(self._allow): return self._action.resolve()
        return self
