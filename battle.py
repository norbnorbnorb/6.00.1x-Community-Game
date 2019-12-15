from itertools import zip_longest
from copy import deepcopy

from data_src import *
from combat_funcs import *
import random


def battle_menu(attacker, enemy_party):
    # generate option lists
    # attack_options = [{'name': item.attack_name, 'attack_setup': item.attack_setup} for item in
    #                   [attacker.equip_slots['Main Hand'],
    #                    attacker.equip_slots['Off Hand']] if item]
    equip_with_attacks = ['Main Hand', 'Off Hand']

    attack_loc_strings = [attacker.equip_slots.get(item).__getattribute__('attack') for item in equip_with_attacks
                          if attacker.equip_slots.get(item, None)]
    attack_player_display_list = []
    attack_list = []
    for a_loc_s in attack_loc_strings:
        attack = get_data_from_loc_str(data, a_loc_s)
        attack_list.append(attack)
        user_info_str = f'{attack["name"]}'  # TODO: add info from attack setup, target number ....
        attack_player_display_list.append(user_info_str)

    spell_options = []
    on_cd = []
    low_mana = []
    for spell in attacker.spell_book:
        if spell['cd_timer'] > 0:
            on_cd.append(spell)
        elif spell['mana_cost'] > attacker.mana:
            low_mana.append(spell)
        else:
            spell_options.append(spell)

    possible_actions = ['Attack']
    possible_actions += ['Spell']
    possible_actions += ['Show Hero Stats']  # , 'Skip turn']
    possible_actions += ['Flee Battle']

    action = attacker.choose_battle_action(possible_actions).lower()
    if action == 'attack':
        attack_index = attacker.choose_attack(attack_player_display_list)
        attack_loc_str = attack_loc_strings[attack_index]
        attack = get_data_from_loc_str(data, attack_loc_str)
        setup = get_data_from_loc_str(data, attack['attack_setup'])
        attack_dmg_base = attack['dmg_base']
        elemental = attack['elemental']
        status_effect = None
        if attack.get('status_effect', None):
            status_effect = deepcopy(get_data_from_loc_str(data, attack.get('status_effect')))
        dmg_done = run_attack(attacker, enemy_party, dmg_base=attack_dmg_base, elemental=elemental,
                              status_effect=status_effect, **setup)

    elif action == 'spell':
        if len(spell_options) < 1:
            print(f'You have no spells to use this turn!')
            action = battle_menu(attacker, enemy_party)
        else:
            spell_index = attacker.choose_attack(spell_options)
            spell = spell_options[spell_index]
            attack_setup = get_data_from_loc_str(data, spell['attack_setup'])
            spell_dmg_base = spell['dmg_base']
            spell_elemental = spell['elemental']
            status_effect = None
            if spell.get('status_effect', None):
                status_effect = deepcopy(get_data_from_loc_str(data, spell.get('status_effect')))
            dmg_done = run_attack(attacker, enemy_party,
                                  dmg_base=spell_dmg_base, elemental=spell_elemental,
                                  status_effect=status_effect, **attack_setup)

            attacker.set_mana(-spell['mana_cost'])
            spell['cd_timer'] = spell['cool_down']

    elif action == 'show hero stats':
        attacker.party.display_single_member_item_card(attacker)
        action = battle_menu(attacker, enemy_party)
    elif action == 'skip turn':
        pass
    elif action == 'flee battle':
        pass
    return action


def check_dodge(target, can_dodge):
    return (random.randrange(100) < target.dodge) if can_dodge else False


def check_crit(attacker, can_crit):
    return (random.randrange(100) < attacker.crit_chance) if can_crit else False


def generate_dmg(attacker, target, dmg_base='str', is_crit=False,
                 wpn_dmg_perc=100, c_hp_perc_dmg=0, max_hp_perc_dmg=0):

    c_hp_dmg = target.hp / 100 * c_hp_perc_dmg
    max_hp_dmg = target.max_hp / 100 * max_hp_perc_dmg

    dmg_calc = get_data_from_keys(data, ['conversion_ratios', dmg_base+'_to_dmg'])

    dmg_wo_wpn = (attacker.__getattribute__(dmg_base) * dmg_calc['dmg_per_'+dmg_base]) + (attacker.level * dmg_calc['dmg_per_level'])

    wpn_dmg = round((dmg_wo_wpn / 100) * get_data_from_keys(data, ['conversion_ratios', 'b_dmg_wpn_dmg_factor'])
                    * attacker.__getattribute__('wpn_dmg')) + attacker.__getattribute__('wpn_dmg') + dmg_calc['start']

    wpn_dmg = wpn_dmg / 100 * wpn_dmg_perc

    dmg = sum([c_hp_dmg, max_hp_dmg, wpn_dmg])
    if is_crit:
        dmg = (dmg * attacker.crit_dmg) // 100
    return round(dmg)


