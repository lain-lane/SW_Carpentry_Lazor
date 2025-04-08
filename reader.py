import numpy as np
from Lazors import solver

def read_bff(bff):
    ''' 
    Reads board file format (.bff)
    *** Args ***
        bff: str
            filepath to be read
    *** Returns ***
        game_grid: np array
            initial grid with open spaces, x spaces, and fixed blocks
        num_blocks: tuple, int
            (num_A,num_B,num_C) to be placed
        lasers: list, tuple, tuple, int
            list of lasers as tuples
            each tuple contains lasers starting point (x,y) and direction (vx,vy)
        points: list, tuple, int
            list of target points (x,y)
    '''
    f=open(bff).read().strip().split('\n')
    # opening and reading the file
    # strip gets rid of dead space at the beginning and end
    # split will break it apart at each newline \n
    
    # splitting into list of lines
    lines=[]
    for line in f: # could make this shorter with list comprehension but I'm not sure how
        lines.append(line)
    
    # intializing variables
    lasers=[]
    rows=[]
    points=[]
    num_A,num_B,num_C=0,0,0
    ids=['A','B','C','o','x']

    # loop through each line in the file 
    for i in range(len(lines)):
        if lines[i]=="GRID START":
            # if we read GRID START then we will loop through the subsequent lines that represent the grid rows
            for j in range (i+1,len(lines)):
                if lines[j]=='\n':
                    pass # hopefully this makes it robust against extra lines in the grid
                elif lines[j]=="GRID STOP":
                    break
                else:
                    rows.append(lines[j])

        # reading number of blocks to place
        # probably a way to condense this by looping through ['A','B','C'] but it's too late for that now
        elif lines[i].split(' ')[0]=='A' and len(lines[i].split(' '))==2:
            # adding conditional so that it doesn't interpret rows from the grid that start with a fixed block
            # hypothetically this would break if the grid was 2x2 but I don't think there's any puzzles that small
            num_A=int(lines[i].split(' ')[1])
        elif lines[i].split(' ')[0]=='B' and len(lines[i].split(' '))==2:
            num_B=int(lines[i].split(' ')[1])    
        elif lines[i].split(' ')[0]=='C' and len(lines[i].split(' '))==2:
            num_C=int(lines[i].split(' ')[1])
        
        # reading lasers
        elif lines[i].split(' ')[0]=='L':
            las_start=(int(lines[i].split(' ')[1]),int(lines[i].split(' ')[2]))
            las_dir=(int(lines[i].split(' ')[3]),int(lines[i].split(' ')[4]))
            lasers.append((las_start,las_dir))
        # reading points
        elif lines[i].split(' ')[0]=='P':
            points.append((int(lines[i].split(' ')[1]),int(lines[i].split(' ')[2])))
        else:
            pass
    
    # Raise exceptions if any of the vital info isn't in the file
    if rows==[]:
        raise Exception('Board read error - no grid detected')
    if lasers==[]:
        raise Exception('Board read error - no lasers detected')
    if points==[]:
        raise Exception('Board read error - no points detected')
    if num_A==0 and num_B==0 and num_C==0:
        raise Exception('Board read error - no blocks detected')

    def grid_reader(rows):
        ''' interprets list of gameboard rows into xy grid as a numpy array'''
        y_dim=len(rows)  
        ### this would break if there's extra lines in the bff so we need logic for that
        x_dim=0 # initialize
        for char in rows[0].split(' '):
            if char not in ids:
                raise Exception('Board read error - invalid char in grid')
            else:
                x_dim+=1
        grid=np.zeros((2*y_dim+1,2*x_dim+1),dtype=str)
        # 2*length+1 to get the full size of grid including the even spaces
        # see the handout for explanation of grid indexing
        for j in range(y_dim):
            for i in range(x_dim):
                if rows[j].split(' ')[i]==' ':
                    pass
                else:
                    grid[2*j+1,2*i+1]=rows[j].split(' ')[i]
                # place the symbols from the board into corresponding index of the grid
                # 2*x+1 gives us the odd number indexes
        return grid
    game_grid=grid_reader(rows)

    # check that there is an appropriate number of blocks for the grid
    opens=solver.get_open(game_grid)
    if len(opens)<num_A+num_B+num_C:
        raise Exception('Board read error - too many blocks detected')
    
    # checks position of points (cannot be placed on corners where both indices are even or block spaces where both indices are odd)
    for point in points:
        if point[0]%2==0 and point[1]%2==0:
            raise Exception('Board read error - invalid target points')
        elif point[0]%2!=0 and point[1]%2!=0:
            raise Exception('Board read error - invalid target points')
        
    # check that lasers have valid starting points and directions
    for laser in lasers:
        if laser[0][0]%2==0 and laser[0][1]%2==0:
            raise Exception('Board read error - invalid laser position')
        elif laser[0][0]%2!=0 and laser[0][1]%2!=0:
            raise Exception('Board read error - invalid laser position')
        if abs(laser[1][0])!=1 or abs(laser[1][1])!=1:
            raise Exception('Board read error - invalid laser direction')


    return(game_grid,(num_A,num_B,num_C),lasers,points)