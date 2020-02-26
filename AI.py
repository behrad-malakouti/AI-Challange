import random
import AI_MinimaxUtils

from model import *

# def neighbor_cells(cell):
#     res = []
#     if (cell.col > 0):
#         res.append(Cell(row=cell.row, col=cell.col - 1))
#     if (cell.row > 0):
#         res.append(Cell(row=cell.row, col=cell.col - 1))
#     if (cell.col > 0):
#         res.append(Cell(row=cell.row, col=cell.col - 1))
#     if (cell.col > 0):
#         res.append(Cell(row=cell.row, col=cell.col - 1))

class AI:
    def __init__(self):
        self.rows = 0
        self.cols = 0
        self.path_for_my_units = None

    # this function is called in the beginning for deck picking and pre process
    def pick(self, world):
        print("pick started!")

        # pre process
        map = world.get_map()
        self.rows = map.row_num
        self.cols = map.col_num

        # choosing all flying units
        all_base_units = world.get_all_base_units()
        my_hand = [base_unit for base_unit in all_base_units if base_unit.is_flying]

        # picking the chosen hand - rest of the hand will automatically be filled with random base_units
        world.choose_hand(base_units=my_hand)
        # other pre process
        self.path_for_my_units = world.get_friend().paths_from_player[0]

    # it is called every turn for doing process during the game
    def turn(self, world):
        print("turn started:", world.get_current_turn())
        myself = world.get_me()
        max_ap = world.get_game_constants().max_ap

        enemy_units = world.get_first_enemy().units + world.get_second_enemy().units
        friend_units = world.get_friend().units
        my_units = world.get_me().units

        # play all of hand once your ap reaches maximum. if ap runs out, putUnit doesn't do anything
        for base_unit in myself.hand:
            world.put_unit(base_unit=base_unit, path=self.path_for_my_units)


        # this code tries to cast the received spell
        received_spell = world.get_received_spell()
        if received_spell is not None:
            if received_spell.type == SpellType.HP:
                if received_spell.target == SpellTarget.ENEMY:
                    enemy_units.sort(key=lambda x: x.hp)
                    world.cast_area_spell(center=enemy_units[0].cell, spell=received_spell)
                else:
                    friend_units.sort(key=lambda x: x.hp)
                    world.cast_area_spell(center=friend_units[0].cell, spell=received_spell)
            elif received_spell.type == SpellType.TELE:
                best_score = 0
                best_unit = my_units[0]
                for unit in my_units:
                    #TODO: add distance from king to score
                    score = unit.hp + unit.attack + unit.rage
                    if score > best_score:
                        best_score = score
                        best_unit = unit

                #TODO: find if you want cast the spell
            elif received_spell.type == SpellType.DUPLICATE:
                #TODO: change the code if the ratio is based on BaseUnit properties
                best_score = 0
                best_unit = friend_units[0]
                for unit in friend_units:
                    unit_score = unit.hp + unit.attack + unit.range + 100 * int(unit.target != None) + 1000 * int(unit.target_if_king != None)
                    if (unit_score > best_score):
                        best_score = unit_score
                        best_unit = unit
                    world.cast_area_spell(best_unit.cell, spell=received_spell)

            elif received_spell.type == SpellType.HASTE:
                best_score = 0
                best_unit = friend_units[0]
                for unit in friend_units:
                    unit_score = unit.hp + unit.attack + unit.range + 20 * int(unit.target != None) + 1000 * int(
                        unit.target_if_king != None)
                    if (unit_score > best_score):
                        best_score = unit_score
                        best_unit = unit
                    world.cast_area_spell(best_unit.cell, spell=received_spell)

                    # this code tries to upgrade damage of first unit. in case there's no damage token, it tries to upgrade range
        if len(myself.units) > 0:
            unit = myself.units[0]
            world.upgrade_unit_damage(unit=unit)
            world.upgrade_unit_range(unit=unit)

    # it is called after the game ended and it does not affect the game.
    # using this function you can access the result of the game.
    # scores is a map from int to int which the key is player_id and value is player_score
    def end(self, world, scores):
        print("end started!")
        print("My score:", scores[world.get_me().player_id])