def defense_calc(dmg, target, elemental):
    # TODO: generalise resistances

    if elemental == 'physical':  # untill we have the new npc
        defense = target.armor
    elif elemental == 'magic':
        defense = target.magic_resistance
    elif elemental == 'elemental':
        defense = target.elemental_resistance
    else:
        defense = 0  # TODO: heal reduction/multi?
    # TODO: armor piercing calc here

    if defense < 0:
        lol_dmg_multi = 2 - (100 / (100 - defense))
    else:
        lol_dmg_multi = 100 / (100 + defense)

    dmg_done = lol_dmg_multi * dmg

    # else:
    #     dmg_done = dmg - defense
    if elemental == 'true':
        dmg_done = dmg
    if elemental == 'heal':   # * -1 if heal
        dmg_done = -dmg_done
    return round(dmg_done)


def get_target(attacker, primary, forced_primary_target,
               target_num, members_list, rnd_target):
    if primary:
        if forced_primary_target:
            target = forced_primary_target
        else:
            target = attacker.choose_target(members_list)
    else:
        if rnd_target:
            target = random.choice(members_list)
        elif target_num < len(members_list):
            target = attacker.choose_target(members_list)
        else:
            target = members_list[0]
    return target


# TODO: add a function to modify setup based on player stats and percs once we have that before running attack?
def run_attack(attacker, target_party, target_num=1, primary=True, primary_pct=100,
               rnd_target=True, forced_primary_target=None, splash_dmg=0,
               elemental='physical', vamp=0, can_crit=True, dmg_base='str',
               wpn_dmg_pct=100, c_hp_pct_dmg=0, max_hp_pct_dmg=0, can_dodge=True, status_effect=None, p=True):
    """

    :param status_effect: status effects applied to the target on hit
    :param can_dodge:  bool:
    :param attacker: npc or subclass
    :param target_party: party
    :param target_num: int: number of targets including primary / 'all' for full target party
    :param primary: bool: is there a primary target hit for primary percent
    :param primary_pct: percent of full dmg the primary target is hit for
    :param rnd_target: bool: chooses non primary targets randomly
    :param forced_primary_target: npc or subclass: used as primary target
    :param splash_dmg: dmg to non primary targets
    :param elemental: dmg etype used to calculate and apply dmg / special for 'heal'(inverts dmg) and 'true'(ignores defense)
    :param vamp: int: percentage of dmg dealt affecting attacker hp. can be negative
    :param can_crit: bool:
    :param dmg_base: 'str_based' or 'int_based' or 'dex_bases'. for dmg generation
    :param max_hp_pct_dmg: int: percent of target max hp as dmg
    :param c_hp_pct_dmg: int: percent of target current hp as dmg
    :param wpn_dmg_pct: int: percentage modifier for weapon dmg / set to 0 if you want only target hp pool based dmg
    :return: int: overall dmg done
    """
    members_list = attacker.party.members[:] if elemental == 'heal' else target_party.members[:]

    if target_num == 'all' or target_num > len(members_list):
        target_num = len(members_list)

    dmg_combined = 0
    while target_num > 0:
        dmg_mod = primary_pct if primary else splash_dmg
        target = get_target(attacker, primary, forced_primary_target, target_num,
                            members_list, rnd_target)
        primary = False
        is_crit = check_crit(attacker, can_crit)
        raw_dmg = generate_dmg(attacker, target, dmg_base, is_crit, wpn_dmg_pct,
                               c_hp_pct_dmg, max_hp_pct_dmg, )  # value for full dmg before and mod or reduction

        #  other modification, not really generation, not really defense reduction
        dmg_dealt = raw_dmg * dmg_mod // 100  # modify for splash or primary dmg factor
        is_dodge = check_dodge(target, can_dodge)
        if is_dodge:
            pass
            print(f'{target.name} dodged!')
        else:
            dmg_received = defense_calc(dmg_dealt, target, elemental,)
            target.set_hp(-dmg_received)
            if target.is_alive and status_effect:
                status_effect['caster'] = attacker  # TODO: this seems a bit dirty
                target.add_status_effect(status_effect)
            print(f'vamp: {vamp}')
            if not vamp == 0:
                run_attack(attacker, attacker.party, 1, forced_primary_target=attacker,
                           primary_pct=vamp, dmg_base=dmg_base, elemental='heal',
                           can_dodge=False)

            dmg_combined += dmg_received
            if p:
                verb = 'healed' if dmg_received < 0 else 'hit'
                crit_str = ' with a crit!' if is_crit else '.'
                print(f'{attacker.name} {verb} {target.name} for {abs(dmg_dealt)} pts{crit_str} {abs(dmg_received)} stuck.')
        members_list.remove(target)
        target_num -= 1
    return dmg_combined


