from mapa import Map
from utils import *
import asyncio
from queue import PriorityQueue

GOAL_COST = 0
FLOOR_COST = 0.5
MOVE_TO_BOX = 0.5
KEEPER_MOVE_COST = 1.5
#DEADLOCK_COST = 50


DIRECTIONS = ["w","a","s","d"]

# Nos de uma arvore de pesquisa
class SearchNode:
    def __init__(self,state,parent,cost=None,heuristic=None,action=''): 
        self.state = state
        self.parent = parent
        self.cost = cost
        self.heuristic = heuristic
        self.action = action

    def in_parent(self, newstate):
        if self.parent == None:
            return False
        # verifica se o novo estado e o pai do no atual
        if self.parent.state == newstate:
            return True
        # verifica se o novo estado esta no caminho já percorrido (avo, bisavo, etc)
        return self.parent.in_parent(newstate)
    def __lt__(self, other):
        return self.cost + self.heuristic < other.cost + other.heuristic
    def __le__(self, other):
        return self.cost + self.heuristic <= other.cost + other.heuristic

    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + ")"
    def __repr__(self):
        return str(self)

# Arvores de pesquisa
class SokobanSolver:
    # construtor
    def __init__(self,level_map: Map, strategy='breadth', method='manhatan'): 
        self.level_map = level_map
        self.boxes_position = []
        self.goals_position = []
        self.deadlocks = []
        self.strategy = strategy
        self.method = method
        self.deadlocks_pos = []
    
    
    # obtain the path from the initial state to the goal state
    def get_path(self,node):
        if node.parent == None:
            return [node.action]
        path = self.get_path(node.parent)
        path += [node.action]       
        return path
    
    #def has_path(self, BoxPos):
    #    return self.get_path(node) != []
    def result(self, current_state, direction):
        '''
            RECEIVES: the current state and a direction (action)
            RETURNS: the next state 
            
            Calculates the next state given the current state and a direction (action):
                -> Receives a dictionary containing the current state
                -> Calculates the next state (positions of the keeper and boxes)
                -> Returns the new state calculated
        '''
        next_state = calc_next_state(current_state, direction)
        return next_state
    
    
    def actions(self, current_state):
        '''
            RECEIVES: the current state
            RETURNS: a list containing all the valid actions for the state
            
            Calculates all the valid actions for a state:
                -> Receives a dictionary containing the current state
                -> For every direction in "wasd" calculates the next state (positions of the keeper and boxes)
                -> Verifies wether the boxes are in a deadlock
                -> Return a list of valid actions (directions)
        '''
        valid_directions = []
        for direction in DIRECTIONS:
            next_state = calc_next_state(current_state,direction)
            keeper = next_state.keeper
            boxes = next_state.boxes[:]
            
            valid_directions.append(direction)
            if Map.is_blocked(self.level_map,keeper) or len(list(set(boxes))) < len (boxes):
                valid_directions.remove(direction)
                continue
            
            for box in boxes:
                ''' Estas verificações não poupam grande coisa em termo de nós abertos '''
                if box in self.deadlocks_pos:
                    valid_directions.remove(direction)
                    continue          
                elif self.isDeadlock(box):
                    self.deadlocks_pos.append(box)                
                    #self.deadlocks.append(next_state)
                    valid_directions.remove(direction)
        return list(set(valid_directions))
    

    def heuristic(self, current_state,method='manhatan'):
        keeper = current_state.keeper
        boxes = current_state.boxes[:]
        goals = current_state.goals[:]
        heuristic = calc_distance(keeper,boxes,method)
        for box in boxes:
            heuristic += calc_distance(box,goals,method)
        return heuristic
        
        
    def cost(self, current_state, direction):
        ''' 
        RECEIVES: the current state and a direction (action)
        RETURNS: the cost of achieving the next state 
            
        Calculates the next state given the current state and a direction (action):
            -> Receives a dictionary containing the current state
            -> Calculates the next state (positions of the keeper and boxes)
            -> Returns the cost of achieving the new state
        '''
        prev_boxes = current_state.boxes[:]
        next_state = calc_next_state(current_state, direction)
            # check if the next position is a goal
        
        boxes = next_state.boxes[:]
        for box in boxes:
            if box in self.goals_position:
                return GOAL_COST
                # check if the next position is a deadlock
            
            if next_state.keeper in near_box(box):
                return MOVE_TO_BOX
            
            
            #isto acho que nao faz nada, nunca vemos o custo de um estado se ele for um deadlock
            #elif box in self.deadlocks_pos:
            #    return DEADLOCK_COST
        
        # if we moved a box into a normal floor tile    
        boxes.sort()
        prev_boxes.sort()
        if str(boxes) != str(prev_boxes):
            return FLOOR_COST
        
        #if its neither a goal, a deadlock nor moved a box return the cost of a keeper move
        return KEEPER_MOVE_COST

    def satisfies(self, current_state):
        ''' 
        RECEIVES: current state
        RETURNS: True or False
        
        Verifies if all the boxes are placed on the goals:
            -> Receives a dictionary containing the current state
            -> Sorts the lists containing the positions of the boxes and goals
            -> Checks wether the lists are equal
        '''
        current_state.boxes.sort()
        current_state.goals.sort()
        return current_state.boxes == current_state.goals

    # procurar a solucao
    async def search(self, state):
        #permite inicializar uma nova arvore de cada vez que é chamada a funcao search
        #faz reset basicamente
        self.open_nodes = PriorityQueue()
        root = SearchNode(state,None,cost=0,heuristic=0)
        
        self.open_nodes.put((0,root))
        open_nodes = 0
        #print("HEURISTIC: ", self.heuristic(state,self.method))
        
        #while self.open_nodes != []:
        while not self.open_nodes.empty(): 
            await asyncio.sleep(0)

            node = self.open_nodes.get()[1]

            if self.satisfies(node.state):
                print("OPEN NODES: ", open_nodes)
                return self.get_path(node)

            # para cada ação na lista de ações possíveis
            for action in self.actions(node.state):
                new_state = self.result(node.state,action)

                if new_state not in self.deadlocks:
                    if node.in_parent(new_state):
                        continue
                    
                    #heur = self.heuristic(new_state, self.cost(node.state,action), self.method)
                    #acc_cost = acc_cost * .5
                    #heur = heur * .5
                    acc_cost = (node.cost + self.cost(node.state,action))*.5
                    heur = self.heuristic(new_state,self.method)*.5
                    #heur *= (1.0 + 1/100)
                    new_node = SearchNode(state=new_state,parent=node,cost=acc_cost,
                                heuristic=heur,action=action)
                    open_nodes += 1   
                    
                    #print("ACC COST: ", new_node.cost)
                    #print("COST: ", cost)
                    #print("HEURISTIC: ", new_node.heuristic)
                    #print("OPEN NODES UNTIL NOW: ", open_nodes)   
                    #print(new_node)
                    self.open_nodes.put((acc_cost+heur, new_node))
                    #lnewnodes.append(new_node)
            #self.add_to_open(lnewnodes)
        return None

    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
        if self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == 'uniform':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda node: node.cost)
        elif self.strategy == 'greedy':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda node: node.heuristic)
        elif self.strategy == 'a*':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda node: node.cost + node.heuristic)

    # auxiliary method for calculating deadlocks
    def isDeadlock(self, pos):
        i_x = 0 #number of horizontal wall next to the pos i
        i_y = 0 #number of vertical wall next to the pos i
        other_boxes = [box for box in self.boxes_position if box != pos]
        if self.level_map.is_blocked(pos):
            return True
        if self.level_map.is_blocked((pos[0] + 1, pos[1])) or self.level_map.is_blocked((pos[0] - 1, pos[1])) or (pos[0] + 1, pos[1]) in other_boxes or (pos[0] - 1, pos[1]) in other_boxes:
            i_x += 1
        if self.level_map.is_blocked((pos[0], pos[1] + 1)) or self.level_map.is_blocked((pos[0], pos[1] - 1)) or (pos[0], pos[1] + 1) in other_boxes or (pos[0], pos[1] - 1) in other_boxes:
            i_y += 1

        if (i_x > 0 and i_y > 0) and pos in self.goals_position: # verifies if is not on a corner and if it is, make sure it's not a goal
           return True

        return False