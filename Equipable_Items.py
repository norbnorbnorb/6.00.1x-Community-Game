# Contains base class for equipable items
import random
import string

sWeights = (8, 44, 22, 18, 8)
sList = ['Rusty', 'Common',
         'Great', 'Magical',
         'Legendary']
sValue = {'Rusty': 0.9, 'Common': 1,
          'Great': 1.25, 'Magical': 1.6,
          'Legendary': 2}


class Consumable:
    pass

class Item_card:
    def __init__(self):
        self.item_card = None

    def generate(self):
        pass


class Equipment:
    def __init__(self, quality, quality_value=1, etype='none', equipable_slot='none', value=0,
                 max_durability=10, strength=0, dexterity=0, intelligence=0,
                 max_hp=0, defense=0, att_dmg_min=0, att_dmg_max=0, damage=0,
                 crit_chance=0, crit_multiplier=0):
        self.quality = str(quality)
        self.quality_val = quality_value
        self.value = value + int(10 * quality_value + 10)
        self.max_durability = max_durability
        self.durability = self.max_durability

        self.type = etype
        self.equipable_slot = equipable_slot

        self.str = round(strength * self.quality_val)
        self.dex = round(dexterity * self.quality_val)
        self.int = round(intelligence * self.quality_val)
        self.max_hp = round(max_hp * self.quality_val)
        self.defense = round(defense * self.quality_val)
        self.att_dmg_min = round(att_dmg_min * self.quality_val)
        self.att_dmg_max = round(att_dmg_max * self.quality_val)
        self.damage = round(damage * self.quality_val)
        self.crit_chance = round(crit_chance * self.quality_val)
        self.crit_muliplier = round(crit_multiplier * self.quality_val)

        self._max_left = max(len(k) for k in self.__dict__.keys()) + 10

    @classmethod
    def generate(cls, quality='Common', quality_val=1, etype='Weapon', equipable_slot='main hand', value=0,
                 max_durability=10, strength=0, dexterity=0, intelligence=0,
                 max_hp=0, defense=0, att_dmg_min=0, att_dmg_max=0, damage=0,
                 crit_chance=0, crit_multiplier=0):
        quality = random.choices(sList, weights=sWeights, k=1)[0]
        quality_val = sValue.get(quality)
        return cls(quality, quality_val, etype, equipable_slot, value,
                   max_durability, strength, dexterity, intelligence,
                   max_hp, defense, att_dmg_min, att_dmg_max, damage,
                   crit_chance, crit_multiplier)

    def __repr__(self):
        return self.type + ': ' + self.equipable_slot

    def stats(self):
        return '\n'.join(
            [f"{k.title()}: {str(v).rjust(self._max_left - len(k), ' ')}"
             for k, v in self.__dict__.items()])

    def __str__(self):
        return self.type + ': ' + self.equipable_slot

    def info(self):
        return '\n'.join(
            [f"{k.title()}: {str(v).rjust(self._max_left - len(k), ' ')}"
             for k, v in self.__dict__.items() if v and k[0] != '_'])

    def sell(self):
        # TODO: remove item and add value to player money
        # hero.money += self.value
        # remove from inventory.pop[item_slot]
        # self.del
        pass

    def repair(self):
        # TODO: Add repair function
        self.max_durability = int(self.max_durability * 0.9)


class Weapon(Equipment):
    def __init__(self, quality, quality_val=1, etype='Weapon', equipable_slot='main hand', value=0,
                 max_durability=10, strength=0, dexterity=0, intelligence=0,
                 max_hp=0, defense=0, att_dmg_min=1, att_dmg_max=3, damage=0,
                 crit_chance=1, crit_multiplier=4):
        super(Weapon, self).__init__(quality, quality_val, etype, equipable_slot, value,
                                     max_durability, strength, dexterity, intelligence,
                                     max_hp, defense, att_dmg_min, att_dmg_max, damage,
                                     crit_chance, crit_multiplier)

    @classmethod
    def generate(cls, quality='Common', quality_val=1, etype='Weapon', equipable_slot='main hand', value=0,
                 max_durability=10, strength=0, dexterity=0, intelligence=0,
                 max_hp=0, defense=0, att_dmg_min=1, att_dmg_max=2, damage=0,
                 crit_chance=0, crit_multiplier=0):
        return cls(quality, quality_val, etype, equipable_slot, value,
                   max_durability, strength, dexterity, intelligence,
                   max_hp, defense, att_dmg_min, att_dmg_max, damage,
                   crit_chance, crit_multiplier)

    @classmethod
    def generate_random(cls, etype='Weapon', equipable_slot='main hand', value=0, max_durability=10, strength=0,
                        dexterity=0, intelligence=0,
                        max_hp=0, defense=0, att_dmg_min=1, att_dmg_max=2, damage=0,
                        crit_chance=0, crit_multiplier=0):
        quality = random.choices(sList, weights=sWeights, k=1)[0]
        quality_val = sValue.get(quality)
        equipable_slot = random.choice(['main hand', 'off hand'])
        att_dmg_min *= quality_val
        att_dmg_max = 1 + (random.randint(1, 3) * quality_val)

        return cls(quality, quality_val, etype, equipable_slot, value,
                   max_durability, strength, dexterity, intelligence,
                   max_hp, defense, att_dmg_min, att_dmg_max, damage,
                   crit_chance, crit_multiplier)

    def show_stats(self):
        name = f'{self.quality} {self.type}'
        slot = f'{self.equipable_slot.title():>9}'
        dmg = f'{self.att_dmg_min:>3}-{self.att_dmg_max:<3}'
        line2_left = f'Dur: {self.durability:>2}/{self.max_durability:<2} '
        line2_right = f'Damage: {dmg}'
        return f'{name:<15}{slot:>15}\n{line2_left:<15}{line2_right:>15}\n'


