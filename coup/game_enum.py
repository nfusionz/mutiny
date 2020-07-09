from enum import Enum


class ActionEnum(Enum):
    TAX = "tax"
    STEAL = "steal"
    ASSASSINATE = "assassinate"
    EXCHANGE = "exchange"
    INCOME = "income"
    F_AID = "foreign-aid"
    COUP = "coup"
    NOP = "nop"  # Not typically available to user.


class RoleEnum(Enum):
    DUKE = "duke"
    CAPTAIN = "captain"
    ASSASSIN = "assassin"
    CONTESSA = "contessa"
    AMBASSADOR = "ambassador"


class StateEnum(Enum):
    START_TURN = "start-of-turn"  # Player turn given by playerIdx
    WAIT_FOR_ACTION_RESPONSE = "action-response"  # Waiting for challenge
    WAIT_FOR_BLOCK = "final-action-response"
    WAIT_FOR_BLOCK_RESPONSE = "block-response"  # Waiting for challenge to target's response
    REVEAL = "reveal-influence"  # See playerToReveal
    EXCHANGE = "exchange"  # playerIdx chooses card to pick
