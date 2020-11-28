# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import random
import risk
import helpers

colors = ['Red', 'Blue', 'Green', 'Yellow', 'Black', 'Pink', 'White', 'Grey']


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


def enumerate_countries_and_pick_one(countries):
    for (idx,c) in enumerate(countries):
        print(f'{idx + 1} - {c}')

    max_index = len(countries)
    country_no = helpers.prompt_int_range(
        f'Please select a country from the list (1-{max_index} or 0 to pass): ',
        None, 0, max_index)
    if country_no == 0:
        return None
    else:
        return countries[country_no - 1]


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

    with open(countries_connections_file, 'r') as connections_fp:
        for file_line in connections_fp.readlines():
            # print("[{}]".format(file_line.rstrip()))
            country_id, neighbour_id = file_line.rstrip().split(';')
            country_id = int(country_id)
            neighbour_id = int(neighbour_id)
            # print("cid [{}] nid [{}]".format(countries_dict[country_id],neighbour_id))
            # print("country [{}] has neighbour [{}]".format(countries_dict[country_id],countries_dict[neighbour_id]))
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
    helpers.screen_clear()
    print("\nWelcome to Patricio's TEG!\n\nLet's play.\n")


def prompt_players(game):
    """
    Prompts for players and sets name and color.

    :return:
    A list of objects of type Player
    """
    names_and_colors = []

    min_num = 2
    max_num = 6

    # while not (number_players >= min_num and number_players <= max_num):
    # number_players = int(input('How many players will be playing ({}-{})? '.format(min_num, max_num)))

    number_players = helpers.prompt_int_range('How many players will be playing? ', None, 2, 6)

    print(f"\nAlright, we have {number_players} today!\n")

    for x in range(number_players):
        name = input("Please enter player {}'s name: ".format(x + 1))
        p_color = colors.pop()
        print("Player {} is {} with color {}.\n".format(x + 1, name, p_color))
        names_and_colors.append((name, p_color))

    print("Because you cannot have people pick colors."
          "You'll have a bunch of guys fighting over who's Mr. Black.\n")

    game.AssignPlayers(names_and_colors)

    helpers.press_any_key()


def deal_initial_countries(game):
    """

    :param game:
    :return:
    """

    countries_per_player = int(len(game.countries) / len(game.players))
    countries_raffle = len(game.countries) % len(game.players)

    print(f"\nDealing countries to players now...\n")
    print(f"Total countries: {len(game.countries)}")
    print(f"Total players: {len(game.players)}")
    print(f"Countries per player: {countries_per_player}")
    print(f"Remaining countries after first round of dealing countries: {countries_raffle}")

    helpers.press_any_key()

    game.DealInitialCountriesEqually()

    for p in game.players:
        p_c = game.GetCountries(p)
        print(f'\n{p} got {len(p_c)}:')
        for c in game.GetCountries(p):
            print(c)

    helpers.press_any_key()


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

    helpers.press_any_key()


def demo_load_players(game, n):
    players = []
    if 1 < n < 7:
        for x in range(n):
            players.append(risk.Player(f'Player {x + 1}', colors.pop()))
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

    for p in game.players:
        game.UpdatePlayerCountries(p)

def show_player_countries(player, game):
    print(f'Countries from {player}:')
    x = 0
    for c in game.GetCountries(player):
        x += 1
        print(f'{x} - {c}')


def show_player_countries_which_can_attack(player, game):
    print(f'\nCountries from {player} that can attack:')
    x = 0
    for c in game.GetCountries(player, True):
        x += 1
        print(f'{x} - {c}')


