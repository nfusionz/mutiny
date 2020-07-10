from dataclasses import dataclass
from typing import List, Tuple, Union
from random import randrange, shuffle

from mutiny.exceptions import InvalidMove
from mutiny.game_enum import ActionEnum, RoleEnum, StateEnum
from mutiny.player import Player

TARGETABLE_ACTIONS = {
    ActionEnum.ASSASSINATE,
    ActionEnum.STEAL,
    ActionEnum.COUP
}

CHALLENGEABLE_STATES = {
    StateEnum.WAIT_FOR_ACTION_RESPONSE,
    StateEnum.WAIT_FOR_BLOCK_RESPONSE
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

