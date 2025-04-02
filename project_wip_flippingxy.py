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
    for j in range(x_dim):
        for i in range(y_dim):
            grid[2*j+1,2*i+1]=rows[i].split(' ')[j]
            # place the symbols from the board into corresponding index of the grid
    grid=np.transpose(grid) # inverts x and y
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
            if grid[y+1,x]=='A':
                vy=-vy
            elif grid[y+1,x]=='B': # opaque
                absorbed=True # this tag makes it so that the while loop closes
            elif grid[y+1,x]=='C':
                refract_traj=run_laser(((x+2*vx,y+2*vy),(vx,vy)),grid)
                # start a new laser with the same direction to pass through
                # have to advance the step by two so that it doesn't intersect the same block again
                # add those points to the end so it doesn't mess up the queue
                vy=-vy
        if pos_check((x,y-1),grid)==True:
            if grid[y-1,x]=='A':
                vy=-vy
            elif grid[y-1,x]=='B':
                absorbed=True
            elif grid[y-1,x]=='C':
                refract_traj=run_laser(((x+2*vx,y+2*vy),(vx,vy)),grid)
                vy=-vy
        # if it hits from left or right the x dir flips
        if pos_check((x+1,y),grid)==True:
            if grid[x,y+1]=='A':
                vx=-vx
            elif grid[x,y+1]=='B':
                absorbed=True
            elif grid[x,y+1]=='C':
                refract_traj=run_laser(((x+2*vx,y+2*vy),(vx,vy)),grid)
                vx=-vx
        if pos_check((x-1,y),grid)==True:
            if grid[y,x-1]=='A':
                vx=-vx 
            elif grid[y,x-1]=='B':
                absorbed=True
            elif grid[y,x-1]=='C':
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

