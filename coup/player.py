from dataclasses import dataclass
from typing import Tuple, Union, Dict

from exceptions import InvalidMove
from game_enum import RoleEnum
from constants import CASH_LIMIT, CASH_START


@dataclass
class Influence:
    role: RoleEnum
    revealed: bool = False


@dataclass
class Player:
    """
    Model for a player. Keeps track of cash and cards in hand.
    """
    name: str
    self_id: int
    cash: int = CASH_START
    hand: Union[Tuple[Influence, Influence], None] = None

    def reset(self) -> None:
        self.cash = CASH_START
        self.hand = None

    def draw(self, hand: Tuple[RoleEnum, RoleEnum]) -> None:
        if hand is not None:
            raise RuntimeError("{} has already drawn a hand".format(self.name))
        self.hand = (Influence(hand[0]), Influence(hand[1]))

    def addCash(self, cash: int):
        if self.must_coup:
            raise RuntimeError("{} already has {}+ coins".format(self.name, CASH_LIMIT))
        self.cash += cash

    def removeCash(self, cash: int):
        if self.cash < cash:
            raise RuntimeError("{} has less than {} coins".format(self.name, cash))
        self.cash -= cash

    def hasAliveInfluence(self, role: RoleEnum) -> bool:
        if not self.hand[0].revealed and self.hand[0].role == role: return True
        if not self.hand[1].revealed and self.hand[1].role == role: return True
        return False

    def reveal(self, role: Union[RoleEnum, None] = None) -> None:
        """ Reveals left-to-right by default. """
        if not self.hand[0].revealed and (role is None or self.hand[0].role == role):
            self.hand[0].revealed = True
        elif not self.hand[1].revealed and (role is None or self.hand[1].role == role):
            self.hand[1].revealed = True
        else:
            raise RuntimeError("{} does not have {}".format(self.name, role.value))

    def replace(self, initial_role: RoleEnum, replacement_role: RoleEnum):
        if not self.hand[0].revealed and initial_role == self.hand[0].role: self.hand[0].role = replacement_role
        elif not self.hand[1].revealed and initial_role == self.hand[1].role: self.hand[1].role = replacement_role
        else: raise RuntimeError("{} does not have {}".format(self.name, initial_role.value))

    @property
    def must_coup(self) -> bool:
        return self.cash >= CASH_LIMIT

    @property
    def influence_count(self) -> int:
        if self.hand is None:
            raise RuntimeError("No influence to count.")
        return sum(1 for i in self.hand if not i.revealed)

    @property
    def alive(self) -> bool:
        return self.influence_count >= 0

    def to_dict(self, player_id=None) -> Dict:
        """
        Returns a dictionary representing the view of this player from the perspecive of the player with player_id.
        If player_id is self or None, give full information. Otherwise, hide hidden information.
        """
        has_info = player_id in [None, self.self_id]
        d = dict()
        d["name"] = self.name
        d["cash"] = self.cash
        d["influenceCount"] = self.influence_count
        d["influence"] = [
                {
                    "role": inf.role.value if has_info else "unknown",
                    "revealed": inf.revealed
                }
                for inf in self.hand]
        return d
