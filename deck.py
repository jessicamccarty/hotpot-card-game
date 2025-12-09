# Define the Deck class and implement the Fisher-Yates shuffle

import random
from typing import List
from card import Card, CATEGORIES

class Deck:
    # 8 categories x 3 ingredients x 4 copies = 96 card deck

    def __init__(self) -> None:
        self.cards: List[Card] = []
        self._build_deck()
        self.fisher_yates_shuffle()

    
    def _build_deck(self) -> None:
        self.cards.clear()

        for category, ingredients in CATEGORIES.items():
            for ingredient in ingredients:
                for _ in range(4):
                    self.cards.append(Card(category, ingredient))


    def fisher_yates_shuffle(self) -> None:
        # Algorithm runs in O(n) time and produces a uniform random permutation

        n = len(self.cards)
        for i in range( n - 1, 0, -1):
            j = random.randint(0, i)
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]

    

    def draw(self) -> Card | None:
        # Will draw top card from the deck. Return None if no cards remain in the deck.

        if not self.cards:
            return None
        return self.cards.pop()
    

    def remaining(self) -> int:
        return len(self.cards)