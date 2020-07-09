from dataclasses import dataclass
from typing import Tuple, Union, List, Dict
from random import randrange, shuffle

from game_enum import ActionEnum, StateEnum, RoleEnum
from player import Player


@dataclass
class GameState:
    """ Container for state of a game. """
    players: List[Player]
    state_id: int = 0  # Counter for state
    player_turn: int = 0
    deck: Union[List[RoleEnum], None] = None
    winner_id: Union[int, None] = None

    def __iter__(self):
        return self

    def __next__(self):
        """ Probably should not be here. """
        if not self.done:
            for i in range(1, len(self.players)):
                player_id = self.player_turn + i % len(self.players)
                if self.player_alive(player_id):
                    self.player_turn = player_id
                    self.state_id += 1
                    return self
        if self.winner is None:
            self.winner = [i for i, player in enumerate(self.players) if player.influence_count >= 0][0]
            self.state_id += 1
            return self
        raise StopIteration

    def player_alive(self, player_id: int) -> bool:
        return self.players[player_id].influence_count >= 0

    @property
    def players_left(self) -> int:
        return sum(1 for player in self.players if player.influence_count >= 0)

    @property
    def done(self) -> bool:
        return self.players_left == 1

    def to_dict(self, player_id=None) -> Dict:
        """
        Returns a dictionary representing the game state from the perspective of player_id.
        When player_id is None (unspecified), returns the unobfuscated game state (all info).
        """
        d = dict()
        d["stateId"] = self.state_id
        d["players"] = [p.to_dict(player_id) for p in self.players]
        d["playerIdx"] = player_id
        d["numPlayers"] = len(self.players)


    def reset(self) -> None:
        """ Initialize game. """
        self.state_id = 0
        self.player_turn = randrange(len(self.players))
        self.deck = [role for _ in range(3) for role in RoleEnum]
        self.shuffle_deck()

        for player in self.players:
            player.reset()
            player.draw((self.deck.pop(), self.deck.pop()))

    def shuffle_deck(self):
        shuffle(self.deck)
