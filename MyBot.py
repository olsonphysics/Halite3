#!/usr/bin/env python3
# Python 3.6

import logging
import hlt
import random
import shipclass
from hlt import constants, entity, positionals, game_map
from hlt.positionals import Direction

""" <<<Game Begin>>> """


spawn_counter = 0
spawn_cardinals = [Direction.North, Direction.South, Direction.East, Direction.West]
game = hlt.Game()

#Add Code Here for anything that will exceed the 2 second per turn timer, such as initial analysis of the map (size, max halite, # of players)#

game.ready("PicoGrande")

logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

while True:
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map
    ship_list = []    

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []

    for ship in me.get_ships():
        b_ship = shipclass.BetterShip(ship, game_map)
        if b_ship.halite_amount > 600:
            command_queue.append(
                ship.move(game_map.naive_navigate(ship, me.shipyard.position)))
        elif b_ship.position == me.shipyard.position and not game_map[b_ship.position.directional_offset(spawn_cardinals[spawn_counter%4])].is_occupied:
            command_queue.append(
                ship.move(spawn_cardinals[spawn_counter%4]))
            spawn_counter += 1
        elif game_map[ship.position].halite_amount > 100:
            command_queue.append((ship.stay_still()))
        elif b_ship.safe_move(b_ship.check_surroundings()):
            command_queue.append(ship.move(game_map.naive_navigate(ship, b_ship.safe_move(b_ship.check_surroundings()))))


            
        # elif game_map[ship.position].halite_amount < constants.MAX_HALITE / 10 or ship.is_full:
        #     command_queue.append(
        #         ship.move(
        #             random.choice([ Direction.North, Direction.South, Direction.East, Direction.West ])))
        else:
            command_queue.append(ship.stay_still())

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

