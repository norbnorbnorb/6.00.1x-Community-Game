from person import Person, Hero, Vampire, Blocker
from weapons import Weapon, Sword, Axe
from party import Party
from battle import Battle


party1 = Party()
party2 = Party()
battle = Battle()

enemy1 = Vampire('Blood Sucker')
enemy2 = Blocker('Shield Man')
enemy3 = Person('Goomba')

fighter1 = Person('Basic B')
hero = Hero('Player One')
fighter3 = Person('Cannon Fodder')
fighter4 = Person('More Cannon Fodder')
# fighter5 = Person('Even more Cannon Fodder')
# fighter6 = Person('and more Cannon Fodder')

battle_axe = Axe(dmg=2, defense=0)
longsword = Sword(dmg=4, defense=0)
short_sword = Sword(dmg=3, defense=1)


party1.add_member(enemy1)
party1.add_member(enemy2)
party1.add_member(enemy3)

party2.add_member(fighter1)
party2.add_member(hero)
party2.add_member(fighter3)
party2.add_member(fighter4)
# party2.add_member(fighter5)
# party2.add_member(fighter6)

if __name__ == '__main__':
    # hero.pickup_gear(battle_axe)
    # GEAR_LIST = hero.get_eqipped_items()
    # hero.pickup_gear(longsword)
    # hero.pickup_gear(short_sword)

    print('---------------------------------')
    print()
#     # battle.whole_party_turn_battle(party1, party2)
    battle.alternating_turn_battle(party1, party2)

