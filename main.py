from game import Game

def main() -> None:
    print("Welcome to the Hotpot Card Game!")
    print("How many human players? (1 to 4)")

    while True:
        count = input("Enter number of human players: ").strip()
        if count.isdigit():
            n = int(count)
            if 1 <= n <= 4:
                break
            print("Invalid input. Please enter 1, 2, 3, or 4.")

        game = Game(human_count=n)
        game.play()

if __name__ == "__main__":
    main()

    