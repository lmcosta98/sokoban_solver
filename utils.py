#from mapa import Map
import math

class State:
    def __init__(self,keeper,boxes=[],goals=[]):
        self.keeper = keeper
        self.boxes = boxes
        self.goals = goals
    def __lt__(self, other):
        return self.cost + self.heuristic < other.cost + other.heuristic
    def __le__(self, other):
        return self.cost + self.heuristic <= other.cost + other.heuristic
    def __gt__(self, other):
        return self.cost + self.heuristic > other.cost + other.heuristic
    def __ge__(self, other):
        return self.cost + self.heuristic >= other.cost + other.heuristic
    
    def __str__(self):
        return "STATE(" + str(self.keeper) + "," + str(self.boxes) + "," + str(self.goals) + ")"

def calc_next_state(current_state, direction):
    curr_x, curr_y = current_state.keeper[:]
    boxes = current_state.boxes[:]
    
    if direction == 'w':
        next_positon = curr_x, curr_y-1
        if next_positon in boxes:
            boxes.remove(next_positon)
            boxes.append((curr_x, curr_y-2))
    
    elif direction == 'a':
        next_positon = curr_x-1, curr_y
        if next_positon in boxes:
            boxes.remove(next_positon)
            boxes.append((curr_x-2, curr_y))
                  
    elif direction == 's':
        next_positon = curr_x, curr_y+1
        if next_positon in boxes:
            boxes.remove(next_positon)
            boxes.append((curr_x, curr_y+2))
            
    elif direction == 'd':
        next_positon = curr_x+1, curr_y
        if next_positon in boxes:
            boxes.remove(next_positon)
            boxes.append((curr_x+2, curr_y))
    
    next_state = State(next_positon,boxes,current_state.goals)
    return next_state
    
        
def calc_distance(position, list_of_positions, method):
    min_distance = float('inf')
    
    for pos in list_of_positions:
        if method == 'euclidean':
            dist = math.sqrt((pos[0] - position[0]) ** 2 + (pos[1] - position[1]) ** 2)
        elif method == 'manhatan':
            dist = abs(position[0] - pos[0]) + abs(position[1] - pos[1])
        elif method == 'mixed':
            dist1 = math.sqrt((pos[0] - position[0]) ** 2 + (pos[1] - position[1]) ** 2)
            dist2 = abs(position[0] - pos[0]) + abs(position[1] - pos[1])
            dist = min(dist1,dist2)
        if dist < min_distance:
           min_distance = dist 
    
    return min_distance
    
def near_box(pos):
    return [(pos[0]-1,pos[1]),(pos[0]+1,pos[1]),(pos[0],pos[1]-1),(pos[0],pos[1]+1)]
            #(pos[0]-1,pos[1]-1),(pos[0]-1,pos[1]+1),(pos[0]+1,pos[1]-1),(pos[0]+1,pos[1]+1)]


'''
def isDeadlock(self, pos):
    i_x = 0 #number of horizontal wall next to the pos i
    i_y = 0 #number of vertical wall next to the pos i

    if Map.is_blocked((pos[0] + 1, pos[1])) or Map.is_blocked((pos[0] - 1, pos[1])):
        i_x += 1
    
    if Map.is_blocked((pos[0], pos[1] + 1)) or Map.is_blocked((pos[0], pos[1] - 1)):
        i_y += 1
    
    if i_x > 0 and i_y > 0 and pos not in Map.empty_goals: # verifies if is not on a corner and if it is, make sure it's not a goal
        return True
    
    return False '''