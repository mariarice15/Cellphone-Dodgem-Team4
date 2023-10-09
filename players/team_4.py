import math
import random
import numpy
import fast_tsp
from collections import deque
random.seed(2)

class Player:
    def __init__(self, id, name, color, initial_pos_x, initial_pos_y, stalls_to_visit, T_theta, tsp_path, num_players):
        self.id = id
        self.name = name
        self.color = color
        self.pos_x = initial_pos_x
        self.pos_y = initial_pos_y
        self.stalls_to_visit = stalls_to_visit
        self.num_stalls = len(stalls_to_visit) #number of stalls to visit
        self.T_theta = T_theta
        self.tsp_path = tsp_path
        self.num_players = num_players

        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx**2)

        self.sign_x = 1
        self.sign_y = 1
        
        #next move
        self.action = 'move'

        # team 5 vars
        self.dists = [[0 for _ in range(self.num_stalls + 1)] for _ in range(self.num_stalls + 1)]
        self.q = deque()
        # var to count how long to be in obstacle avoidance mode
        self.collision_counter = 0
        self.target_locations = []

        #storing lookup info
        self.other_players = {}
        self.obstacles = {}
        self.counter = 0

        self.tsp()
        self.queue_path()

    
    # initialize queue with stalls to visit from tsp in order
    def queue_path(self):
        stv = self.stalls_to_visit
        tsp = self.tsp_path

        for i in tsp[1:]:
            self.q.append(stv[i-1])

    # get tsp in relation to us 
    def tsp(self):
        stv = self.stalls_to_visit
        n = self.num_stalls
        px, py = self.pos_x, self.pos_y

        for i in range(0, n):
            d = self.__calc_distance(px, py, stv[i].x, stv[i].y)
            self.dists[0][i+1] = math.ceil(d)

        for i in range(0, n):
            for j in range(0, n):
                d = self.__calc_distance(stv[i].x, stv[i].y, stv[j].x, stv[j].y)
                self.dists[i+1][j+1] = math.ceil(d)
                
        self.tsp_path = fast_tsp.find_tour(self.dists)

    def __calc_distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


    # simulator calls this function when the player collects an item from a stall
    def collect_item(self, stall_id):
        if stall_id == self.q[0].id:
            self.q.popleft()
            print(self.q[0].id)
        else:
            for s in self.q:
                if stall_id == s.id:
                    self.q.remove(s)

    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        for player in other_players:
            self.other_players[player[0]] = player[1], player[2]

        for obstacle in obstacles:
            self.obstacles[obstacle[0]] = obstacle[1], obstacle[2]

        # see if any obstacles are in our path
        # if so, calculate new target point, add to target locations lists
        # modify move function to head towards target point if list isn't empty
        # else head towards stall
        
        self.action = 'move'

    # simulator calls this function when the player encounters an obstacle
    # Maybe if edited and we're given the obstacle id we can add it to our database
    def encounter_obstacle(self):
        self.action = 'lookup'

        self.collision_counter = 20
        self.obstacles[self.counter] = (self.counter, self.pos_x, self.pos_y)
        self.counter += 1
        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx**2)
        self.sign_x *= -1
        self.sign_y *= -1

        # self.pos_x += self.sign_x * self.vx
        # self.pos_y += self.sign_y * self.vy

    # simulator calls this function to get the action 'lookup' or 'move' from the player
    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move'
        
        self.pos_x = pos_x
        self.pos_y = pos_y
        
        return self.action
    
    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):

        if self.collision_counter > 0:
            self.collision_counter -= 1
        elif self.q and len(self.q) > 0:
            target_stall = self.q[0]
            delta_y = target_stall.y - self.pos_y
            delta_x = target_stall.x - self.pos_x

            if delta_y == 0:
                self.vy = 0
                self.vx = 1
            elif delta_x == 0:
                self.vy = 1
                self.vx = 0
            else:
                angle = math.atan(numpy.abs(delta_y)/numpy.abs(delta_x))
                # sin/cos multiplied by 1 to get the straight line distance to the point
                self.vy = math.sin(angle)
                self.vx = math.cos(angle)

            if delta_y < 0:
                self.sign_y = -1
            else:
                self.sign_y = 1

            if delta_x < 0:
                self.sign_x = -1
            else:
                self.sign_x = 1
        else:
            # post game strategy -> find a place to hide and accumulate phone points
            self.vx , self.vy = 0

        new_pos_x = self.pos_x + self.sign_x * self.vx
        new_pos_y = self.pos_y + self.sign_y * self.vy

        return new_pos_x, new_pos_y