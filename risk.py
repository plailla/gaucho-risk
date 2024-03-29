import random
import math
import re
import helpers


class Player:
    """
    Represent one of the game's players.

    """

    def __init__(self, name, color):
        """
        Creates a new object of the class.

        :param name:
        The player's name.

        :param color:
        A color for the player. Can be pretty much anything (string, codes, etc.),
        it's there in case it's used somehow for displaying the information.
        """
        self.name = name
        self.color = color

        # These get filled by methods after the game starts
        self.times_country_cards_traded = 0
        self.objectives = []
        self.countries = []
        self.cards = None
        self.world_objective = None
        #self.cards_deck = None

    def __str__(self):
        return f"{self.name} ({self.color})"

    def add_objective(self, objective):
        self.objectives.append(objective)


class Country:
    def __init__(self, name, id):
        self.name = name
        self.id = id

        # Needs to be loaded from file
        self.neighbours = []
        self.continent = None

        # Gets assigned during the game
        self.player = None
        self.armies = 0

    def __str__(self):

        and_text = 'and'

        text = f'{self.name}'

        if self.player != None:
            text += f" ({self.player.name}, {self.armies})"
        else:
            text += f" ({self.armies})"

        if len(self.neighbours) > 0:
            # # Some consideration to punctuation while enumerating
            # if len(self.neighbours) == 1:
            #     text += f' - with neighbour {self.neighbours[0].name}'
            # elif len(self.neighbours) == 2:
            #     text += f' - with neighbours {self.neighbours[0].name} and {self.neighbours[1].name}'
            # else:
            #     text += f' - with neighbours '
            #     for c in self.neighbours:
            #         text += f'{c.name}, '
            #
            #     # Quick and dirty way to fix the end of the list
            #
            #     # Take out the trailing ', ' from the enumeration
            #     text = re.sub(r', $', '', text)
            #
            #     # We want to replace not the first but the last occurence of ', '
            #     # and replace it with 'and', so we reverse the string to leave the last occurence
            #     # as first. So we need to reverse and then replace ' ,'
            #     text = text[::-1].replace(' ,', f' {and_text[::-1]} ',1)[::-1]
            text += ' - neighbours: '

            for sorted_country in sorted(self.neighbours, key=lambda x: x.armies, reverse=True):
                text += f'{sorted_country.name} ({sorted_country.armies}), '

        return text

    def add_neighbour(self,country):
        self.neighbours.append(country)

    def SetPlayer(self,pl):
        #print(f'{self.name} owned by: {self.player}')
        self.player = pl
        #print(f'{self.name} now owned by: {self.player}')


class Continent:
    """
    A continent, which has a list of countries and a number of armies that it grants to its conqueror.
    """

    def __init__(self, name, army_bonus):
        # Required attributes for initialization
        self.name = name
        self.army_bonus = army_bonus

        # Attributes set later
        self.countries = None

    def __str__(self):
        return f"{self.name} ({len(self.countries)} countries)"

    def set_countries(self, countries):
        self.countries = countries

    def add_country(self, country):
        if not self.countries:
            self.countries = []
        self.countries.append(country)

    def conquered_by_player(self, player):
        conquered_by_player = True
        for c in self.countries:
            if c.player != player:
                conquered_by_player = False

        return conquered_by_player


class Objective:
    """
    Objective class to serve as the base for all types of objectives.
    """
    def __init__(self):
        pass


    def is_achieved(self, player):
        raise NotImplementedError('Subclass must implement this method.')


class WorldDominationObjective(Objective):
    """
    Class for the generic objective for everyone of conquering a number of countries.
    """

    def __init__(self,amount_countries, all_countries):
        self.amount_countries = amount_countries
        self.all_countries = all_countries

    def __str__(self):
        return f'World domination - Conquer a total of {self.amount_countries} countries'

    def is_achieved(self, pl):
        p_countries = []
        for c in self.all_countries:
            if c.player == pl:
                p_countries.append(c)
        if len(p_countries) >= self.amount_countries:
            return True
        else:
            return False


class AnnihilationObjetive:
    """
    Class for the objectives that require the destruction of a specific player.
    """
    def __init__(self, player_to_be_destroyed):
        """
        Objective to destroy a player.
        :param player_to_be_destroyed:
        The player who needs to be destroyed
        """
        self.player = player_to_be_destroyed

    def __str__(self):
        return f"Eliminate {self.player}"

    def is_achieved(self, player):
        if len(self.player.countries) == 0:
            return True
        else:
            return False


