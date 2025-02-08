import asyncio
from typing import Tuple
import argparse
import treys
import time

from tg.bot import Bot
import tg.types as pokerTypes

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


class EV_bot(Bot):
    def act(self, state, hand):
        print("asked to act")
        # print("acting", state, hand, self.my_id)
        print(hand)
        p = self.win_prob(state, hand)
        print(p)
        EV_Call = p * (state.pot + state.target_bet) - (state.target_bet) * (1 - p)
        print(EV_Call)
        best_val = max(0, EV_Call)
        action = "fold" if best_val == 0 else "call"
        return {"type": action}

    def opponent_action(self, action, player):
        print("opponent action?", action, player)

    def game_over(self, payouts):
        print("game over", payouts)

    def start_game(self, my_id):
        self.my_id = my_id
        print("start game", my_id)

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
