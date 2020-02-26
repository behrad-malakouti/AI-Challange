import random
import AI_MinimaxUtils

from model import *

#def number_of_enemies(cell)

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
                    best_score = -1000
                    best_unit = friend_units[0]
                    for unit in friend_units:
                        score = unit.hp * -1
                        if (unit.target_if_king and unit.hp < unit.base_unit.max_hp):
                            score += 100

                        if score > best_score:
                            best_score = score
                            best_unit = unit

                    world.cast_area_spell(center=best_unit.cell, spell=received_spell)
            elif received_spell.type == SpellType.TELE:
                last_unit = myself.units[-1]
                world.cast_unit_spell(last_unit, self.path_for_my_units, self.path_for_my_units.cells[len(self.path_for_my_units.cells) // 2 - 2],
                                      received_spell)
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
            elif received_spell.target == SpellTarget.ENEMY:
                #Cast spell poison or damage for the best_unit
                #TODO: It will be better if we can count the number of enemies in 8 tiles form it for each unit
                #Then we can add it to variable unit_score
                best_score = 0
                best_unit = my_units[0]
                for unit in my_units:
                    unit_score = unit.hp + unit.attack + unit.range * 100 * int(unit.target != None) + 1000 * int(unit.target_if_king != None)
                    if(unit_score > best_score):
                        best_score = unit.score
                        best_unit = unit
                    world.cast_area_spell(best_unit.cell, spell=received_spell)

            #Damage Upgrade Code:
            best_score = 0
            best_unit = my_units[0]
            for unit in my_units:
                unit_score = 10 * unit.hp  + 100 * int(unit.target_if_king != None)
                if (unit_score > best_score):
                    best_score = unit_score
                    best_unit = unit

            world.upgrade_unit_damage(unit=best_unit)
            world.upgrade_unit_range(unit=best_unit)

    # it is called after the game ended and it does not affect the game.
    # using this function you can access the result of the game.
    # scores is a map from int to int which the key is player_id and value is player_score
    def end(self, world, scores):
        print("end started!")
        print("My score:", scores[world.get_me().player_id])
