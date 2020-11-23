import random
import re

class Player():
    '''
    Represent one of the game's players.

    '''

    def __init__(self, name, color):
        '''
        Creates a new object of the class.

        :param name:
        The player's name.

        :param color:
        A color for the player. Can be pretty much anything (string, codes, etc.),
        it's there in case it's used somehow for displaying the information.
        '''
        self.name = name
        self.color = color

        # These get filled by methods after the game starts
        self.objectives = []
        self.countries = []
        self.world_objective = None


    def __str__(self):
        return f"Player {self.name} ({self.color})"


class Country():
    def __init__(self, name, id):
        self.name = name
        self.id = id

        # Needs to be loaded from file
        self.neighbours = []

        # Gets assigned during the game
        self.player = None
        self.armies = 0


    def __str__(self):

        and_text = 'and'

        text = f'Country of {self.name}'

        if self.player != None:
            text += f", belonging to player {self.player.name}"

        if len(self.neighbours) > 0:
            # Some consideration to punctuation while enumerating
            if len(self.neighbours) == 1:
                text += f', with neighbour country {self.neighbours[0].name}'
            elif len(self.neighbours) == 2:
                text += f', with neighbour countries {self.neighbours[0].name} and {self.neighbours[1].name}'
            else:
                text += f', with neigbour countries '
                for c in self.neighbours:
                    text += f'{c.name}, '

                # Quick and dirty way to fix the end of the list

                # Take out the trailing ', ' from the enumeration
                text = re.sub(r', $', '', text)

                # We want to replace not the first but the last occurence of ', '
                # and replace it with 'and', so we reverse the string to leave the last occurence
                # as first. So we need to reverse and then replace ' ,'
                text = text[::-1].replace(' ,', f' {and_text[::-1]} ',1)[::-1]

        return text


    def add_neighbour(self,country):
        self.neighbours.append(country)


    def SetPlayer(self,pl):
        #print(f'{self.name} owned by: {self.player}')
        self.player = pl
        #print(f'{self.name} now owned by: {self.player}')


class Objective():
    '''
    Objective class to serve as the base for all types of objectives.
    '''
    def __init__(self):
        pass


    def IsAchieved(self):
        raise NotImplementedError('Subclass must implement this method.')


class WorldDominationObjective(Objective):
    '''
    Class for the generic objective for everyone of conquering a number of countries.
    '''

    def __init__(self,amount_countries):
        self.amount_countries = amount_countries


    def IsAchieved(self, player):
        if len(self.player.GetCountries()) >= self.amount_countries:
            return True
        else:
            return False


class AnihilationObjetive():
    '''
    Class for the objetives that require the destruction of an especific player.
    '''

    def __init__(self, player):
        '''
        Objective to destroy a player.
        :param player:
        The player who needs to be destroyed
        '''
        self.player = player


    def IsAchieved(self):
        if len(self.player.GetCountries()) == 0:
            return True
        else:
            return False


class ConquestObjetive(Objective):
    '''
    Class for objectives that require the conquest of a number of countries or continents.
    '''
    def __init__(self, continents, countries):
        self.countries = countries
        self.continents = continents


    def IsAchieved(self, player):
        '''

        :param player:
        The player whom should be evaluated.
        :return:
        '''
        return False


class Game():
    '''
    The Game class acts as an interface, to minimize the need of knowing
    the game's different classes and their methods.
    It offers methods with the usual actions of a game.
    '''

    # Players of this game
    players = None

    # All countries in game
    countries = None

    # Represent the deck with country cards
    countries_deck = None


    def InitialSetupReady(self):
        if self.players == None or len(self.players) < 2:
            return False

        if len(self.GetUnassignedCountries()) > 0:
            return False

        return True


    def LoadCountriesFromFile(self, countries_file='countries.txt', countries_connections_file='country_connections.txt'):
        '''
        Initialises the game's list of country objects with data from files.
        A country code is used for simplicity and storage efficiency in files,
        while definining neighbours for instance.

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
        '''
        self.countries = []
        countries_dict = {}

        # try:
        with open(countries_file, 'r') as countries_fp:
            for file_line in countries_fp.readlines():
                country_id, country_name = file_line.rstrip().split(';')
                country_id = int(country_id)
                new_country = Country(country_name, country_id)
                self.countries.append(new_country)
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


    def AssignPlayers(self, names_and_colors):
        '''
        Load the players into the appropiate class.

        :param names_and_colors:
        A list of tuples with name and color.

        :return:
        '''
        players = []

        for name, color in names_and_colors:
            players.append(Player(name, color))

        self.players = players


    def GetCountries(self, a_player):
        '''
        Returns a list with countries owned by a player.

        :param a_player:
        One object of the class Player
        :return:
        List collection of objects from the class Country
        '''
        countries_from_this_player = []
        for c in self.countries:
            #print(f'c.player=[{c.player}]; a_player=[{a_player}]')
            if c.player == a_player:
                countries_from_this_player.append(c)

        return countries_from_this_player


    def GetUnassignedCountries(self):
        unassigned_countries = []
        for c in self.countries:
            if c.player == None:
                unassigned_countries.append(c)
        return unassigned_countries


    def InitializeCountriesDeck(self):
        '''
        Sets the game's deck with country cards if countries are already loaded.

        :return:
        '''
        if self.countries != None:
            self.countries_deck = []
            for c in self.countries:
                self.countries_deck.append(c)
            random.shuffle(self.countries_deck)


    def ShowBoardForPlayer(self, player_number):
        '''
        Shows all the relevant information for a player during one round.
        '''
        current_player = Player('foo','ff')
        print(f'\nCurrent player: {players[player_name].name}')

        # List each country owned with its number of armies, also showing
        # surrounding regions with number of armies in each.
        print(f'\nCountries:')


    def ShowPlayerObjective(self, player_name):
        pass


    def Attack(self, country_from, country_to, dices_a, dices_d):
        '''
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
        '''

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
        dices_a.sort(Reverse=True)
        dices_d.sort(Reverse=True)

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


    def DealInitialCountriesEqually(self):
        '''
        Deals list of countries to players, dividing total between number of players.
        Modulus remains unassigned, i.e. if 10 countries and 3 players were distributed,
        one country will remain unassigned.

        The unassigned countries are returned, which should be assigned individually
        after throwing dices.
        '''

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


    def CheckIfWinner(self):
        '''
        Check if the game has a winner already, evaluating whether
        each player reached one of their objectives. Only the first
        match is returned, so this should be checked after each player
        moves.

        :return:
        Returns an instance of the class Player, namely the winner.
        Otherwise returns None.
        '''
        for p in self.players:
            for objective in p.objectives:
                if objective.IsAchieved():
                    return p

        return None


    def LoadWorldDominationObjective(self, percent_to_conquer):
        '''
        Creates the world domination objective, which is based on
        the total number of countries.

        :param percent_to_conquer:
        A floating point number representing the percentage number of countries
        to be conquered. Must be between greater than zero and lower or equal than one.
        :return:
        '''
        if self.countries == None or len(self.countries) == 0:
            raise Exception('Cannot do this if countries have not been loaded yet.')
        else:
            self.world_objective = WorldDominationObjective(round(percent_to_conquer * len(self.countries)))