class Armor(Equipment):
    def __init__(self, quality='Common', quality_val=1, etype='Armor', equipable_slot='chest', value=0,
                 max_durability=10, strength=0, dexterity=0, intelligence=0,
                 max_hp=0, defense=1, att_dmg_min=0, att_dmg_max=0, damage=0,
                 crit_chance=0, crit_multiplier=0):
        super(Armor, self).__init__(quality, quality_val, etype, equipable_slot, value,
                                    max_durability, strength, dexterity, intelligence,
                                    max_hp, defense, att_dmg_min, att_dmg_max, damage,
                                    crit_chance, crit_multiplier)

    @classmethod
    def generate(cls, quality='Common', quality_val=1, etype='Armor', equipable_slot='chest', value=0,
                 max_durability=10, strength=0, dexterity=0, intelligence=0, max_hp=0, defense=1,
                 att_dmg_min=0, att_dmg_max=0, damage=0, crit_chance=0, crit_multiplier=0):
        return cls(quality, quality_val, etype, equipable_slot, value,
                   max_durability, strength, dexterity, intelligence,
                   max_hp, defense, att_dmg_min, att_dmg_max, damage,
                   crit_chance, crit_multiplier)

    @classmethod
    def generate_random(cls, etype='Armor', equipable_slot='chest', value=0, max_durability=10,
                        strength=0, dexterity=0, intelligence=0, max_hp=0, defense=0,
                        att_dmg_min=0, att_dmg_max=0, damage=0, crit_chance=0, crit_multiplier=0):
        quality = random.choices(sList, weights=sWeights, k=1)[0]
        quality_val = sValue.get(quality)
        equipable_slot = random.choice(['head', 'chest', 'legs', 'feet'])
        defense = 1 + random.randint(0, 2)

        return cls(quality, quality_val, etype, equipable_slot, value,
                   max_durability, strength, dexterity, intelligence,
                   max_hp, defense, att_dmg_min, att_dmg_max, damage,
                   crit_chance, crit_multiplier)
    @classmethod
    def generate_random1(cls, etype='Armor', equipable_slot='chest', value=0, max_durability=10,
                        strength=0, dexterity=0, intelligence=0, max_hp=0, defense=0,
                        att_dmg_min=0, att_dmg_max=0, damage=0, crit_chance=0, crit_multiplier=0):
        quality = random.choices(sList, weights=sWeights, k=1)[0]
        quality_val = sValue.get(quality)
        equipable_slot = random.choice(['head', 'chest', 'legs', 'feet'])
        defense = 1 + random.randint(0, 2)

        return cls(quality, quality_val, etype, equipable_slot, value,
                   max_durability, strength, dexterity, intelligence,
                   max_hp, defense, att_dmg_min, att_dmg_max, damage,
                   crit_chance, crit_multiplier)

    def show_stats(self):
        name = f'{self.quality} {self.type}'
        slot = f'{self.equipable_slot.title():>9}'
        line2_left = f'Dur: {self.durability:>2}/{self.max_durability:<2} '
        line2_right = f'Defense: {self.defense}'
        return f'{name:<17}{slot:>13}\n{line2_left:<15}{line2_right:>15}\n'


# Code designed to generate item variation
# def generate_quality():
#     return random.choices(list(sValue.keys()), weights=sWeights, k=1)[0]
# def generate_item_variable_str(string_length=5):
#     """Generate a random string of fixed length """
#     letters = string.ascii_lowercase
#     return ''.join(random.sample(letters, string_length))


def create_random_item(class_type=1):
    """Generates an instance of the selected class"""
    if class_type == 1:
        item_variable = Weapon.generate()
        return item_variable

    elif class_type == 2:
        item_variable = Armor.generate()
        return item_variable


def create_random_equipable_item(how_many=1, etype=random.randint(1, 2)):
    for i in range(0, how_many):
        x = create_random_item(etype)
        return x
