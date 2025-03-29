import numpy as np 
import matplotlib.pyplot as plt

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


def run_laser(laser,grid):
    '''runs laser from starting point with trajectory until it leaves the board
    *** Args
        laser: tuple, tuple, int
            laser as a tuple of starting coords (x,y) and trajectory (vx,vy)
        grid: np array
    *** Returns
        laser_traj: list, tuple, int
            list of laser positions in reverse
    '''
    laser_traj=[laser[0]]
    refract_traj=[]
    # grab starting point from laser tuple
    x,y=laser_traj[0][0],laser_traj[0][1]
    vx,vy=laser[1][0],laser[1][1]
    absorbed=False

    # update new positions to the start of the trajectory list
    # run as long as new position is within the grid
    while pos_check(laser_traj[0],grid)==True and absorbed==False:
        
        ### BLOCK CONDITIONALS
        # if it hits from above or below the y dir flips
        if pos_check((x,y+1),grid)==True:
            if grid[x,y+1]=='A':
                vy=-vy
            elif grid[x,y+1]=='B': # opaque
                absorbed=True # this tag makes it so that the while loop closes
            elif grid[x,y+1]=='C':
                refract_traj=run_laser(((x+2*vx,y+2*vy),(vx,vy)),grid)
                # start a new laser with the same direction to pass through
                # have to advance the step by two so that it doesn't intersect the same block again
                # add those points to the end so it doesn't mess up the queue
                vy=-vy
        if pos_check((x,y-1),grid)==True:
            if grid[x,y-1]=='A':
                vy=-vy
            elif grid[x,y-1]=='B':
                absorbed=True
            elif grid[x,y-1]=='C':
                refract_traj=run_laser(((x+2*vx,y+2*vy),(vx,vy)),grid)
                vy=-vy
        # if it hits from left or right the x dir flips
        if pos_check((x+1,y),grid)==True:
            if grid[x+1,y]=='A':
                vx=-vx
            elif grid[x+1,y]=='B':
                absorbed=True
            elif grid[x+1,y]=='C':
                refract_traj=run_laser(((x+2*vx,y+2*vy),(vx,vy)),grid)
                vx=-vx
        if pos_check((x-1,y),grid)==True:
            if grid[x-1,y]=='A':
                vx=-vx 
            elif grid[x-1,y]=='B':
                absorbed=True
            elif grid[x-1,y]=='C':
                refract_traj=run_laser(((x+2*vx,y+2*vy),(vx,vy)),grid)
                # have to start the new laser from 2 steps forward so it doesn't interact with C again
                # but then we lose that point in the trajectory so I'm gonna put it back at the end
                refract_traj.append((x+vx,y+vy))
                vx=-vx

        
        laser_traj.insert(0,(x+vx,y+vy))
        x,y=laser_traj[0][0],laser_traj[0][1]

    # have to delete the last new point that broke the loop
    del laser_traj[0]
    for point in refract_traj:
        laser_traj.append(point)
    return(laser_traj)

def game_plotter(laser_traj,grid,points):
    ''' uses matplotlib to visualize game board
        blocks are represented with squares:
            blue = A (reflect)
            black = B (opaque)
            yellow = C (refract)
        laser is represented with red points
        target points are represented with X's
            black if not hit
            red if hit'''
    
    x_dim,y_dim = np.shape(grid)[0], np.shape(grid)[1]

    for i in range(x_dim):
        for j in range(y_dim):
            if grid[i,j]=='A':
                plt.scatter(i,j,s=1000,c='b',marker='s')
            elif grid[i,j]=='B':
                plt.scatter(i,j,s=1000,c='k',marker='s')
            elif grid[i,j]=='C':
                plt.scatter(i,j,s=1000,c='y',marker='s')
    for point in points:
        if point in laser_traj:
            plt.scatter(point[0],point[1],c='r',marker='x')
        else:
            plt.scatter(point[0],point[1],c='k',marker='x')
    las_x,las_y=[],[]
    for point in laser_traj:
        las_x.append(point[0])
        las_y.append(point[1])
    plt.scatter(las_x,las_y,c='r',marker='.')

    plt.gca().set_xlim([0,x_dim-1])
    plt.gca().set_ylim([0,y_dim-1])
    plt.gca().invert_yaxis()

    plt.show()

if __name__=="__main__":
    rows,blocks,lasers,points=read_bff('bff_files/yarn_5.bff')
    # print(rows)
    # print(blocks)
    # print(lasers)
    # print(points)

    grid=grid_reader(rows)

    # grid[1,3]='C'
    traj=run_laser(lasers[0],grid)

    game_plotter(traj,grid,points)




