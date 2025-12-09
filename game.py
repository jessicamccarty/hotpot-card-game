from __future__ import annotations

import random
from typing import List
from deck import Deck
from player import Player

# ---------------- COLOR HELPERS ----------------
def red(text): return f"\033[91m{text}\033[0m"
def green(text): return f"\033[92m{text}\033[0m"
def yellow(text): return f"\033[93m{text}\033[0m"
def blue(text): return f"\033[94m{text}\033[0m"
def magenta(text): return f"\033[95m{text}\033[0m"
def cyan(text): return f"\033[96m{text}\033[0m"
def bold(text): return f"\033[1m{text}\033[0m"

WINNING_SETS = 3  # First player to complete 3 sets wins


class Game:
    def __init__(self, human_count: int) -> None:
        if human_count < 1 or human_count > 4:
            raise ValueError("human_count must be between 1 and 4.")

        self.deck = Deck()
        self.players: List[Player] = []

        for i in range(1, human_count + 1):
            self.players.append(Player(f"Player {i}", is_human=True))

        ai_needed = 4 - human_count
        for i in range(1, ai_needed + 1):
            self.players.append(Player(f"Computer {i}", is_human=False))

        self.current_player_index: int = 0
        self._pending_winner: Player | None = None

    # Setup player hands
    def deal_initial_hands(self, cards_per_player: int = 8) -> None:
        for _ in range(cards_per_player):
            for player in self.players:
                card = self.deck.draw()
                if card:
                    player.add_card(card)

        for player in self.players:
            player.sort_hand()

    # ------------------------------------------------------------
    # Main Game Loop
    # ------------------------------------------------------------
    def play(self) -> None:
        print(bold(magenta("Welcome to the Hotpot minigame!")))
        print("The first player to complete 3 sets of 3 cards wins.")
        print("Up to 4 players may play; others are computer controlled.")
        print("Type 'q' on your turn to quit.\n")

        self.deal_initial_hands()

        winner: Player | None = None

        while not winner and self.deck.remaining() > 0:

            # Did someone just win on their draw?
            if self._pending_winner is not None:
                winner = self._pending_winner
                break

            current = self.players[self.current_player_index]
            self._print_table_state(current)

            if current.is_human:
                quit_game = self._human_turn(current)
                if quit_game:
                    print(f"{current.name} has quit the game.")
                    return
            else:
                self._computer_turn(current)

            # Check if a player won during their turn
            if self._pending_winner is not None:
                winner = self._pending_winner
                break

            # End-of-turn set check (kept for safety)
            current.sort_hand()
            sets_found = current.find_sets_in_hand()

            if len(sets_found) >= WINNING_SETS:
                winner = current
                break

            # Rotate turn
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

        self._print_final_results(winner)

    # ------------------------------------------------------------
    # Printing the table state
    # ------------------------------------------------------------
    def _print_table_state(self, current: Player) -> None:
        print(bold(magenta("=" * 60)))
        print(bold(yellow(f"Current Turn: {current.name}")))
        print(f"Deck has {self.deck.remaining()} cards remaining.\n")

        for player in self.players:
            top = player.top_discard()

            if player.is_human:
                print(bold(green(f"{player.name} (HUMAN)")))
                print(f"Hand size: {player.hand_size()}, Sets: {player.sets_count()}, Score: {player.score}")
                print(cyan("Hand:"))
                print(player.describe_hand())
                print(cyan("\nSets:"))
                print(player.describe_sets())
            else:
                print(bold(blue(f"{player.name} (AI)")))
                print(f"Hand size: {player.hand_size()}, Sets: {player.sets_count()}, Score: {player.score}")
                if top:
                    print(f"Top discard: {yellow(str(top))}")
                else:
                    print("No discards yet.")

            print(magenta("-" * 60))

    # ------------------------------------------------------------
    # Human turn logic
    # ------------------------------------------------------------
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

        # ---------------- DRAW LOOP ----------------
        while True:
            choice = input("Choose where to draw from: ").strip().lower()

            if choice == "q":
                return True

            if choice == "1":
                drawn = self.deck.draw()
                if drawn:
                    print(green(f"You drew: {drawn}"))
                    player.add_card(drawn)
                else:
                    print(red("The deck is empty."))

                # IMMEDIATE WIN CHECK AFTER DRAW
                player.sort_hand()
                sets_found = player.find_sets_in_hand()
                if len(sets_found) >= WINNING_SETS:
                    self._pending_winner = player
                    return False

                break

            if choice.isdigit():
                num = int(choice)
                if num in discard_options:
                    opponent = discard_options[num]
                    card = player.take_from_discard(opponent)
                    print(green(f"You took: {card} from {opponent.name}"))

                    # WIN CHECK AFTER DRAW
                    player.sort_hand()
                    sets_found = player.find_sets_in_hand()
                    if len(sets_found) >= WINNING_SETS:
                        self._pending_winner = player
                        return False

                    break

            print(red("Invalid choice, try again."))

        # ---------------- DISCARD SECTION ----------------
        if player.hand_size() == 0:
            print("Your hand is empty. Nothing to discard.")
            return False

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
                    print(red(f"You discard: {removed}"))
                    break
            print(red("Invalid index."))

        input("Press Enter to end your turn...")
        return False

    # ------------------------------------------------------------
    # AI Turn Logic
    # ------------------------------------------------------------
    def _computer_turn(self, player: Player) -> None:
        print(blue(f"{player.name} is taking a turn..."))

        steal_candidates = [p for p in self.players if p is not player and p.top_discard()]

        if steal_candidates and random.random() < 0.4:
            opponent = random.choice(steal_candidates)
            card = player.take_from_discard(opponent)
            print(blue(f"{player.name} takes from {opponent.name}'s discard: {card}"))
        else:
            card = self.deck.draw()
            if card:
                player.add_card(card)
                print(blue(f"{player.name} draws from deck."))
            else:
                print(red(f"{player.name} cannot draw; deck empty."))

        # IMMEDIATE WIN CHECK
        player.sort_hand()
        sets_found = player.find_sets_in_hand()
        if len(sets_found) >= WINNING_SETS:
            self._pending_winner = player
            return

        # AI discards random card
        if player.hand_size() > 0:
            idx = random.randrange(player.hand_size())
            removed = player.discard_card_by_index(idx)
            print(red(f"{player.name} discards: {removed}"))

    # ------------------------------------------------------------
    # End game results
    # ------------------------------------------------------------
    def _print_final_results(self, winner: Player | None) -> None:
        print("\n" + bold(magenta("=" * 60)))
        print(bold("Game over!"))

        for p in self.players:
            print(f"{p.name} - sets: {p.sets_count()}, score: {p.score}, "
                  f"hand size: {p.hand_size()}")

        if winner is None:
            print(red("No one reached 3 sets before deck exhaustion. Draw."))
        else:
            print(green(f"{winner.name} WINS the game!"))

        print(bold(magenta("=" * 60)))
