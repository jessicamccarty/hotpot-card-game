from __future__ import annotations

import random
from typing import List
from deck import Deck
from player import Player

WINNING_SETS = 3  # First player to complete 3 sets wins

class Game:
    def __init__(self, human_count: int) -> None:
        # Create game with N human players and (4 - N) AI opponents.
        if human_count < 1 or human_count > 4:
            raise ValueError("human_count must be between 1 and 4.")

        self.deck = Deck()
        self.players: List[Player] = []
    
        # Create human players
        for i in range(1, human_count + 1):
            self.players.append(Player(f"Player {i}", is_human=True))

        # Create AI players
        ai_needed = 4 - human_count
        for i in range(1, ai_needed + 1):
            self.players.append(Player(f"Computer {i}", is_human=False))

        self.current_player_index: int = 0

    # Setup player hands
    def deal_initial_hands(self, cards_per_player: int = 8) -> None:
        for _ in range(cards_per_player):
            for player in self.players:
                card = self.deck.draw()
                if card:
                    player.add_card(card)

        # Sort opening hands
        for player in self.players:
            player.sort_hand()

    # Main game loop
    def play(self) -> None:
        print("Welcome to the Hotpot minigame!")
        print("The first player to complete 3 sets of 3 cards wins.")
        print("Up to 4 players may play; others are computer controlled.")
        print("Type 'q' on your turn to quit.")

        self.deal_initial_hands()

        winner: Player | None = None

        while not winner and self.deck.remaining() > 0:
            current = self.players[self.current_player_index]
            self._print_table_state(current)

            # FIXED: Prevent humans from running AI logic
            if current.is_human:
                quit_game = self._human_turn(current)
                if quit_game:
                    print(f"{current.name} has quit the game.")
                    return
            else:
                self._computer_turn(current)

            # After drawing and discarding, detect sets
            current.sort_hand()
            sets_found = current.find_sets_in_hand()

            if len(sets_found) >= 3:
                winner = current
                break

            # Rotate turn
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

        self._print_final_results(winner)

    # Turn logic
    def _print_table_state(self, current: Player) -> None:
        print("=" * 60)
        print(f"It is {current.name}'s turn.")
        print(f"Deck has {self.deck.remaining()} cards remaining.\n")

        for player in self.players:
            top = player.top_discard()
            if player.is_human:
                print(f"{player.name} (HUMAN) - hand size: {player.hand_size()}, "
                      f"sets: {player.sets_count()}, score: {player.score}")
                print("Hand:")
                print(player.describe_hand())
                print("\nSets:")
                print(player.describe_sets())
            else:
                print(f"{player.name} (AI) - hand size: {player.hand_size()}, "
                      f"sets: {player.sets_count()}, score: {player.score}")
                if top:
                    print(f"Top discard: {top}")
                else:
                    print("No discards yet.")

            print("-" * 60)

    def _human_turn(self, player: Player) -> bool:
        print("You must first draw one card, then discard one.")
        print("Draw options:")
        print(" 1 - Draw from the deck")

        valid_discard_sources = []

        # Identify available opponent discard piles
        for idx, opp in enumerate(self.players):
            if opp is not player and opp.top_discard():
                print(f" {idx + 2} - Take from {opp.name}'s discard pile")
                valid_discard_sources.append(idx)

        print(" q - Quit game")

        # draw
        while True:
            choice = input("Choose where to draw from: ").strip().lower()

            if choice == "q":
                return True

            if choice == "1":
                drawn = self.deck.draw()
                if drawn:
                    print(f"You drew: {drawn}")
                    player.add_card(drawn)
                else:
                    print("Deck is empty.")
                break

            if choice.isdigit():
                num = int(choice)
                if num >= 2:
                    opp_index = num - 2
                    if opp_index < len(self.players) and opp_index in valid_discard_sources:
                        opponent = self.players[opp_index]
                        card = player.take_from_discard(opponent)
                        print(f"You took: {card} from {opponent.name}")
                        break
            
            print("Invalid choice, try again.")

        # discard
        if player.hand_size() == 0:
            print("Your hand is empty. Nothing to discard.")
            return False

        player.sort_hand()
        print("\nYour updated hand:")
        print(player.describe_hand())

        while True:
            disc = input("Choose a card index to discard: ").strip().lower()
            if disc == "q":
                return True
            if disc.isdigit():
                idx = int(disc)
                if 0 <= idx < player.hand_size():
                    removed = player.discard_card_by_index(idx)
                    print(f"You discard: {removed}")
                    break
            print("Invalid index.")

        input("Press Enter to end your turn...")
        return False
        
    def _computer_turn(self, player: Player) -> None:
        print(f"{player.name} is taking a turn.")

        steal_candidates = [p for p in self.players if p is not player and p.top_discard()]
        drawn = None

        if steal_candidates and random.random() < 0.4:
            opponent = random.choice(steal_candidates)
            drawn = player.take_from_discard(opponent)
            print(f"{player.name} takes from {opponent.name}'s discard: {drawn}")
        else:
            drawn = self.deck.draw()
            if drawn:
                player.add_card(drawn)
                print(f"{player.name} draws from deck.")
            else:
                print(f"{player.name} cannot draw; deck empty.")

        # Discard random card
        if player.hand_size() > 0:
            idx = random.randrange(player.hand_size())
            removed = player.discard_card_by_index(idx)
            print(f"{player.name} discards: {removed}")

    # Results
    def _print_final_results(self, winner: Player | None) -> None:
        print("\n" + "=" * 60)
        print("Game over!")

        for p in self.players:
            print(f"{p.name} - sets: {p.sets_count()}, score: {p.score}, "
                  f"hand size: {p.hand_size()}")

        if winner is None:
            print("No one reached 3 sets before deck exhaustion. Draw.")
        else:
            print(f"{winner.name} WINS the game!")
        print("=" * 60)