def print_combat_status(party_1, party_2):
    def member_stat_list_generator(member):
        if member:
            stat_list = []
            stat_list.append(member.name)
            stat_list.append(member.profession)
            stat_list.append(member.hp)
            stat_list.append(member.max_hp)
            stat_list.append(member.wpn_dmg)
            stat_list.append(member.attack_dmg)
            stat_list.append(member.hp_bar(length=20))
            stat_list.append(member.mana_bar(length=10))
        else:
            return None
        return stat_list

    def member_stat_list_printer(h, e):

        if h:
            hero_name = f'{h[0]}, the {h[1]}'
            hero_hp = f'Hp: {h[2]:>2}/{h[3]:<2}'
            hero_dmg = f'Dmg: {h[4]:>2}/{h[5]:<2}'

            print(f'+ {hero_name:^20} '
                  f'{hero_hp:<8} '
                  f'{hero_dmg:<12} ', end='\t')
        else:
            print(f"{' ':<50}", end="   ")
        if e:
            enemy_name = f'{e[0]}, the {e[1]}'
            enemy_hp = f'Hp: {e[2]:>2}/{e[3]:<2}'
            enemy_dmg = f'Dmg: {e[4]:>2}/{e[5]:<2}'
            print(f'- {enemy_name:^20} '
                  f'{enemy_hp:<8} '
                  f'{enemy_dmg:<12} ', end='    \n')
        else:
            print()

        if h:
            hero_hp_bar = f'HP {h[6]}'
            hero_mana_bar = f'Mana: {h[7]}'

            print(f' {hero_hp_bar:^40}'
                  f' {hero_mana_bar:<15}', end='\t')
        else:
            print(f"{' ':<50}", end="   ")

        if e:
            enemy_hp_bar = f'HP {e[6]}'
            enemy_mana_bar = f'Mana: {e[7]}'

            print(f' {enemy_hp_bar:^40}'
                  f' {enemy_mana_bar:<15}', end='    \n')
        else:
            print()


    print('=' * 17, end=' ')
    print('Hero Party', end=' ')
    print('=' * 18, end='| |')
    print('=' * 18, end=' ')
    print('Enemy Party', end=' ')
    print('=' * 19, end='')
    print('')
    print('=' * 100)
    for hero, enemy in zip_longest(party_1.members, party_2.members):
        member_stat_list_printer(member_stat_list_generator(hero), member_stat_list_generator(enemy))


def single_unit_turn(unit, enemy_party):
    action = battle_menu(unit, enemy_party)
    enemy_party.remove_dead()
    return action


# TODO figure out how to justify each party output


def alternating_turn_battle(party_1, party_2):
    rounds = 0
    print('A Battle has started!')
    while party_1.has_units_left and party_2.has_units_left:
        rounds += 1
        print('\nRound:', rounds)
        print_combat_status(party_1, party_2)
        for i in range(max(len(party_1.members), len(party_2.members))):
            if i < len(party_1.members):
                action_taken = single_unit_turn(party_1.members[i], party_2)
                if not party_2.has_units_left:
                    break
            if i < len(party_2.members):
                action_taken = single_unit_turn(party_2.members[i], party_1)
                if not party_1.has_units_left:
                    break
    if party_1.has_units_left:
        party_1.party_members_info()
        print('Party 1 has won the battle!')
        input('Congrats! Press Enter!')
        for member in party_1.members:
            member.add_xp(party_2.party_worth_xp())
        party_2.__del__()

        input('Press Enter!')

    else:
        party_2.party_members_info()
        print('Party 2 has won the battle!')
    return party_1.has_units_left