def run_laser_debug(laser,grid):
    ### the problem is that it's detecting blocks next to the starting position before the laser moves
    ### when it should only be detecting when it's a "hit" from the trajectory
    ### maybe I can write special logic for the first interaction and then this code should work for the rest
    ### this seems to have worked but now it breaks when the starting point is sandwiched between two blocks
    ### so i need to deal with that
    
    '''runs laser from starting point with trajectory until it leaves the board
    *** Args
        laser: tuple, tuple, int
            laser as a tuple of starting coords (x,y) and trajectory (vx,vy)
        grid: np array
    *** Returns
        laser_traj: list, tuple, int
            list of laser positions in reverse
    '''
    
    x_dim,y_dim = np.shape(grid)[0], np.shape(grid)[1]
    limiter=(x_dim*y_dim)**2
    blocknames=['A','B','C']

    x1,y1=laser[0][0],laser[0][1]
    vx,vy=laser[1][0],laser[1][1]
    laser_traj=[laser[0]]

    absorbed=False
    refract_traj=[]
    ####### need some sort of try here for if the spaces not being in the grid
    neighbors=[]
    for coords in [[y1,x1-1],[y1,x1+1],[y1-1,x1],[y1+1,x1]]:
        try:
            dummy=grid[coords[0],coords[1]]
            neighbors.append(coords)
        except IndexError:
            pass
        
    # if grid[y1,x1-1] in blocknames or grid[y1,x1+1] in blocknames or grid[y1-1,x1] in blocknames or grid[y1+1,x1] in blocknames:
    if any(grid[coord[0],coord[1]] in blocknames for coord in neighbors)==True:
        # print('starting block detected')
        # print(laser_traj[0])
        if y1 % 2 ==0: # if the laser starts with a block above or below it
            # if it's sandwiched:
            if pos_check((x1,y1+1),grid)==True and pos_check((x1,y1-1),grid)==True:
                if grid[y1+1,x1]=='A' and grid[y1-1,x1]=='A':
                    return laser_traj
                
                ### add conditions for sandwiched between clear blocks
                ### opaque blocks are fine because they'll 
            if vy>0: # if the laser is traveling down
                if pos_check((x1,y1+1),grid)==True:
                    if grid[y1+1,x1]=='A':
                        vy=-vy
                    elif grid[y1+1,x1]=='B': # block above is opaque
                        absorbed=True
                    elif grid[y1+1,x1]=='C':
                        # refract_traj=run_laser(((x1+2*vx,y1+2*vy),(vx,vy)),grid)
                        refract_traj=run_laser_debug(((x1+vx,y1+vy),(vx,vy)),grid)
                        vy=-vy
            else: # if the laser is traveling up
                if pos_check((x1,y1-1),grid)==True:
                    if grid[y1-1,x1]=='A':
                        vy=-vy
                    elif grid[y1-1,x1]=='B': # block above is opaque
                        absorbed=True
                    elif grid[y1-1,x1]=='C':
                        # refract_traj=run_laser(((x1+2*vx,y1+2*vy),(vx,vy)),grid)
                        refract_traj=run_laser_debug(((x1+vx,y1+vy),(vx,vy)),grid) 
                        ##### maybe by adding this for the starting block conditions i don't need to skip 2 spaces anymore
                        ##### test that later
                        vy=-vy
        else: # the block is to the left or right

            if vx>0: # if the laser is traveling right
                if pos_check((x1+1,y1),grid)==True:
                    if grid[y1,x1+1]=='A':
                        vx=-vx
                    elif grid[y1,x1+1]=='B': # block above is opaque
                        absorbed=True
                    elif grid[y1,x1+1]=='C':
                        # refract_traj=run_laser(((x1+2*vx,y1+2*vy),(vx,vy)),grid)
                        refract_traj=run_laser_debug(((x1+vx,y1+vy),(vx,vy)),grid)
                        vx=-vx
            else: # if the laser is traveling left
                if pos_check((x1-1,y1),grid)==True:
                    if grid[y1,x1-1]=='A':
                        vx=-vx
                    elif grid[y1,x1-1]=='B': # block above is opaque
                        absorbed=True
                    elif grid[y1,x1-1]=='C':
                        # refract_traj=run_laser(((x1+2*vx,y1+2*vy),(vx,vy)),grid)
                        refract_traj=run_laser_debug(((x1+vx,y1+vy),(vx,vy)),grid)
                        vx=-vx
    laser_traj.insert(0,(x1+vx,y1+vy))
    x,y=laser_traj[0][0],laser_traj[0][1]
    
    for point in refract_traj:
        print('refraction')
        print(point)
        laser_traj.append(point)        
    ##############

    refract_traj=[] # re initialize an empty array to hold the refracted points
    x,y=laser_traj[0][0],laser_traj[0][1]

    counter=0 # use this to end the loop if the laser is stuck within the grid
    # update new positions to the start of the trajectory list
    # run as long as new position is within the grid
    while pos_check(laser_traj[0],grid)==True and absorbed==False and counter<limiter:
        # print(counter)
        # print(laser_traj[0])
        counter+=1
        ### BLOCK CONDITIONALS
        # if it hits from above or below the y dir flips
        if pos_check((x,y+1),grid)==True:
            if grid[y+1,x]=='A':
                vy=-vy
            elif grid[y+1,x]=='B': # opaque
                print('below')
                absorbed=True # this tag makes it so that the while loop closes
            elif grid[y+1,x]=='C':
                # refract_traj=run_laser(((x+2*vx,y+2*vy),(vx,vy)),grid)
                refract_traj=run_laser_debug(((x+vx,y+vy),(vx,vy)),grid)
                # start a new laser with the same direction to pass through
                # have to advance the step by two so that it doesn't intersect the same block again
                # add those points to the end so it doesn't mess up the queue
                vy=-vy
        if pos_check((x,y-1),grid)==True:
            if grid[y-1,x]=='A':
                vy=-vy
            elif grid[y-1,x]=='B':
                print('above')
                absorbed=True
            elif grid[y-1,x]=='C':
                # refract_traj=run_laser(((x+2*vx,y+2*vy),(vx,vy)),grid)
                refract_traj=run_laser_debug(((x+vx,y+vy),(vx,vy)),grid)
                vy=-vy
        # if it hits from left or right the x dir flips
        if pos_check((x+1,y),grid)==True:
            if grid[y,x+1]=='A':
                vx=-vx
            elif grid[y,x+1]=='B':
                print('right')
                absorbed=True
            elif grid[y,x+1]=='C':
                # refract_traj=run_laser(((x+2*vx,y+2*vy),(vx,vy)),grid)
                refract_traj=run_laser_debug(((x+vx,y+vy),(vx,vy)),grid)
                vx=-vx
        if pos_check((x-1,y),grid)==True:
            if grid[y,x-1]=='A':
                vx=-vx 
            elif grid[y,x-1]=='B':
                print('left')
                absorbed=True
            elif grid[y,x-1]=='C':
                # refract_traj=run_laser(((x+2*vx,y+2*vy),(vx,vy)),grid)
                refract_traj=run_laser_debug(((x+vx,y+vy),(vx,vy)),grid)
                # have to start the new laser from 2 steps forward so it doesn't interact with C again
                # but then we lose that point in the trajectory so I'm gonna put it back at the end
                refract_traj.append((x+vx,y+vy))
                vx=-vx

        laser_traj.insert(0,(x+vx,y+vy))
        x,y=laser_traj[0][0],laser_traj[0][1]

    # have to delete the last new point that broke the loop
    del laser_traj[0]
    for point in refract_traj:
        print('refraction')
        print(point)
        laser_traj.append(point)
    return(laser_traj)

