import json
import copy
import os

from x_Attack_Setups import *
import x_Spell_Setups
from Item_Bases import *
import battle
from types import SimpleNamespace
from data_src import data

test_weapon = {
            'base_stats': {
                'vit': 1,
                'dex': 2,
                'str': 0,
                'int': 0,
                'agility': 1,
                'toughness': 1,
            },
            'stats': {
                'max_hp': 13,
                'max_mana': 10,
                'armor': 0,
                'magic_resistance': 0,
                'speed': 0,
                'dodge': 0,
                'crit_chance': 2,
                'crit_dmg': 20,
                'elemental_resistance': 10,
                'wpn_dmg': 5,
            },
            'attack_name': 'single_attack_setup',
            'attack_setup': weapon_setups['single_attack_setup'],
        }


class NPC:

    def __init__(self, name='Mr. Lazy', profession='str_class', level=1, new_char=True, type='trash_mob'):
        """
        Create new person """

        self.hero = False
        self.name = name
        self.profession = profession
        self.party = None  # Only one party at a time
        self.type = type

        self.level = 1
        self.xp = 0
        self.next_level = 20
        self.worth_xp = 5

        self.base_stats = {
                            'vit': 1,
                            'dex': 1,
                            'str': 1,
                            'int': 1,
                            'agility': 1,
                            'toughness': 1,
                        }

        # rewrite base stats for class_type from setup file TODO: move to generator
        class_data = self.get_class_data()

        for stat in class_data['base'].keys():
            self.base_stats[stat[:-6]] = class_data['base'][stat]

        self.spell_book = [x_Spell_Setups.heal.copy(), x_Spell_Setups.base_spell.copy()]

        self.equip_slots = {'Main Hand': Weapon.generate(quality='Common', quality_val=1, etype='Weapon',
                                                         equipable_slot='Main Hand',
                                                         att_dmg_min=1, att_dmg_max=3),
                            'Off Hand': None,
                            'Head': None,
                            'Chest': None,
                            'Legs': None,
                            'Feet': None,
                            'Ring': None,
                            'Necklace': None,
                            }

        # self.tracked_values = 'test'
        self.tracked_values = {
            'ct': 1000,
            'c': 0, 'status_effects': [],
            'hp': 1,
            'mana': 1
        }

        if new_char:
            level_up_counter = 1
            while level_up_counter < level:
                self.level_up(p=False)
                level_up_counter += 1
        # self.calculate_stats_with_equipment()

        # TODO: why is this? fix mana and hp init
        self.tracked_values['hp'] = self.max_hp
        self.tracked_values['mana'] = self.max_mana

    def get_conversion_ratios(self):
        return data.conversion_ratios

    def get_data(self):
        return data.enemys

    def get_class_data(self):
        # TODO: make get_class_data work for enemy stats and move tho to hero
        class_key = self.profession
        mob_type = self.type
        return self.get_data()[mob_type][class_key]

    def get_stat_from_equipment(self, stat, base_stat=True):
        gear = self.get_equipped_items()
        # gear = [value for value in self.equip_slots.values() if value]
        if base_stat:
            stat_key = 'base_stats'
        else:
            stat_key = 'stats'
        return sum([item.__getattribute__(stat_key).get(stat, 0) for item in gear])

    # base_stat_list = ['vit', 'dex', 'str', 'int', 'agility', 'toughness']
    def get_status_effects(self):
        return self.tracked_values['status_effects']

    def get_stat_from_status_effect(self, stat, base_stat=True):
        items = self.get_status_effects()
        flat_stats = sum([item.get('flat_'+stat, 0) for item in items])
        # print('flat', flat_stats)
        pct_stats = sum([item.get('pct_'+stat, 0) for item in items])
        # print('pct', pct_stats)
        all_flat = sum([self.__getattribute__('full_' + stat), flat_stats])
        # print('all', all_flat)
        return all_flat + (all_flat * (pct_stats / 100))

    # full_ values are for display only
    @property
    def full_vit(self):
        stat = 'vit'
        return self.base_stats[stat] + self.get_stat_from_equipment(stat)

    @property
    def full_dex(self):
        stat = 'dex'
        return self.base_stats[stat] + self.get_stat_from_equipment(stat)

    @property
    def full_str(self):
        stat = 'str'
        return self.base_stats[stat] + self.get_stat_from_equipment(stat)

    @property
    def full_int(self):
        stat = 'int'
        return self.base_stats[stat] + self.get_stat_from_equipment(stat)

    @property
    def full_agility(self):
        stat = 'agility'
        return self.base_stats[stat] + self.get_stat_from_equipment(stat)

    @property
    def full_toughness(self):
        stat = 'toughness'
        return self.base_stats[stat] + self.get_stat_from_equipment(stat)

    @property
    def vit(self):
        return round(self.get_stat_from_status_effect('vit', base_stat=True))

    @property
    def dex(self):
        return round(self.get_stat_from_status_effect('dex', base_stat=True))

    @property
    def str(self):
        return round(self.get_stat_from_status_effect('str', base_stat=True))

    @property
    def int(self):
        return round(self.get_stat_from_status_effect('int', base_stat=True))

    @property
    def agility(self):
        return round(self.get_stat_from_status_effect('agility', base_stat=True))

    @property
    def toughness(self):
        return round(self.get_stat_from_status_effect('toughness', base_stat=True))


