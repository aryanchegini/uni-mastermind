import sys
import itertools
import os
import random
import time


def print_to_output(outputfile: str, message: str, mode: str = 'w') -> None:
    """
    :param outputfile: name of output file to write to
    :param message: message content
    :param mode: write mode, 'a' or 'w'
    :return: None
    """
    with open(outputfile, mode) as file:
        file.write(message + '\n')


def get_feedback(guess: str or list, secret_code: list) -> (int, int):
    """
    Takes in a guess and the secret code and returns pegs in the form (black pegs, white pegs).
    """
    code_copy = secret_code.copy()
    black_pegs = 0
    white_pegs = 0

    if type(guess) is str:
        guess = guess.split(' ')
    else:
        guess = list(guess)

    for i in range(len(code_copy)):
        if code_copy[i] == guess[i]:
            black_pegs += 1
            code_copy[i] = guess[i] = "matched"

    for colour in guess:
        if colour != 'matched' and colour in code_copy:
            white_pegs += 1
            code_copy.remove(colour)

    return black_pegs, white_pegs


def parse_inputs() -> tuple[str, str, int, int, list[str]]:
    if len(sys.argv) >= 3:

        input_file = sys.argv[1]
        # check if the input file exists
        if not os.path.exists(input_file):
            sys.exit(2)

        output_file = sys.argv[2]
        # check whether we have permission to write to output file
        if os.path.exists(output_file) and not os.access(output_file, os.W_OK):
            sys.exit(3)

        try:
            code_length = int(sys.argv[3])
        except IndexError:  # if only 3 arguments are given
            code_length = 5
        except ValueError:  # if value given is not an integer
            code_length = 12
        try:
            max_guesses = int(sys.argv[4])
        except IndexError:
            max_guesses = 12
        except ValueError:
            max_guesses = 12
        colours = sys.argv[5:]
        if len(colours) == 0:
            colours = ["red", "blue", "yellow", "green", "orange"]
    else:
        sys.exit(1)  # not enough program arguments provided

    return input_file, output_file, code_length, max_guesses, colours


def map_guesses(guesses: list[str], code_length: int, max_guesses: int, available_colours: list[str],
                set_code: list[int], outputfile: str) -> None:
    with open(outputfile, 'w'):  # clear the output file
        pass

    guess_count = 0
    lost = False
    won = False
    for guess in guesses:
        if lost or won:
            continue
        guess_count += 1
        if guess_count > max_guesses:
            print_to_output(outputfile, "You lost. Please try again.\nYou can only have 4 guesses.", 'a')
            lost = True
            continue
        if len(guess.split(" ")) != code_length or not all([g in available_colours for g in guess.split(" ")]):
            print_to_output(outputfile, f"Guess {guess_count}: Ill-formed guess provided", 'a')
        else:
            pegs = get_feedback(guess, set_code)
            feedback = 'black ' * pegs[0] + 'white ' * pegs[1]
            feedback.rstrip()
            print_to_output(outputfile, f"Guess {guess_count}: {feedback}", 'a')
            if pegs == (code_length, 0):  # if the feedback is all black pegs
                won = True
                print_to_output(outputfile, f"You won in {guess_count} guesses. Congratulations!", 'a')
                if guess_count < len(guesses):
                    print_to_output(outputfile, f"The game was completed. Further lines were ignored.", 'a')

    if not won and not lost:  # if they made fewer guesses than the maximum number of guesses
        print_to_output(outputfile, "You lost. Please try again.", "a")


def computer_game(outputfile: str, code_length: int, max_guesses: int, available_colours: list,
                  secret_code: list) -> None:
    # initialise files
    print_to_output("computerGame.txt", "code " + " ".join(secret_code))
    print_to_output("computerGame.txt", "player human", 'a')
    with open(outputfile, 'w'):  # clear the output file
        pass

    possible_guesses = list(itertools.product(available_colours, repeat=code_length))

    guess_count = 0
    won = False
    while guess_count < max_guesses and not won:
        guess_count += 1
        guess = list(random.choice(possible_guesses))  # return a random guess from the list of possible guesses

        print_to_output("computerGame.txt", " ".join(guess), 'a')
        pegs = get_feedback(guess, secret_code)
        feedback = 'black ' * pegs[0] + 'white ' * pegs[1]
        feedback.rstrip()
        print_to_output(outputfile, f"Guess {guess_count}: {feedback}", 'a')

        # only keeps the guesses which modify the current guess without decreasing the number of black or white pegs
        possible_guesses = [g for g in possible_guesses if get_feedback(g, guess) == pegs]

        if pegs == (code_length, 0):  # if the feedback is all black pegs
            won = True
            print_to_output(outputfile, f"You won in {guess_count} guesses. Congratulations!", 'a')

    if not won:
        print_to_output(outputfile, f"You lost. Please try again.\nYou can only have {max_guesses} guesses.", 'a')


def start() -> None:
    input_file, output_file, code_length, max_guesses, colours = parse_inputs()
    with open(input_file, 'r') as file:
        lines = file.readlines()  # store each line of the input file into a list
    lines = list(map(lambda x: x.rstrip('\n').rstrip(), lines))  # removes '\n' from the lines

    while lines and lines[-1].strip() == "":  # remove any blank lines at the end of the file
        lines.pop()

    # secret code exit codes
    set_code = lines[0].split(' ')

    if set_code[0] != 'code':
        print_to_output(output_file, 'No or ill-formed code provided')
        sys.exit(4)

    if len(set_code[1:]) != code_length:
        print_to_output(output_file, 'No or ill-formed code provided')
        sys.exit(4)

    for colour in set_code[1:]:
        if colour not in colours:
            print_to_output(output_file, 'No or ill-formed code provided')
            sys.exit(4)

    # player exit codes
    given_player = lines[1].split(' ')

    if given_player[0] != 'player':
        print_to_output(output_file, 'No or ill-formed player provided')
        sys.exit(5)

    if len(given_player[1:]) != 1:
        print(len(given_player[1:]))
        print_to_output(output_file, 'No or ill-formed player provided')
        sys.exit(5)

    if given_player[1] not in ['computer', 'human']:
        print_to_output(output_file, 'No or ill-formed player provided')
        sys.exit(5)

    # map guesses
    if given_player[1] == 'human':
        map_guesses(lines[2:], code_length, max_guesses, colours, set_code[1:], output_file)
        sys.exit(0)

    elif given_player[1] == 'computer':
        start_time = time.process_time()
        computer_game(output_file, code_length, max_guesses, colours, set_code[1:])
        end_time = time.process_time()
        print(end_time-start_time)
        sys.exit(0)


if __name__ == "__main__":
    start()
