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
    ASSASIN = "assassin"
    CONTESSA = "contessa"
    AMBASSADOR = "ambassador"


class StateEnum(Enum):
    START_TURN = "start-of-turn"  # Player turn given by playerIdx
    WAIT_CHALLENGE = "action-response"  # Waiting for challenge
    WAIT_BLOCK = "final-action-response"
    WAIT_BLOCK_CHALLENGE = "block-response"  # Waiting for challenge to target's response
    REVEAL = "reveal-influence"  # See playerToReveal
    EXCHANGE = "exchange"  # playerIdx chooses card to pick