def get_open(grid):
    ''' gets list of spaces in a grid where a block can be placed
    ***Args
        grid: np array
    ***Returns
        open_spaces: list, tuple, int'''
    open_spaces=[]
    x_dim,y_dim = np.shape(grid)[0], np.shape(grid)[1]
    for i in range(x_dim):
        for j in range(y_dim):
            if grid[i,j]=='o':
                open_spaces.append((i,j))
    return open_spaces

def get_configs(grid,blocks):
    # this needs to be done with some kind of recursion iterating through the blocks_list 
    # (see how it works for tiny_5)
    grid_orig=grid
    blocks_list=blocks
    configs=[]
    def block_placer(grid,blocks):
        while blocks!=[]:
            for space in get_open(grid):
                grid[space[0],space[1]]=blocks[0]
                configs.append(grid)
            blocks.pop(0)
    return

def get_block_list(blocks):
    '''
    ***Args
        blocks: tuple, int
            (num_A,num_B,num_C)
    ***Returns
        block_list: list, str
            list containing amount of A's,B's, and C's'''
    num_A, num_B, num_C = blocks[0],blocks[1],blocks[2]
    block_list=[]
    for i in range(num_A):
        block_list.append('A')
    for i in range(num_B):
        block_list.append('B')
    for i in range(num_C):
        block_list.append('C')
    return block_list

def get_configs_tiny_5_debug(grid,block_list):
    # gonna write a script to solve one puzzle in particular to help understand the problem in general
    # i think this is working now but it returns a list of nested lists instead of numpy arrays
    # so i'll need to convert back to array before feeding it to run laser
    configs=[]
    grid_place=grid
    # print(get_open(grid))
    for space_0 in get_open(grid_place):
        grid_place[space_0[0],space_0[1]]=block_list[0]
        # print('0')
        for space_1 in get_open(grid_place):
            grid_place[space_1[0],space_1[1]]=block_list[1]
            # print('1')
            for space_2 in get_open(grid_place):
                grid_place[space_2[0],space_2[1]]=block_list[2]
                # print('2')
                for space_3 in get_open(grid_place):
                    grid_place[space_3[0],space_3[1]]=block_list[3]    
                    grid_list=grid_place.tolist() # this line saved us i think
                    configs.append(grid_list)
                    grid_place[space_3[0],space_3[1]]='o'
                grid_place[space_2[0],space_2[1]]='o'
            grid_place[space_1[0],space_1[1]]='o'
        grid_place[space_0[0],space_0[1]]='o'
    
    configs_stripped=[]
    for config in configs:
        # print(config)
        if config not in configs_stripped:
            configs_stripped.append(config)
            # print(configs_stripped)
    return configs_stripped

