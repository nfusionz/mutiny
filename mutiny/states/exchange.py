from typing import Tuple, Dict, Union

import mutiny.actions
from mutiny.player import Influence
from mutiny.game_enum import StateEnum, ActionEnum, RoleEnum
from mutiny.game_data import GameData
from mutiny.state_interface import StateInterface
from mutiny.exceptions import InvalidMove


class Exchange(StateInterface):
    """
    Exchange state: only valid thing to happen is for the player whose turn it is to exchange their cards
    """

    def __init__(self, *,
                 data: GameData,
                 exchange_options: Tuple[RoleEnum, RoleEnum]):
        super().__init__(data=data)
        self.exchange_options = exchange_options

    @property
    def state_name(self) -> StateEnum:
        return StateEnum.EXCHANGE

    def to_dict(self, player_id=None) -> Dict:
        d = super().to_dict(player_id)
        d["state"]["action"] = ActionEnum.EXCHANGE.value
        if player_id in [None, self._data.player_turn]:
            d["state"]["exchangeOptions"] = [o.value for o in self.exchange_options] + [o.role.value for o in self._data.active_player.hand if not o.revealed]
        return d

    def noop(self, player_id: int) -> StateInterface:
        if player_id == self._data.player_turn:
            raise InvalidMove(f"Player {player_id} must replace on {self.state_name}")
        return self

    def replace(self, player_id: int, influences: Tuple[RoleEnum, Union[RoleEnum]]) -> StateInterface:
        if player_id != self._data.player_turn:
            raise InvalidMove("Wrong player to exchange")

        player = self._data.active_player

        # check that the player is trying to keep the correct number of cards (maintain influence count)
        cards_to_keep = [role for role in influences]
        if len(cards_to_keep) != player.influence_count:
            raise InvalidMove("Player can only keep as many cards as influence they have.")

        # check influences to keep are valid (in the player's hand or in the player's exchange options)
        cards_can_keep = [influence.role for influence in player.hand if not influence.revealed] + list(self.exchange_options)
        for role in cards_to_keep:
            if role not in cards_can_keep:
                raise InvalidMove("Exchange attempt invalid due to role choice.")
            cards_can_keep.remove(role)

        removed_cards = cards_can_keep # the cards the player chose not to keep

        # do the actual exchange; put the cards in the hand and shuffle the other cards back into the deck
        new_hand = [player.hand[i] for i in range(2)]
        j = len(influences)-1
        for i in range(2):
            if not player.hand[i].revealed:
                new_hand[i] = Influence(influences[j], False)
                j -= 1
        player.hand = tuple(new_hand)

        self._data.deck += removed_cards
        self._data.shuffle_deck()

        return mutiny.actions.NoOp(self._data).resolve()
