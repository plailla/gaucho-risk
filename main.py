# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import random
import risk

colors = ['Red', 'Blue', 'Green', 'Yellow', 'Black', 'Pink', 'White', 'Grey']

def press_any_key():
    input('\nPress any key to continue...\n')


def lang_enumeration(and_expression='and', *kwarg):
    text = ''
    for item in kwarg:
        text += ''

    return text


def throw_dice(n, min=1, max=6):
    '''
    Simulates throwing dices.
    :param n:
    Number of dices
    :return:
    List of N dices
    '''
    dices = []

    for x in range(n):
        dices.append(random.randint(min, max))

    return dices


def compare_dices(dices1, dices2):
    '''
    Compares two sets of dices and returns the winner.
    :param dices1:
    List of integers with dice numbers.
    :param dices2:
    List of integers with dice numbers.
    :return:
    List of integers with winning dice numbers.
    '''
    ordered_1 = sorted(dices1)
    ordered_2 = sorted(dices2)
    for x in range(min(len(ordered_1), len(ordered_2))):
        pass


def show_dices(dices):
    text = ''
    for dice in sorted(dices):
        text += f'({dice}) '
    print(text)


def load_countries(countries_file='countries.txt', countries_connections_file='country_connections.txt'):
    countries = []
    countries_dict = {}

    print('Loading countries from the database...')

    # try:
    with open(countries_file, 'r') as countries_fp:
        for file_line in countries_fp.readlines():
            country_id, country_name = file_line.rstrip().split(';')
            country_id = int(country_id)
            new_country = risk.Country(country_name, country_id)
            countries.append(new_country)
            countries_dict[country_id] = new_country
        countries_fp.close()

    with open(countries_connections_file,'r') as connections_fp:
        for file_line in connections_fp.readlines():
            #print("[{}]".format(file_line.rstrip()))
            country_id, neighbour_id = file_line.rstrip().split(';')
            country_id = int(country_id)
            neighbour_id = int(neighbour_id)
            #print("cid [{}] nid [{}]".format(countries_dict[country_id],neighbour_id))
            #print("country [{}] has neighbour [{}]".format(countries_dict[country_id],countries_dict[neighbour_id]))
            countries_dict[country_id].add_neighbour(countries_dict[neighbour_id])
        connections_fp.close()

    print('Loaded following countries:\n')
    for c in countries:
        print(c)

    input('\nPress any key to continue...')

    return countries
    # except:
    #    print("Problem reading data from files.")


def show_banner():
    print("\nWelcome to Patricio's TEG!\n\nLet's play.\n")


def prompt_players(game):
    '''
    Prompts for players and sets name and color.

    :return:
    A list of objects of type Player
    '''
    names_and_colors = []

    min_num = 2
    max_num = 6

    number_players = 0

    while not (number_players >= min_num and number_players <= max_num):
        number_players = int(input('How many players will be playing ({}-{})? '.format(min_num, max_num)))

    print(f"\nAlright, we have {number_players} today!\n")

    for x in range(number_players):
        name = input("Please enter player {}'s name: ".format(x + 1))
        p_color = colors.pop()
        print("Player {} is {} with color {}.\n".format(x + 1, name, p_color))
        names_and_colors.append((name, p_color))

    print("Because you cannot have people pick colors. You'll have a bunch of guys fighting over who's Mr. Black.\n")

    game.AssignPlayers(names_and_colors)

    press_any_key()


def deal_initial_countries(game):
    '''

    :param game:
    :return:
    '''

    countries_per_player = int(len(game.countries) / len(game.players))
    countries_raffle = len(game.countries) % len(game.players)

    print(f"\nDealing countries to players now...\n")
    print(f"Total countries: {len(game.countries)}")
    print(f"Total players: {len(game.players)}")
    print(f"Countries per player: {countries_per_player}")
    print(f"Remaining countries after first round of dealing countries: {countries_raffle}")

    press_any_key()

    game.DealInitialCountriesEqually()

    for p in game.players:
        p_c = game.GetCountries(p)
        print(f'\n{p} got {len(p_c)}:')
        for c in game.GetCountries(p):
            print(c)

    press_any_key()


def deal_rest_countries_dice(game):

    free_countries = game.GetUnassignedCountries()
    players_dices = []
    winner = None

    print("\nWe still have to deal {} countries, but we'll use dices for that:".format(len(free_countries)))

    for c in free_countries:
        print(f'Dealing country {c.name}:')
        max_value = 0
        for p in game.players:
            input(f"{p.name}, press any key to roll one dice.")
            dice = throw_dice(1)[0]
            players_dices.append((p, dice))
            print(f"{p.name} got {dice}.")
            if dice > max_value:
                max_value = dice
                winner = p

        print(f'Player {winner.name} receives {c.name}.')
        c.SetPlayer(winner)
            ### What happens if two people get the same? or three?

    press_any_key()


def demo_load_players(game, n):
    players = []
    if n > 1 and n < 7:
        for x in range(n):
            players.append(risk.Player(f'Player {x+1}', colors.pop()))
        game.players = players


def demo_deal_initial_countries(game):
    game.DealInitialCountriesEqually()


def demo_deal_rest_countries_dice(game):
    free_countries = game.GetUnassignedCountries()
    players_dices = []

    for c in free_countries:
        max_value = 0
        for p in game.players:
            dice = throw_dice(1)[0]
            players_dices.append((p, dice))
            if dice > max_value:
                max_value = dice
                winner = p
        print(f'Player {winner.name} receives {c.name}.')
        c.SetPlayer(winner)
            ### What happens if two people get the same? or three?


def play():
    '''
    Main orchestration function. Call this to play.
    ´Will call for the user interaction functions.

    :return:
    Nothing
    '''
    game = risk.Game()

    # We shuffle colors once before playing, then they get assigned to players in create_players()
    random.shuffle(colors)

    show_banner()

    game.LoadCountriesFromFile()
    game.InitializeCountriesDeck()

    for c in game.countries:
       print(f'Country {c.name} loaded.')
    press_any_key()

    game.LoadWorldDominationObjective(0.6)
    print(f'\nWorld domination set to {game.world_objective.amount_countries}.\n')

    #prompt_players(game)
    demo_load_players(game,4)
    # Deal countries to players, first round
    demo_deal_initial_countries(game)
    # Raffle for the rest of remaining cards if needed
    demo_deal_rest_countries_dice(game)

    game.AddTroopsTooAllCountries(1)
    for n in (2, 1):
        for p in game.players:
            #print(f'{p} adding now {n} armies.')
            for x in range(n):
                p_cs = game.GetCountries(p)
                c = p_cs[random.randint(0, len(p_cs) - 1)]
                #print(f'Adding randomly one army to: {c}')
                c.armies += 1

    print('\nInitial status of board\n')
    print('Countries:')
    for c in game.countries:
        print(f' - {c}')

    print('\nPlayers:')
    for p in game.players:
        print(f' - {p}')

    press_any_key()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    play()