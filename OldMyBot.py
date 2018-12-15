#!/usr/bin/env python3

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import *

import random
import logging


# This game object contains the initial game state.
game = hlt.Game()
# Respond with your name.
game.ready("Better Greedy Bot")

while True:
    # Get the latest game state.
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn.
    command_queue = []

    for ship in me.get_ships():
        # Move to shipyard if ship is near full.
        if ship.halite_amount >= 800:
            if game_map[me.shipyard.position].is_occupied:
                command_queue.append(ship.stay_still())
            else:    
                command_queue.append(ship.move(game_map.navigate(ship, me.shipyard.position)))

        # Move to halite source
        elif game_map[ship.position].halite_amount < constants.MAX_HALITE / 25:
            if game_map[ship.position].halite_amount == 0:
                # Cannot stay on current position
                next_pos = random.choice(ship.position.get_surrounding_cardinals())
                for cardinal in ship.position.get_surrounding_cardinals():
                    if game_map[cardinal].is_empty:
                        next_pos = cardinal
                        break
            else:
                # Current position should not be a problem
                next_pos = ship.position

            for cardinal in ship.position.get_surrounding_cardinals():
                # Find a better direction than source
                if not game_map[cardinal].is_occupied and game_map[cardinal].halite_amount > game_map[next_pos].halite_amount:
                    next_pos = cardinal

            command_queue.append(ship.move(game_map.navigate(ship, next_pos)))
            
        # Else, collect halite.
        else:
            command_queue.append(ship.stay_still())

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
