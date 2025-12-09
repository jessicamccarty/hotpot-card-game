from __future__ import annotations

import random
import time
import sys
from typing import List

from deck import Deck
from player import Player

# Import Winsound for sound effects. Will only work with Windows.
try:
    import winsound
except ImportError:
    winsound = None

# Colors
def red(text): return f"\033[91m{text}\033[0m"
def green(text): return f"\033[92m{text}\033[0m"
def yellow(text): return f"\033[93m{text}\033[0m"
def blue(text): return f"\033[94m{text}\033[0m"
def magenta(text): return f"\033[95m{text}\033[0m"
def cyan(text): return f"\033[96m{text}\033[0m"
def bold(text): return f"\033[1m{text}\033[0m"

WINNING_SETS = 3  # First player to complete 3 sets wins

# Sounds
def play_beep(freq: int, dur: int) -> None:
    if winsound:
        winsound.Beep(freq, dur)

def sound_draw() -> None:
    play_beep(900, 80)

def sound_discard() -> None:
    play_beep(600, 60)

def sound_ai_turn() -> None:
    play_beep(500, 40)

def sound_win_fanfare() -> None:
    # Simple rising triad
    for f, d in [(600, 120), (800, 120), (1000, 180)]:
        play_beep(f, d)
        time.sleep(0.05)

# Animations
def slow_print(text: str, delay: float = 0.03) -> None:
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def animate_deal(player_name: str, card_str: str) -> None:
    slow_print(f"Dealing to {player_name}: {card_str}", delay=0.01)

def animate_turn_start(player_name: str, is_human: bool) -> None:
    icon = "🧑‍🍳" if is_human else "🤖"
    sound_ai_turn()
    slow_print(bold(magenta(f"{icon} {player_name}'s turn begins...")), delay=0.02)
    time.sleep(0.2)

def suspense_animation(message: str = "Revealing winner", steps: int = 4) -> None:
    slow_print(bold(yellow(message)), delay=0.05)
    for i in range(steps):
        slow_print("." * (i + 1), delay=0.15)

def title_banner() -> None:
    border = "🥘" + "─" * 42 + "🥘"
    print(bold(magenta(border)))
    slow_print(bold(yellow("        HOTPOT MINIGAME - TEXT EDITION")), delay=0.04)
    print(bold(magenta(border)))
    print()

def winning_animation(winner_name: str) -> None:
    suspense_animation("Calculating final hotpot results")
    time.sleep(0.3)
    lines = [
        "",
        f"   🎉🎉🎉 {winner_name.upper()} WINS!!! 🎉🎉🎉",
        "",
        "         🏆 HOTPOT CHAMPION 🏆",
        "",
        "   Thank you for playing the Hotpot Minigame!",
        "",
    ]
    for line in lines:
        slow_print(bold(green(line)), delay=0.05)
    sound_win_fanfare()


