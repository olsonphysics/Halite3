from hlt import entity, positionals, game_map, constants


class BetterShip(entity.Ship):
    def __init__(self, ship_id, gmmap):
        self.game_map = gmmap
        self.id = ship_id.id
        self.owner = ship_id.owner
        self.position = ship_id.position
        self.halite_amount = ship_id.halite_amount
        self.returning = False
        self.game_map = gmmap
        self.exploring = False
        self.target = self.position

#creates a list of form [(position, halite amount, occupied or not)] in ascending halite value in 4 cardinal directions
    def check_surroundings(self):
        halite_list=[]
        sorted_list=[]
        for coordinates in self.position.get_surrounding_cardinals():
            halite_list.append((coordinates, self.game_map[coordinates].halite_amount, self.game_map[coordinates].is_occupied))
        halite_list.append((self.position, self.game_map[coordinates].halite_amount, True))
        sorted_list = sorted(halite_list, key = lambda t: t[1])
        return(sorted_list)

    def scarce_move(self, sorted_list, min_halite):
        scarce_condition = 0
        for i in sorted_list:
            if i[1] <= min_halite / 10:
                scarce_condition += 1
        if scarce_condition >= 3:
            return True
        else:
            return False

#takes a sorted list (of form generated by check_surroundings) and returns a move to the 
#adjacent, unoccupied square with the highest halite value, or False if all squares occupied 
    def safe_move(self, sorted_list):
        final_list=[]
        for i in range(len(sorted_list)):
            if sorted_list[i][2] == False:
                final_list.append(sorted_list[i])
        if len(final_list):
            return(final_list[-1][0])
        else:
            return ()        

#returns the position of the square with the most 
#halite in a square centered around the ship +/- scope in each direction
    def get_target(self, scope):
        halite_list=[]
        for x in range(self.game_map.width):
            for y in range(self.game_map.height):
                halite_list.append((positionals.Position(x,y), self.game_map[positionals.Position(x,y)].halite_amount))
        sorted_list = sorted(halite_list, key=lambda t: t[1])
        return sorted_list[-1][0]

    def get_target2(self, scope):
        return self.position.directional_offset(positionals.Direction.East)

    def return_home(self, threshold):
        if self.halite_amount >= threshold:
            self.returning = True

class Fleet:
    def __init__(self, player_id, game_map):
        self.ships = player_id.get_ships()
        self.game_map = game_map
        for i in range(len(self.ships)):
            self.ships[i]=BetterShip(self.ships[i], self.game_map)
        self.ship_positions = {}
        for s in self.ships:
            self.ship_positions[s] = s.position
        self.ship_orders = {}
    def fleet_navigate(self, ship, destination):
        for direction in self.game_map.get_unsafe_moves(ship.position, destination):
            target_pos = ship.position.directional_offset(direction)
            if target_pos not in self.ship_orders.values():
                self.ship_orders[ship] = target_pos
                return direction
        self.ship_orders[ship] = ship.position
        return positionals.Direction.Still
    def fleet_stay_still(self, ship):
        if ship.position in self.ship_orders.values():
            for location in ship.position.get_surrounding_cardinals():
                if location not in self.ship_orders.values():
                    return ship.move(self.fleet_navigate(ship, location))
        else:
            self.ship_orders[ship]=ship.position
            return ship.stay_still()