def attack_round(player, game):
    finished_attacking = False
    while not finished_attacking:
        show_player_countries_which_can_attack(player, game)

        player_cs = game.GetCountries(player, True)

        if len(player_cs) > 0:

            attacking_country_no = helpers.prompt_int_range(
                'Which country is attacking? (Enter number or 0 to pass) ',
                None, 0, len(player_cs))

            if attacking_country_no > 0:

                attacker_c = player_cs[attacking_country_no - 1]

                enemy_countries = []
                for c in attacker_c.neighbours:
                    if c.player != attacker_c.player:
                        enemy_countries.append(c)

                if len(enemy_countries) > 0:

                    print(f'Country {attacker_c.name} can attack these enemy countries:')
                    x = 0
                    for n in enemy_countries:
                        x += 1
                        print(f'{x} - {n}')

                    attacked_country_no = helpers.prompt_int_range(
                        'Which country do you wish to attack? (Enter number) ',
                        None,
                        1,
                        len(enemy_countries))
                    attacked_country_no -= 1
                    attacked_c = enemy_countries[attacked_country_no]

                    max_attack_troops = attacker_c.armies - 1

                    # You cannot attack with more than three armies no matter how many the country has.
                    if max_attack_troops > 3:
                        max_attack_troops = 3

                    if max_attack_troops == 1:
                        print('Only one army available to attack.')
                        troops_no = 1
                    else:
                        troops_no = helpers.prompt_int_range(
                            f'How many troops are attacking? (1 to {max_attack_troops}) ',None, 1, max_attack_troops)

                    # game.Attack(attacker_c, attacked_c, dices_attacker, dices_defender)
                    battle = game.CallAttack(attacker_c, attacked_c, troops_no)

                    print(f"\nFollowing battle will take place:\n{battle}")

                    input(f'\n{player.name}, press any key to throw {troops_no} dices...')
                    battle.RollDicesAttacker()
                    print(f'{player.name} got dices {battle.dices_attacker}')

                    attacker_loses_before_fighting = True
                    for dice in battle.dices_attacker:
                        if dice > 1:
                            attacker_loses_before_fighting = False

                    if attacker_loses_before_fighting:
                        print(f'Ones means that the attacker cannot win, defender does not need to throw dices.')
                        battle.RollDicesDefender() # Because the object still needs dices to calculate
                    else:
                        input(f'\n{attacked_c.player.name}, press any key to throw {attacked_c.armies} dices...')
                        battle.RollDicesDefender()
                        print(f'{attacked_c.player.name} got dices {battle.dices_defender}')

                    battle.Calculate()

                    if battle.defender_lost_country:
                        game.UpdatePlayerCountries(battle.defending_player)
                        game.UpdatePlayerCountries(battle.attacking_player)

                    print(f"\nBattle results:\n{battle}")
                    print(f'\nStatus after battle:\n - Attacker {attacker_c}\n - Defender {attacked_c}')

                else:
                    print(f'{attacker_c} has no enemy neighbour countries.')

                helpers.press_any_key()

            else:
                finished_attacking = True

        else:
            print(f'{player.name} has no countries with more than one army that could attack.')
            finished_attacking = True

            helpers.press_any_key()


def movement_round(player, game):
    print(f'\nMovement round from {player.name}\n')

    countries_relocate = game.GetCountries(player, True)

    done_moving = False

    while not done_moving:

        if len(countries_relocate) > 0:

            cs_relocate_this_single_time = []
            for c in countries_relocate:
                if c.armies > 1:
                    cs_relocate_this_single_time.append(c)

            print(f'Countries that can move troops this round'
                  f' (does not change if other countries have more than one army after relocating once):')

            # Determine country from which troops are moving
            for nr,c in enumerate(cs_relocate_this_single_time):
                print(f'{nr+1} - {c}')
            relocating_country_no = helpers.prompt_int_range(
                'Please enter the number of the country to relocate troops (or 0 to pass): ',
                None, 0, len(cs_relocate_this_single_time))

            if relocating_country_no != 0:

                relocating_country = cs_relocate_this_single_time[relocating_country_no - 1]

                # Determine number of troops to move
                if relocating_country.armies == 2:
                    print('You can only move one army from this country.')
                    troops_no = 1
                else:
                    troops_min = 1
                    troops_max = relocating_country.armies - 1
                    troops_no = helpers.prompt_int_range(
                        f'Please enter the number of troops you want to move ({troops_min}-{troops_max}): ',
                        None, troops_min, troops_max)

                # Determine target country
                possible_target_countries = []
                for c in relocating_country.neighbours:
                    if c.player == player:
                        possible_target_countries.append(c)

                if len(possible_target_countries) > 0:
                    for nr, c in enumerate(possible_target_countries):
                        print(f'{nr + 1} - {c}')
                    target_country_no = helpers.prompt_int_range(
                        'Please enter the number of target the country (or 0 to pass): ',
                        None, 0, len(possible_target_countries))
                    target_country = possible_target_countries[target_country_no - 1]

                    relocating_country.armies -= troops_no
                    target_country.armies += troops_no
                    print(
                        f'\nMoved armies in following countries:\n - From: {relocating_country}\n - To: {target_country}')
                else:
                    print(f'No possible target countries to move!')

            else:
                print(f'{player} has finished moving.')
                done_moving = True

        else:
            print(f'Player has no countries with more than one troop that could relocate.')
            done_moving = True


def deployment_round(player, game):

    print(f"\n{player.name}'s deployment of new armies\n")
    armies_no = game.GetAmountArmiesPerTurn(player)
    p_countries = game.GetCountries(player)
    p_countries_no = len(p_countries)
    print(f'{player.name} has {p_countries_no} and thus gets {armies_no} to deploy into the map this round.')

    while armies_no > 0:
        print(f"{player.name}'s countries:")
        country = enumerate_countries_and_pick_one(p_countries)
        if country:
            armies_to_deploy = helpers.prompt_int_range(
                f'How many armies should be deployed? (1-{armies_no} or 0 to cancel) ',
                None, 0, armies_no)
            country.armies += armies_to_deploy
            armies_no -= armies_to_deploy

    print(f'{player.name} has placed all available armies on the map.')
    show_player_countries(player, game)