class ConquestObjetive(Objective):
    """
    Class for objectives that require the conquest of a number of countries or continents.

    Can be basically a combination of the following:
     - A number of continents
     - A number of countries from a continent
    """
    def __init__(self, continents_to_conquer=None, continents_and_number_countries=None):
        """
        Creates a new conquest objective.

        :param continents_to_conquer: A list of continents to be conquered
        :param continents_and_number_countries: A list of tuples with continent and int of total number of countries
        """
        # Check if we got enough data from the parameters
        if ((not continents_and_number_countries) or (len(continents_and_number_countries) == 0))\
                and  ((not continents_to_conquer) or (len(continents_to_conquer) == 0)):
            raise Exception("A conquest objective must have either a list of continents"
                            "or a list of number of countries in continents.")
        self.continents_and_number_countries = continents_and_number_countries
        self.continents_to_conquer = continents_to_conquer

    def __str__(self):
        text = f'Conquer'
        if self.continents_to_conquer and len(self.continents_to_conquer):
            text += " "
            for cont in self.continents_to_conquer:
                text += f'the continent of {cont.name}, '
            text = re.sub(r', $', '', text)
        if self.continents_and_number_countries and len(self.continents_and_number_countries) > 0:
            text += " "
            for cont, num_countries in self.continents_and_number_countries:
                text += f'{num_countries} countries of the continent of {cont.name}, '
            text = re.sub(r', $', '', text)
        return text

    def is_achieved(self, player):
        """

        :param player:
        The player who should be evaluated.
        :return:
        """
        # We'll start from 'accomplished' and set it to false the first time we see something not fulfilled.
        achieved = True
        if self.continents_to_conquer != None and len(self.continents_to_conquer) > 0:
            for cont in self.continents_to_conquer:
                for c in cont.countries:
                    if c.player != player:
                        achieved = False
        if self.continents_and_number_countries != None and len(self.continents_and_number_countries) > 0:
            for (cont, num_required_countries) in self.continents_and_number_countries:
                conquered_countries = 0
                for c in cont.countries:
                    if c.player == player:
                        conquered_countries += 1
                    if conquered_countries < num_required_countries:
                        achieved = False


class Battle:

    def __init__(self, attacking_country, defending_country, attacker_troops_no):

        max_troops = 3

        # Parameters required at creation
        self.attacking_country = attacking_country
        self.defending_country = defending_country

        if attacker_troops_no <= max_troops:
            self.attacker_troops_no = attacker_troops_no
        else:
            self.attacker_troops_no = max_troops

        # Parameters we want to know and that may change in the future
        self.attacking_player = self.attacking_country.player
        self.defending_player = self.defending_country.player

        if self.defending_country.armies <= max_troops:
            self.defender_troops_no = self.defending_country.armies
        else:
            # We cannot defend with more than three.
            self.defender_troops_no = max_troops

        # Some game logic check
        if self.attacking_country == self.defending_country:
            raise Exception("A country cannot attack itself (in this game, at least).")
        if self.attacking_player == self.defending_player:
            raise Exception("A player cannot attack her/himself (in this game, at least).")

        # Whether the battle already took place
        self.is_decided = False

        # Attributes related to results of the battle
        self.dices_attacker = None
        self.dices_defender = None
        self.casualties_attacker = 0
        self.casualties_defender = 0
        self.defender_lost_country = False

        # Time
        self.time_created = None
        self.time_fought = None

    def __str__(self):
        text = (f'{self.attacking_country.name} ({self.attacking_country.player.name})'
                f' attacks with {self.attacker_troops_no} armies {self.defending_country.name}'
                f' ({self.defending_player.name}, {self.defending_country.armies} armies)')

        if self.is_decided:
            text += (f'; attacker lost {self.casualties_attacker}, dices {self.dices_attacker}'
                    f'; defender lost {self.casualties_defender}, dices {self.dices_defender}')

        if self.defender_lost_country:
            text += ', attacker conquered country'

        return text

    def roll_dices_attacker(self):
        self.dices_attacker = []
        for x in range(self.attacker_troops_no):
            self.dices_attacker.append(random.randint(1,6))
        return self.dices_attacker

    def roll_dices_defender(self):
        self.dices_defender = []
        for x in range(self.defender_troops_no):
            self.dices_defender.append(random.randint(1,6))
        return self.dices_defender

    def calculate(self):
        """

        """
        if self.dices_defender and self.dices_attacker:
            # Should we also check if it's been calculated already?

            self.casualties_defender = 0
            self.casualties_attacker = 0

            # Game rule check, cannot attack if having only one army
            if self.attacking_country.armies == 1:
                raise Exception('Cannot attack when having only one army.')

            # Determine how many armies are fighting, determined by minimum amount
            # of both sets of dices
            fighting_armies = min(len(self.dices_attacker), len(self.dices_defender))

            # Sort dices high to low
            self.dices_attacker.sort(reverse=True)
            self.dices_defender.sort(reverse=True)

            # We take the first/best X dices and compare them to estimate losses
            for x in range(fighting_armies):
                # Defender wins on tied dices
                if self.dices_attacker[x] > self.dices_defender[x]:
                    self.casualties_defender += 1
                else:
                    self.casualties_attacker += 1

            self.attacking_country.armies -= self.casualties_attacker
            self.defending_country.armies -= self.casualties_defender

            # If the target country lost all the armies in this battle then
            # the attacker gets it and moves the remaining troops of the movilized ones
            if self.defending_country.armies == 0:
                # Make the move process

                # Change the player on target country
                self.defending_country.player = self.attacking_country.player

                # Estimate and move the troops from attacking country to newly conquered
                remaining_attacking_troops = self.attacker_troops_no - self.casualties_attacker
                self.attacking_country.armies -= remaining_attacking_troops
                self.defending_country.armies += remaining_attacking_troops

                # Update the indicator
                self.defender_lost_country = True
            elif self.defending_country.armies < 0:
                raise Exception('Defending armies went below zero, which is impossible in the game'
                                ' (but nothing is impossible in the wonderful world of IT)')
            elif self.defending_country.armies > 0:
                self.defender_lost_country = False

            self.is_decided = True

        else:
            raise Exception('You cannot decide a battle without throwing dices on both sides.'
                            'Call both RollDices...() functions first.')


