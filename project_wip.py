import numpy as np 

def read_bff(bff):
    ''' 
    Reads board file format (.bff)
    *** Args ***
        bff: str
            name of file to be read
    *** Returns ***
        rows: list, str
            list of string of each row
        blocks: tuple, int
            number of A,B,C blocks respectively
        lasers: list, tuple, tuple, int
            list of lasers as tuples
            each tuple contains lasers starting point (x,y) and direction (vx,vy)
        points: list, tuple
            list of target points (x,y)
    returns(rows,blocks,lasers,points)
    '''
    f=open(bff).read().strip().split('\n')
    # opening and reading the file
    # strip gets rid of dead space at the beginning and end
    # split will break it apart at each newline \n
    
    # splitting into list of lines
    # could try to make this cleaner with list comprehension but I'm not gonna worry about that right now
    lines=[]
    for line in f:
        lines.append(line)
    
    # intializing variables
    lasers=[]
    rows=[]
    points=[]
    num_A,num_B,num_C=0,0,0

    # loop through each line in the file 
    for i in range(len(lines)):
        
        if lines[i]=="GRID START":
            # if we read GRID START then we will loop through the subsequent lines that represent the grid rows
            for j in range (i+1,len(lines)):
                if lines[j]=="GRID STOP":
                    break
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
    return(rows,(num_A,num_B,num_C),lasers,points)

def grid_reader(rows):
    '''
    interprets list of gameboard rows into xy grid as a numpy array
    *** Args 
        rows: list, str
            list of grid rows output from read_bff
    *** Returns
        grid: np array
            xy grid with open spaces and fixed blocks marked'''
    
    y_dim=len(rows)
    x_dim=len(rows[0].split(' '))
    grid=np.zeros((2*x_dim+1,2*y_dim+1),dtype=str)
    # 2*length+1 to get the full size of grid including the even spaces
    # see the handout for explanation of grid indexing
    for j in range(y_dim):
        for i in range(x_dim):
            grid[2*i+1,2*j+1]=rows[j].split(' ')[i]
            # place the symbols from the board into corresponding index of the grid
    return grid

def pos_check(point,grid):
    '''returns True if point is within the grid
    *** Args
        point: tuple, int
            xy coords 
        grid: np array
            generated from grid_reader 
    *** Returns
        bool
            True if point is within the grid, else False
            '''
    x_dim,y_dim = np.shape(grid)[0], np.shape(grid)[1]
    if point[0]<0 or point[0]>x_dim-1:
        return False
    elif point[1]<0 or point[1]>y_dim-1:
        return False
    else:
        return True

def get_adj_blocks(point,grid):
    ''' list of adjacent blocks from point of laser'''
    x,y = point[0],point[1]
    neighbors=[]
    for i in [x-1,x+1]:
        if pos_check((i,y),grid)==True:
            neighbors.append((i,y))
    for j in [y-1,y+1]:
        if pos_check((x,j),grid)==True:
            neighbors.append((x,j))    
    return neighbors


def run_laser(laser,grid):
    '''runs laser from starting point with trajectory until it leaves the board
    *** Args
        laser: tuple, tuple, int
            laser as a tuple of starting coords (x,y) and trajectory (vx,vy)
            when you get lasers from the read_bff
        grid: np array
    '''
    laser_traj=[laser[0]]
    # grab starting point from laser tuple
    x,y=laser_traj[0][0],laser_traj[0][1]
    vx,vy=laser[1][0],laser[1][1]
    absorbed=False

    # update new position to the start of the trajectory list
    # run as long as new position is within the grid
    while pos_check(laser_traj[0],grid)==True and absorbed==False:
        ### conditionals go here for block behaviors

        # this will stop the laser from running if it hits an opaque block from any direction
        for block in get_adj_blocks((x,y),grid):
            if grid[block[0],block[1]]=='B':
                absorbed=True

        ### for the other blocks the behavior will depend on which direction it gets hit from
        ### e.g. if a reflect block is above or below then vy changes
        ### if a reflect block is right or left then vx changes
        ### for the refract block will have to start a new instance of run_laser()
        
        laser_traj.insert(0,(x+vx,y+vy))
        x,y=laser_traj[0][0],laser_traj[0][1]
    # have to delete the last new point that broke out of the grid and killed the while loop
    del laser_traj[0]
    return(laser_traj)

if __name__=="__main__":
    rows,blocks,lasers,points=read_bff('bff_files/tiny_5.bff')
    # print(rows)
    # print(blocks)
    # print(lasers)
    # print(points)

    grid=grid_reader(rows)


    print(run_laser(lasers[0],grid))