def check_if_winner(game):
    winner_player = game.CheckIfWinner()
    if winner_player:
        show_winner_banner(winner_player)
        return True
    else:
        return False


def show_winner_banner(player):
    print('\n####################################################')
    print(f'\nPLAYER {player} WINS!\n\nOne of the following objectives was fulfilled:')
    for o in player.objectives:
        print(f' - {o}')
    print('\n####################################################\n')


def ask_keep_playing():
    choice = input('\nDo you want to keep playing? [Y/n] ')
    if choice.lower() == 'n':
        return False
    else:
        return True


def show_countries_and_players(game):
    '''
    Shows countries and players lists.
    :return:
    Nothing.
    '''
    print('\nCurrent status of board\n')
    print('Countries:')
    for c in game.countries:
        print(f' - {c}')

    print('\nPlayers:')
    for p in game.players:
        print(f' - {p}')


def initialize_objectives(game):
    """
    Creates the game's objectives. These are hardcoded.

    """
    objectives = []

    # We create one annihilation objective per player. In the original game there's one card
    # per player, and if not possible (because player is not player or one is that player) then
    # the next person in the round should be taken as objective, but it's more logical in a computer
    # game to just make one objective for each player.
    for pl in game.players:
        annhil_objective = risk.AnnihilationObjetive(pl)
        objectives.append(annhil_objective)

    obj1 = risk.ConquestObjetive([game.continents[0]], None) # One continent
    obj2 = risk.ConquestObjetive([game.continents[1]],
                                 [(game.continents[0], 1)]) # One continent plus one country
    obj3 = risk.ConquestObjetive(game.continents, None) # Person getting this one is doomed
    obj4 = risk.ConquestObjetive(None,
                                 [(game.continents[0], 3), (game.continents[1], 3)])

    for o in [obj1, obj2, obj3, obj4]:
        objectives.append(o)

    objectives_deck_deal = objectives.copy()
    random.shuffle(objectives_deck_deal)
    for p in game.players:
        p.AddObjective(objectives_deck_deal.pop())

    for p in game.players:
        print(f"{p.name} has following objectives:")
        for o in p.objectives:
            print(f" - {o}")

def play():
    '''
    Main orchestration function. Call this to play.
    ´Will call for the user interaction functions.

    :return:
    Nothing
    '''

    # Initialize a game object
    game = risk.Game()

    # Flag to interrupt the game if desired
    keep_playing = True

    # We'll use winner as an identifier to finish the game
    winner = None

    # We shuffle colors once before playing, then they get assigned to players in create_players()
    random.shuffle(colors)

    show_banner()

    # Loading map data from files
    print('Loading map data from files...')
    game.LoadMapFromFile()

    game.InitializeCountriesDeck()

    # for c in game.countries:
    #   print(f'Country {c.name} loaded.')
    # press_any_key()

    prompt_players(game)
    # demo_load_players(game,4)
    # Deal countries to players, first round

    demo_deal_initial_countries(game)
    # Raffle for the rest of remaining cards if needed
    demo_deal_rest_countries_dice(game)

    game.LoadWorldDominationObjective(0.6)
    print(f'\nWorld domination set to {game.world_objective.amount_countries}.\n')

    initialize_objectives(game)

    game.AddTroopsTooAllCountries(1)
    for n in (2, 1):
        for p in game.players:
            # print(f'{p} adding now {n} armies.')
            for x in range(n):
                p_cs = game.GetCountries(p)
                c = p_cs[random.randint(0, len(p_cs) - 1)]
                # print(f'Adding randomly one army to: {c}')
                c.armies += 1

    show_countries_and_players(game)

    helpers.press_any_key()

    while keep_playing:

        print('\n------------------------------ 1. ATTACK AND RELOCATION ------------------------------\n')
        for p in game.players:

            if keep_playing:
                print(f'{p.name} plays!\n\nATTACK ROUND\n')
                attack_round(p, game)

                if check_if_winner(game):
                    keep_playing = False
                    break

                if not ask_keep_playing():
                    keep_playing = False
                    break

            else:
                break

            if keep_playing:
                print(f'\n{p.name} has finished attacking.\n\nRELOCATION ROUND\n')
                movement_round(p, game)
                print(f'\n{p.name} has finished relocating troops.')

                if check_if_winner(game):
                    keep_playing = False
                    break

                if not ask_keep_playing():
                    keep_playing = False
                    break

            else:
                break

        if keep_playing:
            print('\n------------------------------ 2. DEPLOYMENT ROUND ------------------------------\n')
            for p in game.players:

                print(f'{p.name} plays!\n\nTroop deployment round\n')
                deployment_round(p, game)
                print(f'\n{p.name} has finished deploying troops.')

                if not ask_keep_playing():
                    keep_playing = False
                    break


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    play()
