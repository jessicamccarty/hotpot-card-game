# Define the card type and category / ingredient data.

from dataclasses import dataclass

# Hotpot uses 8 categories with 3 ingredients each

CATEGORIES = {
    "Noodles": ["RamenNoodles", "HangingNoodles", "RolledNoodles"],
    "Seafood": ["Fish", "LobsterClaw", "Shrimp"],
    "Greens": ["BokChoy", "NapaCabbage", "GreenOnion"],
    "Spices": ["Garlic", "HeatRoot", "DariClove"],
    "Veggies": ["Corn", "Potato", "Carrot"],
    "Meat": ["BeefRolls", "SlicedMeat", "SernukSteak"],
    "Mushrooms": ["Brighshroom", "Morel", "Enoki"],
    "Carbs": ["Dumpling", "Tofu", "RiceCake"],
}

@dataclass(frozen=True)
class Card:
    category: str
    ingredient: str

    def id_tuple(self):
        # For sorting and search. Will return a tuple (category, ingredient).
        return self.category, self.ingredient

    def __str__(self):
        return f"{self.ingredient} [{self.category}]"