from actions import NoOp
from game_enum import StateEnum, RoleEnum
from game_state import GameState
from state_interface import StateInterface
from exceptions import InvalidMove

class Exchange(StateInterface):
    """
    Exchange state: only valid thing to happen is for the player whose turn it is to exchange their cards
    """

    def __init__(self,
                 state: GameState,
                 exchange_options: Tuple[RoleEnum, RoleEnum]):
        super().__init__(state)
        self.exchange_options = exchange_options

    @property
    def state_name(self) -> StateEnum:
        return StateEnum.EXCHANGE

    def replace(self, player_id: int, influences: Tuple[RoleEnum, Union[RoleEnum, None]]) -> StateInterface:
        if player_id != self._state.player_turn:
            raise InvalidMove("Wrong player to exchange")

        player = self.state.players[player_id]

        # check that the player is trying to keep the correct number of cards (maintain influence count)
        cards_to_keep = [role for role in influences if role]
        if len(cards_to_keep) != player.influence_count():
            raise InvalidMove("Player can only keep as many cards as influence they have.")

        # check influences to keep are valid (in the player's hand or in the player's exchange options)
        cards_can_keep = [influence.role for influence in player.hand[player_id] if not influence.revealed] + list(self.exchange_options)
        for role in cards_to_keep:
            if role not in cards_can_keep:
                raise InvalidMode("Exchange attempt invalid due to role choice.")
            cards_can_keep.remove(role)

        removed_cards = cards_can_keep # the cards the player chose not to keep

        # do the actual exchange; put the cards in the hand and shuffle the other cards back into the deck
        j = 0
        for i in range(len(player.influence_count)):
            if not player.hand[i].revealed:
                player.hand[i] = influences[j]
                j += 1

        self._state.deck += removed_cards
        self._state.shuffle_deck()

        return NoOp(self._state).resolve()

