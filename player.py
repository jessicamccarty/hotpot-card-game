# Define Player class and include hand management, insertion sort for the hand, binary search on a sorted hand, set detection and scoring

from __future__ import annotations
from typing import List
from card import Card, CATEGORIES


class Player:
    def __init__(self, name: str, is_human: bool = False) -> None:
        self.name = name
        self.is_human = is_human
        self.hand: List[Card] = []
        self.discard_pile: List[Card] = []
        # Each set is (set_type, [Card, Card, Card])
        self.completed_sets: List[Tuple[str, List[Card]]] = []
        self.score: int=0


    # Basic Hand Operations




    # Sorting using insertion sort





    # Searching using binary search



    # Detect sets and score