import asyncio
from typing import Tuple
import argparse
import treys
import time
from collections import defaultdict
from tg.bot import Bot
import tg.types as pokerTypes
from . import eval_hand_strength

parser = argparse.ArgumentParser(
    prog="Template bot",
    description="A Turing Games poker bot that always checks or calls, no matter what the target bet is (it never folds and it never raises)",
)

parser.add_argument("--port", type=int, help="The port to connect to the server on")
parser.add_argument(
    "--host", type=str, default="localhost", help="The host to connect to the server on"
)
parser.add_argument(
    "--room", type=str, default="my-new-room", help="The room to connect to"
)
parser.add_argument("--party", type=str, default="poker", help="The room to connect to")
parser.add_argument("--key", type=str, default="", help="The key for authentication")
parser.add_argument("--simulations", type=int, default=900)

args = parser.parse_args()


def card_name(card: pokerTypes.Card):
    val = str(card.rank)
    if card.rank == 1:
        val = "A"
    if card.rank == 10:
        val = "T"
    elif card.rank == 11:
        val = "J"
    elif card.rank == 12:
        val = "Q"
    elif card.rank == 13:
        val = "K"
    return f"{val}{card.suit[0]}"


percentile_to_hands = defaultdict(list)
for hand, percentile in eval_hand_strength.poker_hand_percentiles.items():
    percentile_to_hands[percentile].append(hand)
sorted_percentiles = sorted(percentile_to_hands.keys())


class max_eric_bot(Bot):
    fold_ = 0
    preflop_fold_ = 4
    call_ = 0
    raise_ = 0
    check_ = 0
    total_ = 0
    isFirstMove = True
    round_count = 4
    villain_tolerance = 25
    raised = False
    rank_map = {
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
        8: "8",
        9: "9",
        10: "10",
        11: "J",
        12: "Q",
        13: "K",
        1: "A",
    }

    def act(self, state, hand):
        # check if rased and if big blind during pre-flop
        if self.last_target_bet == state.target_bet and state.round == "pre-flop":
            self.raised = False
            return {"type": "call"}
        if not (self.raised):
            return {"type": "call"}

        # parsing board into [('A', 'Diamond'), ('K', 'Diamond')] format into board_cards
        board_cards = []
        for card in state.cards:
            board_cards.append((self.rank_map[card.rank], card.suit.capitalize()))
        # hand_cards formatted in the same way
        hand_cards = [
            (self.rank_map[hand[0].rank], hand[0].suit.capitalize()),
            (self.rank_map[hand[1].rank], hand[1].suit.capitalize()),
        ]

        # print('asked to act')
        # print('acting', state, hand, self.my_id)
        p = self.win_prob(state, hand)
        EV_Call = p * (state.pot + state.target_bet) - (state.target_bet) * (1 - p)
        pot_odds = self.pot_odds(state, p)

        # TODO: Not sure how you guys want to implement this but here's pot odds
        action = "fold" if pot_odds < 0 else "call"

        best_val = min(0, EV_Call)
        action = "fold" if best_val == 0 else "call"
        hands = self.get_hands_in_percentile_range(self.preflop_fold_rate())
        print(hands, self.preflop_fold_rate())
        print(len(eval_hand_strength.parse_all_hands(hands)))
        self.raised = False
        return {"type": action}

    def opponent_action(self, action, player):
        if action.type == "fold":
            self.fold_ += 1
        elif action.type == "call":
            self.call_ += 1
        elif action.type == "raise":
            self.raised = True
            self.raise_ += 1
        if self.isFirstMove:
            self.isFirstMove = False
            if action.type == "fold":
                self.preflop_fold_ += 1
        print("opponent action?", action, player)

    def game_over(self, payouts):
        print("game over", payouts)

    def start_game(self, my_id):
        self.my_id = my_id
        print("start game", my_id)
        self.isFirstMove = True
        self.round_count += 1

    def win_prob(
        self,
        state: pokerTypes.PokerSharedState,
        hand: Tuple[pokerTypes.Card, pokerTypes.Card],
    ):
        out = 0
        hand = [treys.Card.new(card_name(hand[0])), treys.Card.new(card_name(hand[1]))]
        board = [treys.Card.new(card_name(card)) for card in state.cards]
        evaluator = treys.Evaluator()
        for i in range(args.simulations):
            deck = treys.Deck()
            deck.shuffle()
            for card in hand + board:
                deck.cards.remove(card)
            pred = board + deck.draw(5 - len(board))
            score = evaluator.evaluate(hand, pred)
            other = 10**9

            for player in state.players:
                if player.id != self.my_id:
                    other = min(other, evaluator.evaluate(deck.draw(2), pred))
            if score < other:
                out += 1
        return out / args.simulations

    def pot_odds(self, state: pokerTypes.PokerSharedState, ev: float) -> float:
        return (state.pot + state.target_bet) * ev - state.target_bet * (1 - ev)

    def get_hands_in_percentile_range(
        self, max_percentile: int, max_threshold=60
    ) -> list[str]:
        hands = []
        max_percentile = min(max_threshold, max_percentile)
        for percentile in sorted_percentiles:
            if percentile <= max_percentile:
                hands.extend(percentile_to_hands[percentile])
        return hands

    def get_player_max_percentile(self, player_id: str) -> int:
        return self.fold_.get(player_id, 15) / self.round_count

    def preflop_fold_rate(self):
      return (1-(self.preflop_fold_ / self.round_count)) * 100