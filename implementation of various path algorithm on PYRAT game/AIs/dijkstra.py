# Template file to create an AI for the game PyRat
# http://formations.telecom-bretagne.eu/pyrat

###############################
# When the player is performing a move, it actually sends a character to the main program
# The four possibilities are defined here
MOVE_DOWN = 'D'
MOVE_LEFT = 'L'
MOVE_RIGHT = 'R'
MOVE_UP = 'U'

###############################
# Please put your imports here
#import utils

###############################
# Please put your global variables here


###############################
# Preprocessing function
# The preprocessing function is called at the start of a game
# It can be used to perform intensive computations that can be
# used later to move the player in the maze.
###############################
# Arguments are:
# mazeMap : dict(pair(int, int), dict(pair(int, int), int))
# mazeWidth : int
# mazeHeight : int
# playerLocation : pair(int, int)
# opponentLocation : pair(int,int)
# piecesOfCheese : list(pair(int, int))
# timeAllowed : float
###############################
# This function is not expected to return anything
def preprocessing(mazeMap, mazeWidth, mazeHeight, playerLocation, opponentLocation, piecesOfCheese, timeAllowed):
    
    # Example prints that appear in the shell only at the beginning of the game
    # Remove them when you write your own program
    print("<b>[mazeMap]</b> " + repr(mazeMap))
    print("<b>[mazeWidth]</b> " + repr(mazeWidth))
    print("<b>[mazeHeight]</b> " + repr(mazeHeight))
    print("<b>[playerLocation]</b> " + repr(playerLocation))
    print("<b>[opponentLocation]</b> " + repr(opponentLocation))
    print("<b>[piecesOfCheese]</b> " + repr(piecesOfCheese))
    print("<b>[timeAllowed]</b> " + repr(timeAllowed))

###############################
# Turn function
# The turn function is called each time the game is waiting
# for the player to make a decision (a move).
###############################
# Arguments are:
# mazeMap : dict(pair(int, int), dict(pair(int, int), int))
# mazeWidth : int
# mazeHeight : int
# playerLocation : pair(int, int)
# opponentLocation : pair(int, int)
# playerScore : float
# opponentScore : float
# piecesOfCheese : list(pair(int, int))
# timeAllowed : float
###############################

def heap_pop(heap):
    if heap != []:
        vertex,weight,parent = heap.pop(0)
        return (vertex, weight, parent)
    else:
        raise

def heap_add_or_replace(heap, triplet):
    def sortSecond(val): 
        return val[1]  
    c=0
    found = False
    for t in heap:
        if triplet[0]==t[0] :
            found=True
            if (triplet[1]<t[1]) and (triplet[1]!=t[1]):
                heap[c]=triplet
                #print("modified")
        c=c+1
    if found==False:
        heap.append(triplet)
    heap.sort(key=sortSecond)


##################
def create_walk_from_parents(parent_dict,initial_vertex,target_vertex):
    path=list()
    #parent_found=()
    #current_vertex=target_vertex
    current_parent=parent_dict.get(target_vertex)
    
    if current_parent==None:
        return path
    path.append(target_vertex)
    while current_parent!=initial_vertex:
        #print(path)
        path.append(current_parent)
        current_parent=parent_dict.get(current_parent)
   # path.append()    
    #path = path.reverse()   
    path=path[::-1]
    #print(path)
    return path
def get_position_above(original_position):
    """
    Given a position (x,y) returns the position above the original position, defined as (x,y+1)
    """
    (x,y) = original_position
    return (x,y+1)

def get_position_below(original_position):
    """
    Given a position (x,y) returns the position below the original position, defined as (x,y-1)
    """
    ###
    ### YOUR CODE HERE
    ###
    (x,y)=original_position
    return(x,y-1)
    # END YOUR CODE
def get_position_right(original_position):
    """
    Given a position (x,y) returns the position to the right of the original position, defined as (x+1,y)
    """
    ###
    ### YOUR CODE HERE
    ###
    (x,y)=original_position
    return(x+1,y)
    # END YOUR CODE

def get_position_left(original_position):
    """
    Given a position (x,y) returns the position to the left of the original position, defined as (x-1,y)
    """
    ###
    ### YOUR CODE HERE
    ###
    (x,y)=original_position
    return(x-1,y)
    # END YOUR CODE
    
def get_direction(initial_vertex,target_vertex):
    if get_position_above(initial_vertex) == target_vertex:
        return MOVE_UP
    elif get_position_below(initial_vertex) == target_vertex:
        return MOVE_DOWN
    elif get_position_left(initial_vertex) == target_vertex:
        return MOVE_LEFT
    elif get_position_right(initial_vertex) == target_vertex:
        return MOVE_RIGHT
    else:
        raise Exception("vertices are not connected")

def walk_to_route(walk,initial_vertex):
    walk_list=list()
    for p in walk:
        walk_list.append(get_direction(initial_vertex,p))
        initial_vertex=p
    # YOUR CODE HERE
    return walk_list
def is_explored(explored_vertices,vertex):
    return vertex in explored_vertices

def add_to_explored_vertices(explored_vertices,vertex):
    explored_vertices.append(vertex)
    
def Dijkstra(maze_graph,initial_vertex):
    # Variable storing the exploredled vertices vertexes not to go there again
    explored_vertices = list()
    
    # Stack of vertexes
    heap = list()
    
    #Parent dictionary
    parent_dict = dict()
    # Distances dictionary
    distances = dict()
    
    # First call
    initial_vertex = (initial_vertex, 0, initial_vertex)#vertex to visit, distance from origin, parent
    heap_add_or_replace(heap,initial_vertex)
    parent_dict[initial_vertex[0]]=initial_vertex[0]
    distances[initial_vertex[0]]=0
    
    while len(heap) > 0:
        (vertex, distance, parent) = heap_pop(heap)
        if vertex not in explored_vertices:
            explored_vertices.append(vertex)
            #print(maze_graph.get(vertex))
            neighbours=maze_graph.get(vertex)
            #parent_dict[vertex]=vertex
            #distances[vertex]=100000
            for k in neighbours:
                #print(k)
                newdist=distance+neighbours.get(k)
                heap_add_or_replace(heap,(k,newdist,vertex))
                #print(heap)
                for t in heap:
                    if k==t[0] :
                        #dist=distances.get(k)
                        #print(distances)
                        #t=t[1]
                        #print(t)
                        if(distances.get(k)!= None):
                            if (distances.get(k) > t[1]):
                                parent_dict[k]=t[2]
                                distances[k]=t[1]
                        elif(distances.get(k)== None):
                            parent_dict[k]=t[2]
                            distances[k]=t[1]

    return explored_vertices, parent_dict, distances



################

def A_to_B(maze_graph,initial_vertex,target_vertex):
    explored_vertices,parent_dict,distances=Dijkstra(maze_graph,initial_vertex)
    walk=create_walk_from_parents(parent_dict,initial_vertex,target_vertex)
    walk_list=walk_to_route(walk,initial_vertex)
    return walk_list
    

# This function is expected to return a move
def turn(mazeMap, mazeWidth, mazeHeight, playerLocation, opponentLocation, playerScore, opponentScore, piecesOfCheese, timeAllowed):
    
    # Example print that appears in the shell at every turn
    # Remove it when you write your own program
    #print("Move: [" + MOVE_UP + "]")
    move=A_to_B(mazeMap,playerLocation,piecesOfCheese[0])
    #print("NEXT NEXT NEXT NEXT NEXT NEXT NEXT NEXT NEXT NEXT NEXT")
    # In this example, we always go up
    return move.pop(0)