def get_configs_tiny_5(grid,block_list):
    # gonna write a script to solve one puzzle in particular to help understand the problem in general
    # returns a list of nested lists because the numpy dtype was giving us trouble
    # so i'll need to convert back to array before feeding it to run laser
    configs=[]
    print(get_open(grid))
    for space_0 in get_open(grid):
        grid[space_0[0],space_0[1]]=block_list[0]
        for space_1 in get_open(grid):
            grid[space_1[0],space_1[1]]=block_list[1]
            for space_2 in get_open(grid):
                grid[space_2[0],space_2[1]]=block_list[2]
                for space_3 in get_open(grid):
                    grid[space_3[0],space_3[1]]=block_list[3]    
                    grid_ls=grid.tolist()
                    configs.append(grid_ls)
                    grid[space_3[0],space_3[1]]='o'
                grid[space_2[0],space_2[1]]='o'
            grid[space_1[0],space_1[1]]='o'
        grid[space_0[0],space_0[1]]='o'
    
    configs_stripped=[]
    for config in configs:
        if config not in configs_stripped:
            configs_stripped.append(config)
    return configs_stripped

def game_solver_tiny_5(grid,blocks,lasers,points):
    block_list=get_block_list(blocks)
    configs=get_configs_tiny_5_debug(grid,block_list)
    counter=0
    for config in configs:
        print(counter)
        counter+=1
        config_grid=np.array(config)
        lasers_trajs=[]
        for laser in lasers:
            print('running laser')
            laser_traj=run_laser_debug(laser,config_grid)
            lasers_trajs.append(laser_traj)
            print('laser ran')
        if all(point in lasers_trajs for point in points)==True:
            solved_grid=config_grid
            break
        print('config failed')
    return solved_grid, lasers_trajs

def game_plotter(laser_traj,grid,points):
    ''' uses matplotlib to visualize game board
        blocks are represented with squares:
            blue = A (reflect)
            black = B (opaque)
            yellow = C (refract)
        laser is represented with red points
        target points are represented with X's
            black if not hit
            red if hit
        *** Args
            laser_traj: list, tuple, int
                list of laser positions in reverse
            grid: np array
            points: list, tuple, int
                list of target coords '''
    
    x_dim,y_dim = np.shape(grid)[0], np.shape(grid)[1]

    for i in range(x_dim):
        for j in range(y_dim):
            if grid[j,i]=='A':
                plt.scatter(i,j,s=1000,c='b',marker='s')
            elif grid[j,i]=='B':
                plt.scatter(i,j,s=1000,c='k',marker='s')
            elif grid[j,i]=='C':
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
    rows,blocks,lasers,points=read_bff('bff_files/tiny_5.bff')
    grid=grid_reader(rows)
    
    # traj=run_laser(lasers[0],grid)

    # game_plotter(traj,grid,points)
    
    # print(grid)
    # print(get_open(grid))
    
    # print(get_configs_tiny_5_debug(grid,get_block_list(blocks)))
    configs=get_configs_tiny_5_debug(grid,get_block_list(blocks))
    # solution,trajs=game_solver_tiny_5(grid,blocks,lasers,points)
    
    config_grid=np.array(configs[69])
    print(config_grid)
    run_laser_debug(lasers[0],config_grid)
    # print(traj)
    # game_plotter(trajs,solution,points)
    
    
    
    
    
    




