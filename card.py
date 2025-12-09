# Define the card type and category / ingredient data.

from dataclasses import dataclass



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


# added emoji for easier grouping in text based system
CATEGORY_EMOJI = {
    "Noodles": "🍜",
    "Seafood": "🦞",
    "Greens": "🥬",
    "Spices": "🌶️",
    "Veggies": "🥕",
    "Meat": "🥩",
    "Mushrooms": "🍄",
    "Carbs": "🥟",
}

# added color coding for easier grouping in text based system
def red(t): return f"\033[91m{t}\033[0m"
def green(t): return f"\033[92m{t}\033[0m"
def yellow(t): return f"\033[93m{t}\033[0m"
def blue(t): return f"\033[94m{t}\033[0m"
def magenta(t): return f"\033[95m{t}\033[0m"
def cyan(t): return f"\033[96m{t}\033[0m"
def white(t): return f"\033[97m{t}\033[0m"

CATEGORY_COLORS = {
    "Noodles": yellow,
    "Seafood": cyan,
    "Greens": green,
    "Spices": red,
    "Veggies": magenta,
    "Meat": blue,
    "Mushrooms": white,
    "Carbs": yellow,
}



@dataclass(frozen=True)
class Card:
    category: str
    ingredient: str

    def id_tuple(self):
        return self.category, self.ingredient

    def __str__(self):
        emoji = CATEGORY_EMOJI.get(self.category, "")
        color = CATEGORY_COLORS.get(self.category, white)
        return color(f"{emoji} {self.ingredient}")
