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