class CountryCard:

    def __init__(self, country, figure, already_traded=False):
        self.country = country
        self.already_traded = already_traded
        self.figure = figure

    def __str__(self):
        text = f"{self.country.name} ({self.figure})"
        if self.already_traded:
            text += " (already traded)"
        return text

    def trade(self):
        if not self.already_traded:
            self.already_traded = True
        else:
            raise Exception("The country card {self} has already been marked as traded.")


class Game:
    """
    The Game class acts as an interface, to minimize the need of knowing
    the game's different classes and their methods.
    It offers methods with the usual actions of a game.
    """

    def __init__(self):
        # Players of this game
        self.players = None

        # All countries in game
        self.countries = None
        self.countries_by_id = None

        # Represent the deck with country cards
        self.country_card_deck = None
        self.country_cards = None

        # Keep track of battles in game
        self.battles = []

        # Player gets a number of armies no matter how few countries she/he has
        self.min_armies_per_turn = 3

        self.world_objective = None

        # More new status variables
        self.current_player = None
        self.player_conquered_territory = False

    def initial_setup_ready(self):
        if self.players == None or len(self.players) < 2:
            return False

        if len(self.get_unassigned_countries()) > 0:
            return False

        return True

    def load_map_from_file(
            self,
            countries_file='game_data/countries.txt',
            countries_connections_file='game_data/country_connections.txt',
            continents_file='game_data/continents.txt'):
        """
        Initialises the game's list of country and continent objects with data from files.
        A country and continent codes are used for simplicity and storage efficiency in files,
        while defining neighbours for instance.

        :param continents_file
        A file with one to many lines with the format "ID_CONTINENT;CONTINENT_NAME;ARMY_BONUS". E.g.
        1;Africa;3

        :param coutries_file:
        A file with one line per country with a code and its description with
        the format "ID_COUNTRY;COUNTRY_NAME". E.g.

        1;Argentina
        2;Brasil
        3;Uruguay

        :param neighbours_file:
        A file with one line per country with a code and its description with
        the format "ID_COUNTRY;COUNTRY_NAME". E.g.

        1;2
        1;3
        2;1
        2;3
        3;1
        3;2

        :return:
        Nothing
        """

        # The actual list of continents that will set for the game
        continents = []

        # A dictionary with the loaded continents accessible by ID
        continents_dict = {}

        self.countries = []
        countries_dict = {}

        with open(continents_file, 'r') as continents_fp:
            for file_line in continents_fp.readlines():
                continent_id, continent_name, continent_army_bonus = file_line.rstrip().split(';')
                continent_id = int(continent_id)
                cont = Continent(continent_name, int(continent_army_bonus))
                continents.append(cont)
                continents_dict[continent_id] = cont
            continents_fp.close()

        self.continents = continents

        # try:
        with open(countries_file, 'r') as countries_fp:
            for file_line in countries_fp.readlines():
                country_id, country_name, continent_id = file_line.rstrip().split(';')
                country_id = int(country_id)
                continent_id = int(continent_id)
                new_country = Country(country_name, country_id)
                new_country.continent = continents_dict[continent_id]
                self.countries.append(new_country)
                countries_dict[country_id] = new_country
                continents_dict[continent_id].add_country(new_country)
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

        self.countries_by_id = countries_dict

    def load_cards(self, cards_file="game_data/card_figures.txt", country_figures_file="game_data/countries_figures.txt"):
        new_cards_deck = []

        figures = {}

        try:
            for file_line in helpers.read_game_data_from_file(cards_file):
                card_number, card_figure = file_line.split(';')
                figures[int(card_number)] = card_figure

            for file_line in helpers.read_game_data_from_file(country_figures_file):
                country_number, card_number = file_line.split(';')
                country_number = int(country_number)
                card_number = int(card_number)
                country = self.countries_by_id[country_number]
                card = CountryCard(country, figures[card_number])
                new_cards_deck.append(card)

            self.country_cards = new_cards_deck

        except:
            raise Exception('There was a problem while reading the country card data.')

    def assign_players(self, names_and_colors):
        """
        Load the players into the appropiate class.

        :param names_and_colors:
        A list of tuples with name and color.

        :return:
        """
        players = []

        for name, color in names_and_colors:
            players.append(Player(name, color))

        self.players = players

    def get_countries(self, a_player, only_countries_with_more_than_one=False):
        """
        Returns a list with countries owned by a player.

        :param a_player:
        One object of the class Player
        :return:
        List collection of objects from the class Country
        """
        countries_from_this_player = []
        for c in self.countries:
            #print(f'c.player=[{c.player}]; a_player=[{a_player}]')
            if c.player == a_player:
                if only_countries_with_more_than_one:
                    if c.armies > 1:
                        countries_from_this_player.append(c)
                else:
                    countries_from_this_player.append(c)

        return countries_from_this_player

    def get_unassigned_countries(self):
        unassigned_countries = []
        for c in self.countries:
            if c.player == None:
                unassigned_countries.append(c)
        return unassigned_countries

    def initialize_countries_deck(self):
        """
        Sets the game's deck with country cards if countries are already loaded.

        :return:
        """
        if self.country_cards and len(self.country_cards) > 0:
            self.country_card_deck = self.country_cards.copy()
            random.shuffle(self.country_card_deck)

        #print('Initialized and shuffled country cards deck.')

    def show_board_for_player(self, player_number):
        """
        Shows all the relevant information for a player during one round.
        """
        current_player = Player('foo','ff')
        print(f'\nCurrent player: {players[player_name].name}')

        # List each country owned with its number of armies, also showing
        # surrounding regions with number of armies in each.
        print(f'\nCountries:')

    def show_player_objective(self, player_name):
        pass

    def call_attack(self, country_from, country_to, troops_no):

        b = Battle(country_from, country_to, troops_no)
        self.battles.append(b)
        return b

    def attack(self, country_from, country_to, dices_a, dices_d):
        """
        A player attacks a country and eventually conquers it.
        :param country_from:
        The country where the attack is coming from.
        :param country_to:
        The attacked country.
        :param dices_a:
        The dices of the attacker. An iterable (list or tuple) with a set of integers.
        :param dices_d:
        The dices from the defender. An iterable (list or tuple) with a set of integers.
        :return:
        """

        losses_defender = 0
        losses_attacker = 0

        # Game rule check, cannot attack if having only one army
        if country_from.armies == 1:
            raise Exception('Cannot attack when having only one army.')

        # Determine how many armies are fighting, determined by minimum number
        fighting_armies = min(len(dices_a), len(dices_d))

        # We need to know how many troops the attacker sent to battle, as the
        # remaining will move to the target country if the enemy was destroyed
        number_attacking_troops = len(dices_a)

        # Sort dices high to low
        dices_a.sort(reverse=True)
        dices_d.sort(reverse=True)

        # We take the first/best X dices and compare them to estimate losses
        for x in range(fighting_armies):
            # Defender wins on tied dices
            if dices_a[x] > dices_d[x]:
                losses_defender += 1
            else:
                losses_attacker += 1

        country_from.armies -= losses_attacker
        country_to.armies -= losses_defender

        # If the target country lost all the armies in this battle then
        # the attacker gets it and moves the remaining troops of the movilized ones
        if country_to.armies == 0:
            country_to.player = country_from.player
            remaining_attacking_troops = number_attacking_troops - losses_attacker
            country_from.armies -= remaining_attacking_troops
            country_to.armies += remaining_attacking_troops

    def deal_initial_countries_equally(self):
        """
        Deals list of countries to players, dividing total between number of players.
        Modulus remains unassigned, i.e. if 10 countries and 3 players were distributed,
        one country will remain unassigned.

        The unassigned countries are returned, which should be assigned individually
        after throwing dices.
        """

        countries_to_deal = self.countries.copy()
        random.shuffle(countries_to_deal)
        countries_per_player = int(len(self.countries) / len(self.players))
        # So for each player in this game
        for p in self.players:
            # add a number of countries to the player
            for i in range(countries_per_player):
                c = countries_to_deal.pop()
                #print(f'Giving {c.name} to {p}.')
                c.SetPlayer(p)

        #print(f'\Countries in the game now:')
        #for c in self.countries:
        #    print(c)

        #print(f'\nFollowing countries still to be assgined:')
        #for c in countries_to_deal:
        #    print(c)
        # return the unassigned countries
        return countries_to_deal

    def add_troops_too_all_countries(self, number_of_troops=1):
        """
        Adds a number of armies to all countries. Meant to be used starting the game.

        :param number_of_troops:
        An integer with the number of troops to be added. Default of 1 if unspecified.
        :return:
        """
        if self.countries == None or len(self.countries) == 0:
            raise Exception('Cannot use if countries has not been initialized.')

        for c in self.countries:
            c.armies += number_of_troops

    def check_if_winner(self):
        """
        Check if the game has a winner already, evaluating whether
        each player reached one of their objectives. Only the first
        match is returned, so this should be checked after each player
        moves.

        :return:
        Returns an instance of the class Player, namely the winner.
        Otherwise returns None.
        """
        for p in self.players:
            for objective in p.objectives:
                #print(objective)
                if objective.is_achieved(p):
                    #print(f'{p.name} achieved:\n{objective}')
                    return p

        return None

    def load_world_domination_objective(self, percent_to_conquer):
        """
        Creates the world domination objective, which is based on
        the total number of countries.

        :param percent_to_conquer:
        A floating point number representing the percentage number of countries
        to be conquered. Must be between greater than zero and lower or equal than one.
        :return:
        """
        if self.countries == None or len(self.countries) == 0:
            raise Exception('Cannot do this if countries have not been loaded yet.')
        elif self.players == None or len(self.players) == 0:
            raise Exception('Cannot do this if players have not been loaded yet.')
        else:
            self.world_objective = WorldDominationObjective(round(percent_to_conquer * len(self.countries)), self.countries)
            for p in self.players:
                p.add_objective(self.world_objective)

    def get_amount_armies_per_turn(self, player):
        armies = int(math.ceil(len(self.get_countries(player)) / 2))
        if armies < 3:
            armies = self.min_armies_per_turn
        return armies

    def update_player_countries(self, player):
        player.countries = self.get_countries(player)

    def trade_card_posessed_country(self, card):
        num_armies = 2
        card.already_traded = True
        return num_armies

    def trade_cards_figures_set(self, player, cards):

        num_required_cards = 3

        if len(cards) == num_required_cards:

            if player.times_country_cards_traded == 0:
                num_armies_for_player = 4
            elif player.times_country_cards_traded == 1:
                num_armies_for_player = 7
            elif player.times_country_cards_traded >= 2:
                num_armies_for_player = 10
            else:
                raise Exception(f'Player {player.name} traded cards {player.times_country_cards_traded} times?')

            for card in cards:
                player.cards.pop(card)
                card.already_traded = False
                self.country_card_deck.add(card)

            return num_armies_for_player

        else:
            raise Exception(f'To trade in cards you need {num_required_cards} cards.')

    def give_country_card_to_player(self, player):
        a_card = self.country_card_deck.pop()
        a_card.already_traded = False
        player.cards.add(a_card)

    def advance_next_player(self):
        if self.initial_setup_ready():
            if self.current_player:
                # Iterate through the list of players and get the next one,
                # if we are at the last one then return the first one
                idx_player = self.players.index(self.current_player)
                if idx_player == len(self.players) - 1: # at the last item
                    self.current_player = self.players[0]
                else:
                    self.current_player = self.players[idx_player + 1]
            else:
                # If current player has not been set yet then just assign the first one
                self.current_player = self.players[0]


class Army:
    """
    Represent a single army. Stores current and previous country.
    """

    def __init__(self, player, current_country, previous_country=None):
        self.previous_country = previous_country
        self.current_country = current_country
        self.player = player

    def __str__(self):
        return f"Army from {self.player.name} in {self.current_country}"
