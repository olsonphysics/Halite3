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


build = True
min_halite = 40
#future optimization is to make scope dynamic based on map size and player count#
scope = 1

""" <<<Game Loop>>> """

while True:
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map
    ship_list = []    
    my_fleet = shipclass.Fleet(me, game_map)
    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []

    for ship in me.get_ships():
        b_ship = shipclass.BetterShip(ship, game_map)

#returning based commands#
        if b_ship.returning:
            command_queue.append(
                ship.move(my_fleet.fleet_navigate(ship, me.shipyard.position)))
        elif b_ship.halite_amount > 700 and not b_ship.returning:
            b_ship.returning = True
            command_queue.append(
                ship.move(my_fleet.fleet_navigate(ship, me.shipyard.position)))
        elif b_ship.halite_amount < (0.1*game_map[ship.position].halite_amount):
            command_queue.append(my_fleet.fleet_stay_still(ship))
        elif game_map[ship.position].halite_amount > min_halite:
            command_queue.append((my_fleet.fleet_stay_still(ship)))
        elif b_ship.position == b_ship.target and b_ship.exploring:
            b_ship.exploring = False
            command_queue.append(my_fleet.fleet_stay_still(ship))
        elif b_ship.exploring:
            command_queue.append(
                ship.move(my_fleet.fleet_navigate(ship, b_ship.target )))


#shipyard based commands#
        elif b_ship.position == me.shipyard.position:# and not game_map[b_ship.position.directional_offset(spawn_cardinals[spawn_counter%4])].is_occupied:
            b_ship.returning = False
            b_ship.target = b_ship.get_target(scope)
            b_ship.exploring = True
            command_queue.append(
                ship.move(my_fleet.fleet_navigate(ship, b_ship.target )))


            # b_ship.exploring = False
            # b_ship.target = b_ship.position

#if halite is less than 100, implement scope to find good spot#
#SCOPE SCOPE SCOPE#
        elif b_ship.scarce_move(b_ship.check_surroundings(), min_halite) == True:        
            b_ship.exploring = True
            b_ship.target = b_ship.get_target(scope)
            command_queue.append(
                ship.move(my_fleet.fleet_navigate(ship, b_ship.target )))
            
        elif b_ship.safe_move(b_ship.check_surroundings()):
            command_queue.append(ship.move(my_fleet.fleet_navigate(ship, b_ship.safe_move(b_ship.check_surroundings()))))

        else:
            command_queue.append(my_fleet.fleet_stay_still(ship))
#NEW ASSHOLE
    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.

    if len(game.players) == 2:
        for player in game.players:
            if player != game.my_id:
                if len(game.players[player].get_ships()) <= 1 and game.turn_number >= 100:
                    build = False

    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied and (me.shipyard.position not in my_fleet.ship_orders.values()) and build == True:
        command_queue.append(me.shipyard.spawn())


    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

#ships that are returnig are assigned orders first
#iterate over game map and ignore all spaces that are less than minimum halite