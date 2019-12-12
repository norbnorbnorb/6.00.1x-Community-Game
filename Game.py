# Game Class
import json
import os
from random import *
from time import sleep

from Class_Party import *
import Class_World_Map
# from Class_Map import *
from Class_Hero import *
from helper_functions import *
from battle import *
from data_src import get_save_games, data
import vfx

project_path = os.getcwd()
save_file_extention = '.json'
save_folder = 'saves'


class Game:
    def __init__(self):
        self.party = Party.generate(self)
        self.Mode = ''
        self.world_map = Class_World_Map.MapManager()
        self.difficulty = ''
        self.kill_count = {
            'trash': 0,
            'elite': 0,
            'boss': 0,
        }

    @staticmethod
    def create_character(name='Jeb', profession='Astronaut', level=1):
        """
         Create new character
         Allows selection of char and reroll of stats
         """
        unit_loc_str = 'heroes/bases/'+profession
        return Hero.generate_unit(unit_loc_str, level, name)

    def create_random_character(self, cls=NPC):
        """
         Create new random character the same level as the party leader
         """
        return cls.generate_random(randint(1, self.party.hero.level))

    def create_hero(self):

        def roll_hero():
            hero_name = input('What is your name, hero?:\n').title()
            if len(hero_name) > 10:
                hero_name = input('That\'s too long! (Max 10). What is your name, hero?:\n').title()
            if len(hero_name) > 0:
                print(f'{hero_name}, ah yes. That name carries great respect!')

            else:
                print('Ah, the quiet type huh? I\'ll just call you Steve.')
                hero_name = 'Steve'

            hero_profession = select_from_list(list(get_data_from_loc_str(data, 'heroes/bases').keys()),
                                               q=f'Now, {hero_name}, What is your profession?:\n')
            print(f'You look like a great {hero_profession}, {hero_name}. I should have guessed.')
            our_hero = self.create_character(hero_name, hero_profession)
            print(our_hero.show_stats())
            return our_hero

        while True:
            our_hero = roll_hero()
            keep_hero = select_from_list(['Yes', 'No'], q='Do you want to keep this Hero?').lower()

            if keep_hero == 'yes':
                our_hero.hero = True
                return our_hero
            else:
                continue

    def count_kills(self, enemy_party):
        for dead_enemy in enemy_party.dead_members:
            self.kill_count[dead_enemy.u_type] += 1

    def adventure(self):
        event = randrange(3)
        print(event)
        if event == 0:
            print(f'You found another traveler You talk for a while and have a great time!')
            traveler = Hero.generate_unit('heroes/bases/rng', self.party.hero.level)
            # TODO: print traveler item card here
            choice = select_from_list(['Yes', 'No'],
                                      'The traveler offers to join your party, what do you say?', False, True)
            # traveler = self.create_random_character(cls=Hero)
            if choice == 'Yes':
                self.party.add_member(traveler)
            elif choice == 'No':
                print('You bid the traveler farewell and continue on your way.\n')

        elif event == 1:
            p1 = create_random_item(2)
            self.party.display_single_item_card(p1)
            self.party.inventory.append(p1)
            print(f'You find an item and toss it in your bag and keep moving.')
        elif event == 2:
            p1 = create_random_item(1)
            self.party.display_single_item_card(p1)
            self.party.inventory.append(p1)
            print(f'You find an item and toss it in your bag and keep moving.')

        else:
            print('\nA tree falls on the party!')
            for member in self.party.members:
                member.set_hp(-20)

    def inventory(self):
        self.party.inventory_menu()

    def camp(self):
        camp_input = select_from_list(['Inventory', 'Rest', 'Craft', 'Continue Adventuring', 'Save', 'Title Screen', 'Exit'],
                                      f'What would you like to do:\n', False, True)
        if camp_input == 'Rest':
            for member in self.party.members:
                member.set_hp(full=True)
                member.set_mana(full=True)
        elif camp_input == 'Inventory':
            self.party.inventory_menu()
        elif camp_input == 'Craft':
            print('You need a craftsman.')
            self.camp()
        elif camp_input == 'Exit':
            print('You Head back out into the wilds..')
        elif camp_input == 'Save':
            self.save()
        elif camp_input == 'Title Screen':
            restart = select_from_list(['Yes', 'No'], q='All unsaved progress will be lost. Are you sure?', horizontal=True)
            if restart == 'Yes':
                self.start()
            else:
                self.camp()

    def main_options(self):
        """
        Contains Choices after new game and settings
        """
        print('*' * 100)
        choice_list = ['Adventure', 'Camp']
        if self.kill_count['trash'] > 5:
            choice_list.append('Boss Fight')
        choice_list.append('Party Info')
        choice = select_from_list(choice_list, f'\nWhat would you like to do\n ', index_pos=False, horizontal=True)
        if choice == 'Adventure':
            event_loc_str = self.world_map.run()

            if event_loc_str == 'random':
                is_fight_trash = 50 < random.randint(0, 100)
                if is_fight_trash:
                    event_loc_str = 'events/default/rng'
                    event = get_data_from_loc_str(data, event_loc_str)

                    self.event_handler(event)
                else:
                    self.adventure()
            elif event_loc_str == 'Camp':
                print('\n' * 20)
                print(vfx.camp_fire + '\n')
                print('  You build a beautiful camp fire.\n')
                self.camp()
            else:
                print(f'This will trigger a specific event once it is implemented')

                event_keys = get_keys_from_loc_str(data, event_loc_str)
                event = get_data_from_keys(data, event_keys)
                self.event_handler(event)
        elif choice == 'Camp':
            print('\n' * 20)
            print(vfx.camp_fire + '\n')
            print('  You build a beautiful camp fire.\n')
            self.camp()
        elif choice == 'Party Info':
            self.party.print_members_info_cards()
        elif choice == 'Boss Fight':
            enemy_party = Party.generate(self)
            enemy_party.add_member(
                NPC.generate_unit('enemies/boss/rng', self.party.hero.level),
                p=False)
            player_won = clock_tick_battle(self.party, enemy_party)
            if player_won:
                for member in self.party.members:
                    member.add_xp(enemy_party.party_worth_xp())
                self.count_kills(enemy_party)

    def game_over(self):
        print('Game Over, Thanks for playing!')

        quit()

    def gameloop(self):
        while self.party.has_units_left:
            self.main_options()

        self.game_over()

    def event_handler(self, event):
        clear_screen()
        for line in event["texts"]["start"]:
            print(f'{line:^80}')  # end='\n')
            sleep(0.5)
        print('')
        input('Press enter.')
        if event['enemies']:
            enemy_party = Party(self)
            for enemy_loc_str in event['enemies']:
                #  generate enemy
                level = self.party.hero.level
                # enemy = get_data_from_loc_str(data, enemy_loc_str)
                #
                #
                # enemy_keys = get_keys_from_loc_str(data, enemy_loc_str)
                enemy_party.add_member(
                    NPC.generate_unit(enemy_loc_str, level),
                    p=False)

            # print(f'enemy party: {enemy_party}')
            enemy_units_left = clock_tick_battle(self.party, enemy_party)
            vfx.clear_screen()
            if not enemy_units_left:
                xp = event['loot']['xp'] + enemy_party.party_worth_xp()
                for member in self.party.members:
                    member.add_xp(xp)

                # TODO: award loot here? would mean only loot for fights
                input('Press enter.')
            else:
                if self.party.has_units_left:
                    print(f'You got away.')
            self.count_kills(enemy_party)
        for char_loc_str in event.get('party_add', []):
            new_member = Hero.generate_unit(char_loc_str, self.party.members[0].level)
            print(f'{new_member.name}, the {new_member.profession}, lvl: {new_member.level}')

            add_choice = select_from_list(['Yes', 'No'], q=f'Do you want {new_member.name} to join your Party?',
                                          index_pos=False, horizontal=True)
            if add_choice == 'Yes':
                self.party.add_member(new_member)
        vfx.clear_screen()
        for line in event["texts"]["end"]:
            print(f'{line:^80}')  # end='\n')
            sleep(0.5)
        input('Press enter.')


    def serialize(self):
        dummy = self.__dict__.copy()
        dummy['party'] = dummy['party'].serialize()
        dummy['world_map'] = dummy['world_map'].serialize()
        return dummy

    @classmethod
    def deserialize(cls, save_data):
        dummy = cls()
        dummy.__dict__ = save_data['game'].copy()
        dummy.party = Party.deserialize(dummy.party.copy())
        dummy.party.game = dummy
        dummy.world_map = Class_World_Map.MapManager.deserialize(dummy.world_map.copy())
        dummy.world_map.game = dummy
        return dummy

    def save(self):
        file_name = self.choose_save_name()
        file = os.path.join(project_path, 'saves', file_name)
        with open(file, 'w') as f:
            json.dump({'game': self.serialize()}, f, indent=4)

    def choose_save_name(self):
        file_name = input(f'Choose a name for the save file:') + save_file_extention
        if file_name in os.listdir(save_folder):
            overwrite = select_from_list(['Yes', 'No'], q='File already exists. Overwrite?')
            if overwrite == 'No':
                file_name = self.choose_save_name()
        return file_name

    @classmethod
    def load(cls):
        fn = os.path.join(project_path, save_folder, cls.choose_load_game())
        with open(fn, 'r') as f:
            load_data = json.load(f)
        load_game = cls.deserialize(load_data)
        return load_game

    @classmethod
    def choose_load_game(cls):
        return select_from_list(get_save_games(), q='Which game do you want to load?') + save_file_extention

    @classmethod
    def new_game(cls):
        game = cls()
        game.party = Party.generate(game)
        game.Mode = select_from_list(['Normal', 'AutoCombat'],
                                     'What mode would you like? ** Recommended: Normal **', False, True)
        game.difficulty = select_from_list(['Easy', 'Medium', 'Hard'], 'Choose your difficulty:')
        print(f'You selected: {game.difficulty}!')
        game.party.add_member(game.create_hero())
        print(f'You are all set! Danger is that way, Good Luck, {game.party.member().name}!\n')
        return game

    @classmethod
    def start(cls):
        saves_files = get_save_games()
        options = ['New Game']
        if len(saves_files) > 0:
            options.append('Load Game')
        game_choice = select_from_list(options, horizontal=True)
        if game_choice == 'New Game':
            game = cls.new_game()
        else:
            game = cls.load()
        game.gameloop()


if __name__ == '__main__':
    Game.start()
