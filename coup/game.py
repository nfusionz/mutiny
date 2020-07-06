from dataclasses import dataclass
from typing import List, Tuple, Union
from random import randrange, shuffle

from exceptions import InvalidMove
from game_enum import ActionEnum, RoleEnum, StateEnum
from player import Player

TARGETABLE_ACTIONS = {
    ActionEnum.ASSASSINATE,
    ActionEnum.STEAL,
    ActionEnum.COUP
}

CHALLENGEABLE_STATES = {
    StateEnum.WAIT_CHALLENGE,
    StateEnum.WAIT_BLOCK_CHALLENGE
}

ACTION_TO_CARD = {
    ActionEnum.ASSASSINATE: RoleEnum.ASSASIN,
    ActionEnum.EXCHANGE: RoleEnum.AMBASSADOR,
    ActionEnum.STEAL: RoleEnum.CAPTAIN,
    ActionEnum.TAX: RoleEnum.DUKE
}

# a_wait_challenge = All challenge
# - If successful, remove resolve, add reveal (if there is choice)
# - If failure, add reveal (if there is choice)
# wait_challenge = normal challenge
# - If successful, add reveal (if there is choice)
#   - Note: If player gone, do not resolve
ACTION_STACK = {
    ActionEnum.INCOME: ["resolve"],
    ActionEnum.F_AID: ["resolve", "wait_block"],
    ActionEnum.TAX: ["resolve", "a_wait_challenge"],
    ActionEnum.STEAL: ["resolve", "wait_block", "a_wait_challenge"],
    ActionEnum.ASSASSINATE: ["resolve", "wait_block", "a_wait_challenge"],
    ActionEnum.COUP: ["resolve"],
    ActionEnum.EXCHANGE: ["resolve", "a_wait_challenge"]
}

@dataclass
class Game:
    """
    Model for game state.
    """

    def action(self,
               player_idx: int,
               action: ActionEnum,
               target_idx: Union[int, None] = None) -> None:
        if self.state != StateEnum.START_TURN or player_idx != self.player_turn:
            raise InvalidMove("It is not {}'s turn".format(self.players[player_idx].name))

        player = self.players[player_idx]
        if action in TARGETABLE_ACTIONS:
            if target_idx is None: raise InvalidMove("No target specified")
            if target_idx == player_idx: raise InvalidMove("Cannot target yourself")

            target = self.players[target_idx]
            if target.influence_count == 0: raise InvalidMove("Invalid target")

            if action == ActionEnum.ASSASSINATE:
                if player.must_coup: raise InvalidMove("{} must coup".format(player.name))

                player.removeCash(ASSASSINATE_COST)
                # Make sure that action is valid before modifying state
                self.current_action = ActionEnum.ASSASSINATE
                self.target = target
                self.state = StateEnum.WAIT_CHALLENGE
            elif action == ActionEnum.COUP:
                player.removeCash(COUP_COST)

                self.current_action = ActionEnum.COUP
                self.reveal_target = target
                self.state = StateEnum.REVEAL
            elif action == ActionEnum.STEAL:
                if player.must_coup: raise InvalidMove("{} must coup".format(player.name))
                if target.cash == 0: raise InvalidMove("Steal target has no cash to steal")

                self.current_action = ActionEnum.STEAL
                self.target = target
                self.state = StateEnum.WAIT_CHALLENGE
            else:
                raise RuntimeError("Not a valid move. Programmer error.")
        else:
            if player.must_coup: raise InvalidMove("{} must coup".format(player.name))
            if target_idx is not None: raise InvalidMove("Cannot target a player")

            if action == ActionEnum.INCOME:
                player.addCash(INCOME_GAIN)
                self._next()
            elif action == ActionEnum.F_AID:
                self.current_action = ActionEnum.F_AID
                self.state = StateEnum.WAIT_BLOCK
            elif action == ActionEnum.TAX:
                self.current_action = ActionEnum.TAX
                self.state = StateEnum.WAIT_CHALLENGE
            elif action == ActionEnum.EXCHANGE:
                self.current_action = ActionEnum.EXCHANGE
                self.state = StateEnum.WAIT_CHALLENGE
            else:
                raise RuntimeError("Not a valid move. Programmer error.")
        self.stateId += 1

    def challenge(self, player_idx: int) -> None:
        if self.state not in CHALLENGEABLE_STATES:
            raise InvalidMove("Cannot challenge now")
        challenger = self.players[player_idx]
        if challenger.influence_count == 0:
            raise RuntimeError("Challenger is already out of the game.")

        if self.state == StateEnum.WAIT_CHALLENGE:
            if self.current_action not in ACTION_TO_CARD:
                raise RuntimeError("Invalid action to challenge. Programmer error.")

            # While the ability to choose cards is in the rules, Treason does not implement this.
            
    