# deriving stats
    #  full values are for display only
    @property
    def full_speed(self):
        stat = 'speed'
        conversion_ratios = self.get_conversion_ratios()
        speed_per_dex = conversion_ratios['dex_to_speed']['speed_per_dex']
        speed_per_agility = conversion_ratios['dex_to_speed']['speed_per_agility']
        speed_factor = conversion_ratios['dex_to_speed']['speed_factor']
        speed_start = conversion_ratios['dex_to_speed']['speed_start']

        speed_from_dex = self.dex * speed_per_dex
        speed_from_agility = self.agility * speed_per_agility
        speed = (speed_from_dex + speed_from_agility) * speed_factor + speed_start
        return speed + self.get_stat_from_equipment(stat, base_stat=False)

    @property
    def full_max_hp(self):
        stat = 'max_hp'
        conversion_ratios = self.get_conversion_ratios()
        hp_start = conversion_ratios['vit_to_hp']['start']
        hp_per_vit = conversion_ratios['vit_to_hp']['hp_per_vit']
        hp_per_lvl = conversion_ratios['vit_to_hp']['hp_per_lvl']
        max_hp = self.vit * hp_per_vit + self.level * hp_per_lvl + hp_start
        return max_hp + self.get_stat_from_equipment(stat, base_stat=False)

    @property
    def full_crit_chance(self):
        stat = 'crit_chance'
        conversion_ratios = self.get_conversion_ratios()
        crit_chance_start = conversion_ratios['dex_to_crit']['chance_start']
        crit_chan_per_level = conversion_ratios['dex_to_crit']['crit_chan_per_level']
        crit_chan_per_dex = conversion_ratios['dex_to_crit']['crit_chan_per_dex']

        crit_chance_from_dex = self.dex * crit_chan_per_dex
        crit_chance_from_lvl = self.level * crit_chan_per_level
        crit_chance = crit_chance_from_dex + crit_chance_from_lvl + crit_chance_start
        return crit_chance + self.get_stat_from_equipment(stat, base_stat=False)

    @property
    def full_crit_dmg(self):
        stat = 'crit_dmg'
        conversion_ratios = self.get_conversion_ratios()
        crit_dmg_start = conversion_ratios['dex_to_crit']['dmg_start']
        crit_dmg_per_level = conversion_ratios['dex_to_crit']['crit_dmg_per_level']
        crit_dmg_per_dex = conversion_ratios['dex_to_crit']['crit_dmg_per_dex']

        crit_dmg_from_dex = self.dex * crit_dmg_per_dex
        crit_dmg_from_level = self.level * crit_dmg_per_level
        crit_dmg = crit_dmg_from_dex + crit_dmg_from_level + crit_dmg_start
        return crit_dmg + self.get_stat_from_equipment(stat, base_stat=False)

    @property
    def full_dodge(self):
        stat = 'dodge'
        conversion_ratios = self.get_conversion_ratios()
        dodge_start = conversion_ratios['dex_speed_to_dodge']['start']
        dodge_per_speed = conversion_ratios['dex_speed_to_dodge']['dodge_per_speed']
        dodge_per_dex = conversion_ratios['dex_speed_to_dodge']['dodge_per_dex']

        dodge_from_dex = self.dex * dodge_per_dex
        dodge_from_speed = self.speed * dodge_per_speed
        dodge = dodge_from_dex + dodge_from_speed + dodge_start
        return dodge + self.get_stat_from_equipment(stat, base_stat=False)

    @property
    def full_armor(self):
        stat = 'armor'
        conversion_ratios = self.get_conversion_ratios()
        armor_per_str = conversion_ratios['str_to_armor']['armor_per_str']
        armor_per_lvl = conversion_ratios['str_to_armor']['armor_per_level']
        armor_per_toughness = conversion_ratios['toughness_to_armor']['armor_per_toughness']

        armor_from_str = (self.str * armor_per_str) + (self.level * armor_per_lvl)
        armor_from_toughness = self.toughness * armor_per_toughness
        armor = armor_from_str + armor_from_toughness
        return armor + self.get_stat_from_equipment(stat, base_stat=False)

    # TODO: find a formula for max mana
    @property
    def full_max_mana(self):
        stat = 'max_mana'
        return (20 + 5 * self.level) + self.get_stat_from_equipment(stat, base_stat=False)

    # TODO: find a formula for mana regen
    @property
    def full_mana_regen(self):
        stat = 'mana_regen'
        return 2 + self.get_stat_from_equipment(stat, base_stat=False)

    @property
    def full_elemental_resistance(self):
        stat = 'elemental_resistance'
        return self.get_stat_from_equipment(stat, base_stat=False)

    @property
    def full_magic_resistance(self):
        stat = 'magic_resistance'
        return self.get_stat_from_equipment(stat, base_stat=False)

    @property
    def full_wpn_dmg(self):
        stat = 'wpn_dmg'
        return self.get_stat_from_equipment(stat, base_stat=False)

    # derived stats to use
    @property
    def speed(self):
        return round(self.get_stat_from_status_effect('speed', base_stat=False),1)

    @property
    def dodge(self):
        return round(self.get_stat_from_status_effect('dodge', base_stat=False),1)

    @property
    def max_hp(self):
        return round(self.get_stat_from_status_effect('max_hp', base_stat=False))

    @property
    def crit_chance(self):
        return round(self.get_stat_from_status_effect('crit_chance', base_stat=False),1)

    @property
    def crit_dmg(self):
        return round(self.get_stat_from_status_effect('crit_dmg', base_stat=False),1)

    @property
    def max_mana(self):
        return round(self.get_stat_from_status_effect('max_mana', base_stat=False))

    @property
    def mana_regen(self):
        return self.get_stat_from_status_effect('mana_regen', base_stat=False)

    @property
    def armor(self):
        return round(self.get_stat_from_status_effect('armor', base_stat=False))

    @property
    def wpn_dmg(self):
        return self.get_stat_from_status_effect('wpn_dmg', base_stat=False)

    @property
    def elemental_resistance(self):
        return round(self.get_stat_from_status_effect('elemental_resistance', base_stat=False),0)

    @property
    def magic_resistance(self):
        return self.get_stat_from_status_effect('magic_resistance', base_stat=False)

    @property
    def hp(self):
        return self.tracked_values['hp']

    @property
    def mana(self):
        return self.tracked_values['mana']

    @property
    def attack_dmg(self):
        dmg_base = self.equip_slots['Main Hand'].attack_setup['dmg_base']
        dummy_target = SimpleNamespace(hp=1, max_hp=1)
        # TODO: get dot notation for the dummy going
        return battle.generate_dmg(self, dummy_target, dmg_base=dmg_base)

    def stat_growth(self):
        class_data = self.get_class_data()
        for stat in class_data['per_lvl'].keys():
            self.base_stats[stat[:-6]] += class_data['per_lvl'][stat]

    def level_up(self, p=True):
        self.level += 1
        self.xp -= self.next_level
        self.next_level = round(4 * (self.level ** 3) / 5) + 20
        if p:
            print(f'{self.name} is now level {self.level}!')
        self.stat_growth()
        # self.calculate_stats_with_equipment()
        self.set_hp(full=True)
        self.set_mana(full=True)

    @property
    def is_alive(self) -> bool:
        return self.tracked_values['hp'] > 0

    def set_hp(self, amount=1, full=False):
        """
        set the hp safely
        :param full: set True to fully heal char
        :param amount: int: to change / can be positive or negative
        :return: amount
        """
        if full:
            self.tracked_values['hp'] = self.max_hp
        else:
            self.tracked_values['hp'] = min(self.tracked_values['hp'] + amount, self.max_hp)
            if self.tracked_values['hp'] < 0:
                self.tracked_values['hp'] = 0

    def set_mana(self, amount=1, full=False):
        """
        set the mana safely
        :param full: set True to fully heal char
        :param amount: int: to change / can be positive or negative
        :return: amount
        """
        if full:
            self.tracked_values['mana'] = self.max_mana
        else:
            self.tracked_values['mana'] = min(self.tracked_values['mana'] + amount, self.max_mana)
            if self.tracked_values['mana'] < 0:
                self.tracked_values['mana'] = 0

    def add_status_effect(self, status_effect, p=True):
        self.tracked_values['status_effects'].append(status_effect.copy())
        if p:
            print(f'{self.name} {status_effect["msg"]}')

    def remove_status_effect(self, status_effect, p=True):
        self.tracked_values['status_effects'].remove(status_effect)
        if p:
            print(f'{self.name} no longer {status_effect["msg"]}')

    def choose_target(self, target_party):
        """
        picks random target from target_party.members
        :param target_party: party instance
        :return: person from party
        """
        if len(target_party) > 1:
            if self.party.has_hero() or self.party.game.difficulty == 'Medium':
                choice = random.randrange(len(target_party))
                target = target_party[choice]
            else:
                if self.party.game.difficulty == 'Hard':
                    target = min(target_party, key=lambda member: member.tracked_values['hp'])
                elif self.party.game.difficulty == 'Easy':
                    target = max(target_party, key=lambda member: member.tracked_values['hp'])
        else:
            target = target_party[0]
        return target

    def choose_attack(self, attack_options):
        choice = random.choice([i for i in range(len(attack_options))])
        return choice

    def choose_battle_action(self, possible_actions):
        """
        ENDPOINT for battle
        npc will always choose basic attack
        :param possible_actions:
        :return: -
        """
        # TODO: add logic to choose spells
        possible_actions = ['attack', ]
        if self.party.game.difficulty == 'Medium':
            heal_under = 0.2
        elif self.party.game.difficulty == 'Hard':
            heal_under = 0.3
        else:
            heal_under = 0.05

        # if self.hp / self.max_hp < heal_under:
        #     possible_actions.append('heal')
        action = random.choice(possible_actions)
        return action

    def show_gear(self):
        items = [self.equip_slots['Main Hand'],
                 self.equip_slots['Off Hand'],
                 self.equip_slots['Head'],
                 self.equip_slots['Chest'],
                 self.equip_slots['Legs'],
                 self.equip_slots['Feet'],
                 self.equip_slots['Ring'],
                 self.equip_slots['Necklace']]
        gear = [item for item in items if item]
        for i in gear:
            print(i.item)

    def get_equipped_items(self):
        """
        :return: list of currently equipped items
        """
        return [value for value in self.equip_slots.values() if value]

    def add_xp(self, xp):
        self.xp += xp
        print(f'{self.name} gained {xp} xp!')
        if self.xp > self.next_level:
            self.level_up()


    def info_card(self):

        name = f'{self.name}'
        prof = f'{self.profession}'

        hp = f'HP: {self.hp:>3}/{self.max_hp:<3}'  # 10
        defense = f'Def: {self.armor}'  # 8

        lvl = f'Lvl: {self.level}'
        xp = f'XP: {self.xp}/{self.next_level}'

        stats_str = f'Str: {self.str}'  # Trying 3 probly 2
        stats_dex = f'Dex: {self.dex}'
        stats_int = f'Int: {self.int}'

        dmg_w = 'DMG: '
        dmg_stat = f'{self.wpn_dmg}/{self.attack_dmg}'  # 11  # TODO: get calculated dmg?
        crit_w = f'Crit %: '
        crit_stat = f'{self.crit_chance:>2}/{self.crit_dmg:<3}'  # 15

        # Combine L an R lines
        name = f'{name:<1}{prof:>{21 - len(name)}}'
        level_xp = f'{lvl}{xp:>{21 - len(lvl)}}'
        hp_def = f'{hp}{defense:>{21 - len(hp)}}'
        stats = f'{stats_str:<7}{stats_dex:<7}{stats_int:<7}'
        dmg = f'{dmg_w}{dmg_stat:>{21 - len(dmg_w)}}'
        crit = f'{crit_w}{crit_stat:>{21 - len(crit_w)}}'
        return [name, level_xp, hp_def, stats, dmg, crit]

    def show_stats(self):
        print(f'\n{self.name},the {self.profession}\n'
              f'Level:\t{self.level:>4}  XP: {self.xp:>6}/{self.next_level}\n'
              f'HP:\t   {self.tracked_values["hp"]}/{self.max_hp:<4}\n'
              f'Str:\t   {self.str:<3}Damage: {self.wpn_dmg:>3}/{self.attack_dmg:<3}\n' 
              f'Dex:\t   {self.dex:<3}Crit:  {self.crit_chance}%/{self.crit_dmg}%\n'
              f'Int:\t   {self.int:<3}Defence: {self.armor:>5}\n')

    def show_combat_stats(self):
        name = f'{self.name}, the {self.profession}'
        hp = f'Hp: {self.hp:>2}/{self.max_hp:<2}'
        dmg = f'Dmg: {self.wpn_dmg:>2}/{self.attack_dmg:<2}'  # TODO: get calculated stats?
        return f'{name:^23} ' \
               f'{hp:<8} ' \
               f'{dmg:<13}'

    def hp_bar(self, length=10, f_color=bcolors.FAIL, m_color=bcolors.FAIL,
               f_char='♥', m_char='-', no_color=False, border='|'):
        '''
        returns a string of an hp_bar for current hp / max hp

        :param border: added at the beginning and the ned of the string
        :param no_color: bool: removes special chars for colors
        :param length: int: length of the bar without border - number of chars
        :param f_color: color code : for filled ticks
        :param m_color: color code : for missing ticks
        :param f_char: str: char to display for filled ticks
        :param m_char: str: char to be displayed for not filled ticks
        :return: hp bar as string
        '''
        bar = BarGFX(self.hp, self.max_hp, length=length, f_color=f_color,
                     m_color=m_color, f_char=f_char, m_char=m_char)
        return bar.bar_str(no_color=no_color, border=border)

    def xp_bar(self, length=10, f_color=bcolors.OKBLUE, m_color=bcolors.OKGREEN,
               f_char='|', m_char='-', no_color=True, border=''):
        '''
        returns a string of an xp_bar for current xp / next_level

        :param border: added at the beginning and the ned of the string
        :param no_color: bool: removes special chars for colors
        :param length: int: length of the bar without border - number of chars
        :param f_color: color code : for filled ticks
        :param m_color: color code : for missing ticks
        :param f_char: str: char to display for filled ticks
        :param m_char: str: char to be displayed for not filled ticks
        :return: xp bar as string
        '''
        bar = BarGFX(self.xp, self.next_level, length=length, f_color=f_color,
                     m_color=m_color, f_char=f_char, m_char=m_char)
        return bar.bar_str(no_color=no_color, border=border)

    def mana_bar(self, length=10, f_color=bcolors.HeadER, m_color=bcolors.OKGREEN,
               f_char='#', m_char='-', no_color=False, border='|'):
        '''
        returns a string of an xp_bar for current xp / next_level

        :param border: added at the beginning and the ned of the string
        :param no_color: bool: removes special chars for colors
        :param length: int: length of the bar without border - number of chars
        :param f_color: color code : for filled ticks
        :param m_color: color code : for missing ticks
        :param f_char: str: char to display for filled ticks
        :param m_char: str: char to be displayed for not filled ticks
        :return: xp bar as string
        '''
        bar = BarGFX(self.mana, self.max_mana, length=length, f_color=f_color,
                     m_color=m_color, f_char=f_char, m_char=m_char)
        return bar.bar_str(no_color=no_color, border=border)

    def __repr__(self):
        return self.name

    def __str__(self):
        return f'{self.name}, the {self.profession}'

    @classmethod
    def generate(cls, name='Jeb', profession='Warrior', level=1, new_char=True, type='trash_mob'):
        """
        Create new character at level 1
        """
        return cls(name, profession, level, new_char, type)

    @classmethod
    def generate_random(cls, level=1, type='trash_mob'):
        """
        Create new random character at level 1
        """
        level = level
        # name = random.choice(['Lamar', 'Colin', 'Ali', 'Jackson', 'Minky',
        #                       'Leo', 'Phylis', 'Lindsay', 'Tongo', 'Paku', ])
        # profession = random.choice(['Warrior', 'Archer', 'Mage', 'Blacksmith', 'Thief', 'Bard'])

        profession = random.choice([p for p in data.enemys[type].keys()])
        name = random.choice(data.enemys[type][profession]['names'])
        # TODO: move level setting to game.create_char
        flat_level = data.enemys[type][profession].get('flat_lvl', None)
        if flat_level:
            level = flat_level
        else:
            low_lvl = data.enemys[type][profession]['meta'].get('low_lvl', level)
            high_lvl = data.enemys[type][profession]['meta'].get('high_lvl', level)
            lvl_mod = random.randint(low_lvl, high_lvl)
            level += lvl_mod
        # if name == 'Minky':
        #     profession = 'Miffy Muffin'
        # if name == 'Colin':
        #     profession = 'Bard of Bass'
        return cls(name, profession, level, type=type)

    def serialize(self):
        dummy = copy.deepcopy(self.__dict__)
        for key, item in dummy['equip_slots'].items():
            if item:
                dummy['equip_slots'][key] = item.serialize()
        dummy['party'] = None
        return dummy

    @classmethod
    def deserialize(cls, save_data):
        dummy = cls.generate(new_char=False)
        dummy.__dict__ = save_data.copy()
        for key, item in dummy.equip_slots.items():
            if item:
                dummy.equip_slots[key] = Equipment.deserialize(item)
        return dummy
