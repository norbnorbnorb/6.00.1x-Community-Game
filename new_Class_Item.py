import random
import data_src
import vfx

sWeights = (6, 44, 28, 18, 4)
sList = ['Rusty', 'Common',
         'Great', 'Magical',
         'Legendary']
sValue = {'Rusty': 0.8, 'Common': 1,
          'Great': 1.5, 'Magical': 2,
          'Legendary': 2.5}


class Equipment:
    def __init__(
            self, quality, quality_val, etype, equipable_slot, value,
            max_durability, durability, name,
            base_stats, stats, attack
            ):
        self.quality = str(quality)
        self.quality_val = quality_val
        self.value = value
        self.max_durability = max_durability
        self.durability = durability
        self.etype = etype
        self.equipable_slot = equipable_slot
        self.name = name

        self.base_stats = base_stats
        self.stats = stats
        self.attack = attack

    # @property
    # def attack_base(self):
    #     return data_src.get_data_from_loc_str(data_src.data, self.attack).get("dmg_base")

    @classmethod
    def generate(cls, item_loc_str, level, quality='rng'):
        if quality == 'rng':
            quality = random.choices(sList, weights=sWeights, k=1)[0]
        quality_val = sValue.get(quality)

        keys = data_src.get_keys_from_loc_str(data_src.data, item_loc_str)
        file, cls_type, item_class, item_id = keys
        item_data = data_src.get_data_from_keys(data_src.data, keys)
        print(item_data)
        etype = item_class
        equipable_slot = item_data.get('equipable_slot')

        level_mod = 1 + level * 0.5  # TODO: move item level mod to setup file, add drop chances somewhere

        base_stat_list = ['vit', 'dex', 'str', 'int', 'agility', 'toughness']
        base_stats = {}
        value = 10
        for stat in base_stat_list:
            base_stats[stat] = item_data["base_stats"].get(stat, 0)
            if base_stats[stat] > 0:
                base_stats[stat] = base_stats[stat] + random.randint(0, level)
                base_stats[stat] = round(base_stats[stat] * quality_val * level_mod)
                value += base_stats[stat]

        value = int(value * quality_val)

        stats = {
            'max_hp': round(item_data["stats"].get('max_hp', 0) * quality_val * level_mod),
            'max_mana': round(item_data["stats"].get('max_mana', 0) * quality_val * level_mod),
            'armor': round(item_data["stats"].get('armor', 0) * quality_val * level_mod),
            'magic_resistance': round(item_data["stats"].get('magic_resistance', 0) * quality_val * level_mod),
            'speed': round(item_data["stats"].get('speed', 0) * quality_val * level_mod),
            'dodge': round(item_data["stats"].get('dodge', 0) * quality_val * level_mod),
            'crit_chance': round(item_data["stats"].get('crit_chance', 0) * quality_val * level_mod),
            'crit_dmg': round(item_data["stats"].get('crit_dmg', 0) * quality_val * level_mod),
            'elemental_resistance': round(item_data["stats"].get('elemental_resistance', 0) * quality_val * level_mod),
            'wpn_dmg': round(item_data["stats"].get('wpn_dmg', 0) * quality_val * level_mod),
        }
        attack = item_data.get('attack', None)

        name = item_data.get('name', None)

        max_durability = 10
        durability = max_durability
        return cls(quality, quality_val, etype, equipable_slot, value,
                   max_durability, durability, name,
                   base_stats, stats, attack)

    @classmethod
    def generate_random(cls, level, e_type='rng', e_slot='rng', quality='rng', main_stat='rng'):
        e_types = {
            "weapon": ['Main Hand', 'Off Hand'],
            "armor": ['Head', 'Chest', 'Legs', 'Feet'],
        }

        quality_attrib_amount = {'Rusty': 0, 'Common': 1,
                                 'Great': 2, 'Magical': 3,
                                 'Legendary': 4}

        name = ''

        level_mod = 0.5 + level * 0.5

        if e_type == 'rng':
            e_type = random.choice(list(e_types))
        if e_slot == 'rng':
            e_slot = random.choice(list(e_types[e_type]))
        if quality == 'rng':
            quality = random.choices(sList, weights=sWeights, k=1)[0]
        quality_val = sValue.get(quality)

        name += quality

        main_base_stats = ['dex', 'str', 'int']
        secondary_base_stats = ['vit', 'toughness', 'agility']
        derived_stats = ['max_hp', 'max_mana', 'armor', 'magic_resistance',
                         'speed', 'dodge', 'crit_chance', 'crit_dmg',
                         'elemental_resistance']

        if main_stat == 'rng':
            main_stat = random.choice(main_base_stats)

        added_stats = [random.choice(secondary_base_stats)
                       for _ in range(quality_attrib_amount[quality])]

        # print(f'main: {main_stat} added: {added_stats}, combined: {added_stats + [main_stat]}')
        item_subtype = random.choice(list(data_src.data['equipment_bases'][e_type]))
        item_data = data_src.data['equipment_bases'][e_type][item_subtype]
        base_stats = item_data.get('base_stats', {})
        stats = item_data.get('stats', {})

        if e_type == 'weapon':
            attack_options = []
            main_stat_attacks = data_src.search_loc('primary_attacks', 'dmg_base', main_stat, 'both')
            print(f'q: {quality}, ms: {main_stat}')

            # todo: get base stats from item class and add item class name to item_name

            for a in main_stat_attacks:
                # print(f'k: {a[1]} ')
                if quality in a[1]['quality']:
                    attack_options.append(a[0])
            attack = random.choice(attack_options)
            attack = 'primary_attacks/' + attack
            wpn_dmg = level + random.randint(0, level)
            stats['wpn_dmg'] += max(1, round(wpn_dmg * quality_val * level_mod))
            attack_data = data_src.get_data_from_loc_str(data_src.data, attack)
            name_prefix = f' {attack_data.get("name_suffix", "basic")}'
            # name += f' {attack}'
        else:
            stats['wpn_dmg'] = 0
            attack = None
            if main_stat == 'dex':
                name_prefix = 'Swift'
            elif main_stat == 'str':
                name_prefix = 'Mighty'
            elif main_stat == 'int':
                name_prefix = 'Smart'

        name += ' ' + name_prefix + ' ' + item_subtype

        value = 10
        # base_stats = {}
        for stat in main_base_stats + secondary_base_stats:
            base_stats[stat] = base_stats.get(stat, 0)

            if stat in added_stats + [main_stat]:
                base_stats[stat] += random.randint(0, level)  # + random.randint(0, level)
                base_stats[stat] = round(base_stats[stat] * (quality_val / 2) * level_mod + level)
                value += base_stats[stat]

        for stat in derived_stats:
            stats[stat] = round(stats.get(stat, 0) * quality_val * 2)
        # stats = {}

        max_durability = 10
        durability = max_durability
        return cls(quality, quality_val, e_type, e_slot, value,
                   max_durability, durability, name,
                   base_stats, stats, attack)



    def serialize(self):
        return self.__dict__.copy()

    @classmethod
    def deserialize(cls, save_data):
        dummy = cls(**save_data)
        return dummy

    def __repr__(self):
        return f'{self.name} {self.etype}: {self.equipable_slot}'

    def __str__(self):
        return f'{self.name} {self.etype}: {self.equipable_slot}'

    @property
    def dmg_base(self):
        if self.attack:
            dmg_base = data_src.get_data_from_loc_str(data_src.data, self.attack).get('dmg_base')
        else:
            dmg_base = None
        return dmg_base

    def show_stats(self):
        name = f'{self.name} {self.quality} {self.etype}'
        slot = f'{self.equipable_slot.title():>9}'
        dmg = f'{self.stats["wpn_dmg"]:>3}-{self.dmg_base:<3}'
        line2_left = f'Dur: {self.durability:>2}/{self.max_durability:<2} '
        line2_right = f'Damage: {dmg}'
        return f'{name:<15}{slot:>15}\n{line2_left:<15}{line2_right:>15}\n'

    def item_card(self):
        if self.etype == 'weapon':
            colors = {
                'dex': vfx.Colors.fg.green,
                'str': vfx.Colors.fg.red,
                'int': vfx.Colors.fg.cyan
            }

            # Line 1
            line_1_left = f'{self.quality} {self.etype}'
            line_1_right = f'{self.equipable_slot}'

            # Line 2
            line_2_left = f'Dur: {self.durability:>2}/{self.max_durability:<2}'

            line_2_right = f'Damage: {self.stats["wpn_dmg"]:>3}-{self.dmg_base:<3}'
        else:

            line_1_left = f'{self.quality} {self.etype}'
            line_1_right = f'{self.equipable_slot}'

            # Line 2
            line_2_left = f'Dur: {self.durability:>2}/{self.max_durability:<2}'

            line_2_right = f'Armor: {self.base_stats["agility"]:>3}-{self.stats["armor"]:<3}'

            # Line 3
            # line_3_left = " " * 15
            # line_3_right = " " * 15
            # if self.enchants[0]:
            #     for enchant, value in self.enchants[0]:
            #         chant1 = f'{enchant}: {value}'
            #         line_3_left = f'{chant1}'
            # if self.enchants[1]:
            #     for enchant, value in self.enchants[1]:
            #         chant2 = f'{enchant}: {value}'
            #         line_3_right = f'{chant2}'

        # Combine L an R lines
        line_1 = f'{line_1_left}{line_1_right:>{30 - len(line_1_left)}}'
        line_2 = f'{line_2_left}{line_2_right:>{30 - len(line_2_left)}}'
        # line_3 = f'{line_3_left}{line_3_right:>{30 - len(line_3_left)}}'
        return [line_1, line_2]  # line_3]



    def info(self):
        return '\n'.join(
            [f"{k.title()}: {str(v).rjust(self._max_left - len(k), ' ')}"
             for k, v in self.__dict__.items() if v and k[0] != '_'])

    def repair(self):
        # TODO: Add repair function
        self.max_durability = int(self.max_durability * 0.9)
