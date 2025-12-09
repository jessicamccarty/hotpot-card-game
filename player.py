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
    
    def add_card(self, card: Card) -> None:
        if card is not None:
            self.hand.append(card)


    def discard_card_by_index(self, index: int) -> Card:
        # Remove the card at the given index from hand and place it on the player's discard pile. Return the discarded card.
        card = self.hand.pop(index)
        self.discard_pile.append(card)
        return card
    

    def top_discard(self) -> Card | None:
        if not self.discard_pile:
            return None
        return self.discard_pile[-1]
    

    def take_from_discard(self, other: "Player") -> Card | None:
        # Take the top card from another player's discard pile. Return None if their pile is empty.
        if not other.discard_pile:
            return None
        card = other.discard_pile.pop()
        self.hand.append(card)
        return card
    
    

    # Sorting using insertion sort

    def sort_hand(self) -> None:
        for i in range(1, len(self.hand)):
            key_card = self.hand[i]
            j = i - 1

            # Compare using card.id_tuple() for order
            while j >= 0 and self.hand[j].id_tuple() > key_card.id_tuple():
                self.hand[j + 1] = self.hand[j]
                j -= 1

            self.hand[j + 1] = key_card


    # Searching using binary search
    
    def has_card_binary_search(self, target: Card) -> bool:
        # Hand must be sorted by sort_hand() first.
        low = 0
        high = len(self.hand) - 1
        target_key = target.id_tuple()

        while low <= high:
            mid = (low + high) // 2
            mid_key = self.hand[mid].id_tuple()

            if mid_key == target_key:
                return True
            elif mid_key < target_key:
                low = mid + 1
            else:
                high = mid - 1
        
        return False

    # Detect sets and score

    def find_sets_in_hand(self):
        # Detect 3 of a kind sets and do not remove any cards. Return a list of sets.
        sets_found = []

        # Group by card identity
        by_exact = {}
        for card in self.hand:
            key = (card.category, card.ingredient)
            by_exact.setdefault(key, []).append(card)

        # Detect 3 of a kind
        for key, cards in by_exact.items():
            if len(cards) >= 3:
                sets_found.append(("three_of_a_kind", cards[:3]))

        # Group by category for cateogry sets
        by_category = {}
        for card in self.hand:
            by_category.setdefault(card.category, {})
            by_category[card.category].setdefault(card.ingredient, 0)
            by_category[card.category][card.ingredient] += 1

        # For each category, see if we have all 3 different ingredients
        from card import CATEGORIES
        for category, ingredients in CATEGORIES.items():
            if category in by_category:
                counts = [by_category[category].get(ing, 0) for ing in ingredients]
                if min(counts) >= 1:
                    # Can form exactly one category set (do NOT remove cards)
                    # Build a 3-card list from the hand
                    set_cards = []
                    for ing in ingredients:
                        for card in self.hand:
                            if card.category == category and card.ingredient == ing:
                                set_cards.append(card)
                                break
                    sets_found.append(("category_set", set_cards))

        return sets_found


    def _extract_three_of_a_kind_sets(self, cards: List[Card]) -> List[Card]:
        groups = {}
        for card in cards:
            key = card.id_tuple()
            groups.setdefault(key, []).append(card)

        remaining: List[Card] = []  # MUST be initialized before loop

        for key, card_list in groups.items():
            count = len(card_list)
            if count >= 3:
                # Take exactly 3 cards for the set
                set_cards = card_list[:3]
                self.completed_sets.append(("three_of_a_kind", set_cards))
                self.score += 120

                # Extra copies (4th card) should remain in the hand
                extra_cards = card_list[3:]
                remaining.extend(extra_cards)
            else:
                # Less than 3, keep all in remaining pool
                remaining.extend(card_list)

        return remaining
    

    def _extract_category_sets(self, cards: List[Card]) -> List[Card]:
        # Group by category then by ingredient
        by_category: dict[str, dict[str, List[Card]]] = {}

        for card in cards: 
            by_category.setdefault(card.category, {})
            by_category[card.category].setdefault(card.ingredient, [])
            by_category[card.category][card.ingredient].append(card)

        remaining: List[Card] = []

        for category, ingredient_dict in by_category.items():
        # Ingredient names from our global definition
            all_ingredients = CATEGORIES[category]

         # Find how many complete sets can be formed limited by the minimum count across each ingredient
            counts = [len(ingredient_dict.get(ing, [])) for ing in all_ingredients]
            possible_sets = min(counts)

            # Form those sets
            for _ in range(possible_sets):
                set_cards: List[Card] = []
                for ing in all_ingredients:
                    set_cards.append(ingredient_dict[ing].pop())
                self.completed_sets.append(("category_set", set_cards))
                self.score += 60

            # Leftover cards stay in the remaining pool
            for ing in all_ingredients:
                remaining.extend(ingredient_dict.get(ing, []))

        return remaining    
    

    # Helpers
    
    def hand_size(self) -> int:
        return len(self.hand)
    

    def sets_count(self) -> int:
        return len(self.completed_sets)
    

    def describe_hand(self) -> str:
        # Create text description for user interface
        if not self.hand:
            return "(empty hand)"
        return ",".join(F"{idx:} {str(card)}" for idx, card in enumerate(self.hand))

    def describe_sets(self) -> str:
        if not self.completed_sets:
             return "No sets yet."
        parts = []
        for idx, (set_type, cards) in enumerate(self.completed_sets, start=1):
            card_text = " | ".join(str(c) for c in cards)
            parts.append(f"Set {idx} [{set_type}]: {card_text}")

        return "\n".join(parts)

