from person import *
from helper_functions import *


class Hero(Person):
    def __init__(self, name, profession, level):
        super().__init__(name, profession, level)
        self.type = 'Hero'

    @classmethod
    def generate(cls, name='Mr. Lazy', profession='warrior', level=1):
        return cls(name, profession, level)

    def __str__(self):
        return super().__str__()

    def choose_target(self, target_party):
        """
        chooses a person to attack
        :param target_party: party instance
        :return: person instance
        """
        print()
        return select_from_list(target_party.members, index_pos=False, q='Choose a target:')

    def choose_attack(self):
        return select_from_list(self.get_attack_options())

    def choose_battle_action(self, enemy_party):
        """
        lets player choose what to do in their turn and calls appropriate methods
        :param enemy_party: party instance
        :return: -
        """
        #  TODO: find a place to store possible actions
        possible_actions = ['attack', 'Heal', 'Show Hero Stats', ]
        action = select_from_list(possible_actions, q='What do you want to do?')
        # if action.lower() == 'change gear':
        #     self.change_gear()
        #     self.choose_battle_action(enemy_party)
        # elif action.lower() == 'Show Hero Stats':
        #     print(self.show_combat_stats())
        #     self.choose_battle_action(enemy_party)
        # elif action.lower() == 'heal':
        #     self.heal(10)
        # else:
        #     self.attack_target(enemy_party, mode=action)
        return action


# Testing Code!
if __name__ == '__main__':
    p = Person.generate('norbnorb', 'Mage')
    p.stat_growth()
    p.show_stats()
    w = Hero.generate('norbnorb', 'Warrior')
    w.calculate_stats()
    print(w.att_dmg_min, end='-')
    print(w.att_dmg_max)
    print(w.calculate_dmg(), end=' ')
    print(w.calculate_dmg(), end=' ')
    print(w.calculate_dmg(), end=' ')
    print(w.calculate_dmg(), end=' ')
    print(w.calculate_dmg(), end=' ')
    print(w.calculate_dmg(), end=' ')
    print(w.calculate_dmg(), end=' ')
    print(w.calculate_dmg(), end=' ')
    print(w.calculate_dmg(), end=' ')
    print(w.calculate_dmg(), end=' ')
    print(w.calculate_dmg(), end=' ')
