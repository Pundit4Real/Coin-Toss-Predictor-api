import random

def coin_toss():
    """
    Simulate a coin toss game.
    """
    # Generate a random number between 0 and 1
    result = random.random()

    # Determine the outcome (head or tail) based on the random number
    if result <= 0.45:
        return 'Tail'
    else:
        return 'Head'

def user_prediction(user_choice):
    """
    Simulate user's prediction.
    """
    # Generate a random number between 0 and 1
    result = random.random()

    # Determine the outcome (win or loss) based on the user's choice
    if user_choice.lower() == 'tail' and result <= 0.45:
        return 'Win'
    elif user_choice.lower() == 'head' and result > 0.45:
        return 'Win'
    else:
        return 'Loss'

def play_game(num_rounds):
    """
    Simulate multiple rounds of the game.
    """
    wins = 0
    losses = 0

    for _ in range(num_rounds):
        user_choice = input("Enter your choice (Head or Tail): ")
        user_result = user_prediction(user_choice)

        coin_result = coin_toss()

        print(f"The result of the coin toss: {coin_result}")
        print(f"Your prediction: {user_result}")

        if user_result == 'Win':
            wins += 1
        else:
            losses += 1

    print(f"Total Wins: {wins}")
    print(f"Total Losses: {losses}")

# Simulate 5 rounds of the game
play_game(5)