class Game:
    def __init__(self, human_count: int) -> None:

        if human_count < 1 or human_count > 4:
            raise ValueError("human_count must be between 1 and 4.")

        self.deck = Deck()
        self.players: List[Player] = []
        self._pending_winner: Player | None = None

        # Create human players
        for i in range(1, human_count + 1):
            self.players.append(Player(f"Player {i}", is_human=True))

        # Create AI players
        ai_needed = 4 - human_count
        for i in range(1, ai_needed + 1):
            self.players.append(Player(f"Computer {i}", is_human=False))

        self.current_player_index: int = 0

    # Deal cards with animation
    def deal_initial_hands(self, cards_per_player: int = 8) -> None:
        for _ in range(cards_per_player):
            for player in self.players:
                card = self.deck.draw()
                if card:
                    animate_deal(player.name, str(card))
                    player.add_card(card)

        for player in self.players:
            player.sort_hand()


    # Main Game Loop
    def play(self) -> None:
        title_banner()
        print("The first player to complete 3 sets of 3 cards wins.")
        print("Up to 4 players may play; others are computer controlled.")
        print("Type 'q' on your turn to quit.\n")

        self.deal_initial_hands()
        winner: Player | None = None

        while True:

            current = self.players[self.current_player_index]

            # WIN CHECK (only AFTER a full turn completes)
            if self._pending_winner is not None and current == self._pending_winner:
                winner = current
                break

            # If deck is empty, end game
            if self.deck.remaining() <= 0:
                break

            animate_turn_start(current.name, current.is_human)
            self._print_table_state(current)

            if current.is_human:
                quit_game = self._human_turn(current)
                if quit_game:
                    print(f"{current.name} has quit the game.")
                    return
            else:
                self._computer_turn(current)

            # END OF TURN — check win condition
            if self._pending_winner is not None and self._pending_winner == current:
                winner = current
                break

            # Rotate turn normally
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

        self._print_final_results(winner)


    # Display game state
    def _print_table_state(self, current: Player) -> None:
        print(bold(magenta("🥘" + "─" * 40 + "🥘")))
        print(bold(yellow(f"Current Turn: {current.name}")))
        print(f"Deck has {self.deck.remaining()} cards remaining.\n")

        for player in self.players:
            top = player.top_discard()

            if player.is_human:
                print(bold(green(f"{player.name} (HUMAN)")))
                print(f"Hand size: {player.hand_size()}, Sets: {len(player.find_sets_in_hand())}")
                print(cyan("Hand:"))
                print(player.describe_hand())
                print(cyan("\nSets:"))
                print(player.describe_sets())
            else:
                print(bold(blue(f"{player.name} (AI)")))
                print(f"Hand size: {player.hand_size()}, Sets: {len(player.find_sets_in_hand())}")
                if top:
                    print(f"Top discard: {yellow(str(top))}")
                else:
                    print("No discards yet.")

            print(magenta("─" * 60))

    # Human turn logic
    def _human_turn(self, player: Player) -> bool:
        print(bold("You must first draw one card, then discard one."))

        print(bold(cyan("Draw Options:")))
        print(green("  1 - Draw from the deck"))

        # Build consecutive discard-pile options
        discard_options = {}
        option_num = 2

        for opp in self.players:
            if opp is not player and opp.top_discard():
                discard_options[option_num] = opp
                print(f"  {option_num} - Take from {opp.name}'s discard pile")
                option_num += 1

        print(yellow("  q - Quit game"))

        # DRAW LOOP
        while True:
            choice = input("Choose where to draw from: ").strip().lower()

            if choice == "q":
                return True

            if choice == "1":
                drawn = self.deck.draw()
                if drawn:
                    sound_draw()
                    slow_print(green(f"You drew: {drawn}"), delay=0.02)
                    player.add_card(drawn)
                break

            if choice.isdigit():
                num = int(choice)
                if num in discard_options:
                    opponent = discard_options[num]
                    card = player.take_from_discard(opponent)
                    sound_draw()
                    slow_print(green(f"You took: {card} from {opponent.name}"), delay=0.02)
                    break

            print(red("Invalid choice, try again."))

        # IMMEDIATE WIN CHECK AFTER DRAW
        player.sort_hand()
        sets_found = player.find_sets_in_hand()
        if len(sets_found) >= WINNING_SETS:
            self._pending_winner = player
            return False

        # DISCARD SECTION
        player.sort_hand()
        print(cyan("\nYour updated hand:"))
        print(player.describe_hand())

        while True:
            disc = input("Choose a card index to discard: ").strip().lower()
            if disc == "q":
                return True
            if disc.isdigit():
                idx = int(disc)
                if 0 <= idx < player.hand_size():
                    removed = player.discard_card_by_index(idx)
                    sound_discard()
                    slow_print(red(f"You discard: {removed}"), delay=0.02)
                    break
            print(red("Invalid index."))

        input("Press Enter to end your turn...")
        return False

    # AI Turn Logic
    def _computer_turn(self, player: Player) -> None:
        sound_ai_turn()
        slow_print(blue(f"{player.name} is taking a turn..."), delay=0.02)

        steal_candidates = [p for p in self.players if p is not player and p.top_discard()]

        if steal_candidates and random.random() < 0.4:
            opponent = random.choice(steal_candidates)
            card = player.take_from_discard(opponent)
            sound_draw()
            slow_print(blue(f"{player.name} takes from {opponent.name}'s discard: {card}"), delay=0.02)
        else:
            card = self.deck.draw()
            if card:
                sound_draw()
                player.add_card(card)
                slow_print(blue(f"{player.name} draws from deck."), delay=0.02)

        # IMMEDIATE WIN CHECK AFTER DRAW
        player.sort_hand()
        sets_found = player.find_sets_in_hand()
        if len(sets_found) >= WINNING_SETS:
            self._pending_winner = player
            return

        # AI discards random card
        if player.hand_size() > 0:
            idx = random.randrange(player.hand_size())
            removed = player.discard_card_by_index(idx)
            sound_discard()
            slow_print(red(f"{player.name} discards: {removed}"), delay=0.02)

    # End game results
    def _print_final_results(self, winner: Player | None) -> None:
        print("\n" + bold(magenta("🥘" + "═" * 40 + "🥘")))
        print(bold("Game over!\n"))

        # Recalculate sets logically at the end
        for p in self.players:
            final_sets = p.find_sets_in_hand()
            print(f"{p.name} - sets: {len(final_sets)}, hand size: {p.hand_size()}")

        if winner is None:
            print(red("No one reached 3 sets before deck exhaustion. Draw."))
        else:
            winning_animation(winner.name)

        print(bold(magenta("🥘" + "═" * 40 + "🥘")))