def whole_party_turn_battle(party_1, party_2):
    rounds = 0
    print('A Battle has started!')
    while party_1.has_units_left and party_2.has_units_left:
        rounds += 1
        print('')
        print('Round:', rounds)
        print('Party 1:', party_1.members_names)
        print('Party 2:', party_2.members_names)
        if party_1.has_units_left:
            for member in party_1.members:
                no_enemies_left = single_unit_turn(member, party_2)
                if no_enemies_left:
                    break
                input('just press enter')
        if party_2.has_units_left:
            for member in party_2.members:
                no_enemies_left = single_unit_turn(member, party_1)
                if no_enemies_left:
                    break
                input('just press enter')
    if party_1.has_units_left:
        print('Party 1 has won the battle!')
    else:
        print('Party 2 has won the battle!')
    return party_1.has_units_left


def clock_tick(party_1, party_2):
    all_members = party_1.members + party_2.members
    for member in all_members:
        member.tracked_values['c'] += member.speed
    all_members = sorted(all_members, key=lambda m: m.tracked_values['c'], reverse=True)

    # [print(f'c: {member.tracked_values["c"]} - name: {member.name}') for member in all_members]
    return all_members


def tick_cool_downs(unit):
    for spell in unit.spell_book:
        if spell['cd_timer'] > 0:
            spell['cd_timer'] -= 1


def tick_status_effects(unit):
    for se in unit.get_status_effects():
        attack = se.get('attack_setup', None)
        if attack:
            run_attack(attacker=se['caster'], target_party=unit.party, forced_primary_target=unit,
                       **get_data_from_loc_str(data, attack))
        se['ticks'] -= 1
        if se['ticks'] < 1:
            unit.remove_status_effect(se)


def check_fleeing():
    return 25 < random.randint(0,100)


def clock_tick_battle(party_1, party_2):
    parties = [party_1, party_2]
    print('A Battle has started!')
    c_ticks = 0
    for member in party_1.members + party_2.members:
        member.tracked_values['ct'] = 1000
        member.tracked_values['c'] = 0
    is_fleeing = False
    while party_1.has_units_left and party_2.has_units_left and not is_fleeing:
        all_members = clock_tick(party_1, party_2)
        c_ticks += 1
        # print(f'ticks: {c_ticks}')
        for member in all_members:
            if member.tracked_values['c'] > member.tracked_values['ct']:
                if member.hero:
                    print(f'Clock Ticks: {c_ticks}')
                    print_combat_status(party_1, party_2)
                print(f'its {member.name}\'s turn!')
                both_parties = parties.copy()
                both_parties.remove(member.party)
                enemy_party = both_parties[0]
                action_taken = single_unit_turn(member, enemy_party)

                member.set_mana(+member.mana_regen)

                if action_taken == 'attack':
                    member.tracked_values['c'] = 0
                    member.tracked_values['ct'] = 1000
                elif action_taken == 'spell':
                    member.tracked_values['c'] = 0
                    member.tracked_values['ct'] = 1000
                elif action_taken == 'skip turn':
                    pass
                if action_taken == 'flee battle':
                    is_fleeing = check_fleeing()
                    if is_fleeing:
                        break
                if not enemy_party.has_units_left:
                    break
                tick_cool_downs(member)
                tick_status_effects(member)
    return party_2.has_units_left


def initiative_battle(party_1, party_2):
    parties = [party_1, party_2]
    print('A Battle has started!')
    round = 0
    while party_1.has_units_left and party_2.has_units_left:
        print(f'Round: {round}')
        all_members = party_1.members + party_2.members
        c_round_members = sorted(all_members.copy(), key=lambda m: m.speed, reverse=True)
        while c_round_members:
            active_unit = c_round_members[0]
            both_parties = parties.copy()
            both_parties.remove(active_unit.party)
            enemy_party = both_parties[0]
            action_taken = single_unit_turn(active_unit, enemy_party)
            c_round_members.remove(active_unit)
            if not enemy_party.has_units_left:
                break
        round += 1
    if party_1.has_units_left:
        print('Party 1 has won the battle!')
    else:
        print('Party 2 has won the battle!')
    return party_1.has_units_left
