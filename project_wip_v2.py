import numpy as np 
import matplotlib.pyplot as plt
import time

def read_bff(bff):
    ''' 
    Reads board file format (.bff)
    *** Args ***
        bff: str
            name of file to be read
    *** Returns ***
        game_grid: np array
        num_blocks: tuple, int
            (num_A,num_B,num_C) to be placed
        lasers: list, tuple, tuple, int
            list of lasers as tuples
            each tuple contains lasers starting point (x,y) and direction (vx,vy)
        points: list, tuple, int
            list of target points (x,y)
    returns(game_grid,num_blocks,lasers,points)
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
    def grid_reader(rows):
        ''' interprets list of gameboard rows into xy grid as a numpy array'''
        y_dim=len(rows)
        x_dim=len(rows[0].split(' '))
        grid=np.zeros((2*y_dim+1,2*x_dim+1),dtype=str)
        # 2*length+1 to get the full size of grid including the even spaces
        # see the handout for explanation of grid indexing
        for j in range(y_dim):
            for i in range(x_dim):
                grid[2*j+1,2*i+1]=rows[j].split(' ')[i]
                # place the symbols from the board into corresponding index of the grid
        return grid
    game_grid=grid_reader(rows)

    def get_block_list(blocks):
        ''' input (num_A,num_B,num_C), return list of A's,B's, and C's'''
        num_A, num_B, num_C = blocks[0],blocks[1],blocks[2]
        block_list=[]
        for i in range(num_A):
            block_list.append('A')
        for i in range(num_B):
            block_list.append('B')
        for i in range(num_C):
            block_list.append('C')
        return block_list

    return(game_grid,(num_A,num_B,num_C),lasers,points)

def get_block_list(blocks):
    ''' input (num_A,num_B,num_C), return list of A's,B's, and C's'''
    num_A, num_B, num_C = blocks[0],blocks[1],blocks[2]
    block_list=[]
    for i in range(num_A):
        block_list.append('A')
    for i in range(num_B):
        block_list.append('B')
    for i in range(num_C):
        block_list.append('C')
    return block_list

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
    x_dim,y_dim = np.shape(grid)[1], np.shape(grid)[0]
    if point[0]<0 or point[0]>x_dim-1:
        return False
    elif point[1]<0 or point[1]>y_dim-1:
        return False
    else:
        return True


def run_laser(laser,grid):
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
    # using this limiter so that the while loop can close if there's an infinite reflection

    # grab initial positions and velocities from the laser input
    x1,y1=laser[0][0],laser[0][1]
    vx,vy=laser[1][0],laser[1][1]
    # first point of the trajectory
    laser_traj=[laser[0]]

    # initializing
    absorbed=False 
    refract_traj=[]
    neighbors=[]
    
    # gathering list of blocks adjacent to the start of the laser
    for coords in [[y1,x1-1],[y1,x1+1],[y1-1,x1],[y1+1,x1]]:
        try:
            dummy=grid[coords[0],coords[1]]
            neighbors.append(coords)
        except IndexError:
            pass
        
    ### special cases for the start of the laser
    blocknames=['A','B','C']
    if any(grid[coord[0],coord[1]] in blocknames for coord in neighbors)==True: # if laser origin has an adjacent block
        if y1 % 2 ==0: # if the laser can start with a block above or below it
            ### SANDWICH CONDITIONS
            if pos_check((x1,y1+1),grid)==True and pos_check((x1,y1-1),grid)==True:
                if grid[y1+1,x1]=='A' and grid[y1-1,x1]=='A':
                    return laser_traj 
                    # if it's stuck between two reflect blocks it can't go anywhere, return the original position
                elif grid[y1+1,x1]=='B' or grid[y1-1,x1]=='B':
                    absorbed=True 
                    # if it's stuck between two opaque blocks it gets absorbed
                    return laser_traj
                elif grid[y1+1,x1]=='C' and grid[y1-1,x1]=='C':
                    # if it's between two refract blocks then we will propagate two new lasers in the positive and negative dir
                    traj_pos=run_laser(((x1+2*vx,y1+2*vy),(vx,vy)),grid) # skipping two spaces so it doesn't get stuck on the same block
                    traj_pos.append((x1+vx,y1+vy)) # adding this block back in manually so it doesn't interact
                    traj_neg=run_laser(((x1+2*vx,y1-2*vy),(vx,-vy)),grid) # skipping two spaces so it doesn't get stuck on the same block
                    traj_neg.append((x1+vx,y1-vy)) # adding this block back in manually so it doesn't interact
                    for point_pos in traj_pos:
                        laser_traj.append(point_pos) 
                    for point_neg in traj_neg:
                        laser_traj.append(point_neg)
                elif grid[y1+1,x1]=='C' and grid[y1-1,x1]=='A':
                    vy=abs(vy) # if the clear block is in positive direction, laser propagates in positive
                    traj=run_laser(((x1+2*vx,y1+2*vy),(vx,vy)),grid)
                    traj.append((x1+vx,y1+vy)) # adding this block back in manually so it doesn't interact
                    for point in traj:
                        laser_traj.append(point)
                elif grid[y1+1,x1]=='A' and grid[y1-1,x1]=='C':
                    vy=-abs(vy) # if the clear block is in negative direction, laser propagates in positive
                    traj=run_laser(((x1+2*vx,y1+2*vy),(vx,vy)),grid)
                    traj.append((x1+vx,y1+vy)) # adding this block back in manually so it doesn't interact
                    for point in traj:
                        laser_traj.append(point)

            if vy>0: # if the laser is traveling down
                if pos_check((x1,y1+1),grid)==True:
                    if grid[y1+1,x1]=='A':
                        vy=-vy
                    elif grid[y1+1,x1]=='B': # block below is opaque
                        absorbed=True
                    elif grid[y1+1,x1]=='C':
                        refract_traj=run_laser(((x1+vx,y1+vy),(vx,vy)),grid)
                        vy=-vy
            else: # if the laser is traveling up
                if pos_check((x1,y1-1),grid)==True:
                    if grid[y1-1,x1]=='A':
                        vy=-vy
                    elif grid[y1-1,x1]=='B': # block above is opaque
                        absorbed=True
                    elif grid[y1-1,x1]=='C':
                        refract_traj=run_laser(((x1+vx,y1+vy),(vx,vy)),grid) 
                        vy=-vy
        else: # the block is to the left or right
            ### SANDWICH CONDITIONS
            ### follows the same logic as the conditions above
            ### this code could probably be condensed a lot but I can't prioritize that rn
            if pos_check((x1+1,y1),grid)==True and pos_check((x1-1,y1),grid)==True:
                if grid[y1,x1+1]=='A' and grid[y1,x1-1]=='A':
                    return laser_traj
                elif grid[y1,x1+1]=='B' or grid[y1,x1-1]=='B':
                    absorbed=True
                    return laser_traj
                elif grid[y1,x1+1]=='C' and grid[y1,x1-1]=='C':
                    traj_pos=run_laser(((x1+2*vx,y1+2*vy),(vx,vy)),grid)
                    traj_pos.append((x1+vx,y1+vy)) # adding this block back in manually so it doesn't interact
                    traj_neg=run_laser(((x1-2*vx,y1+2*vy),(-vx,vy)),grid)
                    traj_neg.append((x1+vx,y1-vy)) # adding this block back in manually so it doesn't interact
                    for point_pos in traj_pos:
                        laser_traj.append(point_pos)
                    for point_neg in traj_neg:
                        laser_traj.append(point_neg)
                    return laser_traj
                elif grid[y1,x1+1]=='C' and grid[y1,x1-1]=='A':
                    vx=abs(vx)
                    traj=run_laser(((x1+2*vx,y1+2*vy),(vx,vy)),grid)
                    traj.append((x1+vx,y1+vy)) # adding this block back in manually so it doesn't interact
                    for point in traj:
                        laser_traj.append(point)
                    return laser_traj
                elif grid[y1,x1+1]=='A' and grid[y1,x1-1]=='C':
                    vx=-abs(vx)
                    traj=run_laser(((x1+2*vx,y1+2*vy),(vx,vy)),grid)
                    traj.append((x1+vx,y1+vy)) # adding this block back in manually so it doesn't interact
                    for point in traj:
                        laser_traj.append(point)
                    return laser_traj
                    
            if vx>0: # if the laser is traveling right
                if pos_check((x1+1,y1),grid)==True:
                    if grid[y1,x1+1]=='A':
                        vx=-vx
                    elif grid[y1,x1+1]=='B': 
                        absorbed=True
                    elif grid[y1,x1+1]=='C':
                        # refract_traj=run_laser(((x1+2*vx,y1+2*vy),(vx,vy)),grid)
                        refract_traj=run_laser(((x1+vx,y1+vy),(vx,vy)),grid)
                        vx=-vx
            else: # if the laser is traveling left
                if pos_check((x1-1,y1),grid)==True:
                    if grid[y1,x1-1]=='A':
                        vx=-vx
                    elif grid[y1,x1-1]=='B': 
                        absorbed=True
                    elif grid[y1,x1-1]=='C':
                        # refract_traj=run_laser(((x1+2*vx,y1+2*vy),(vx,vy)),grid)
                        refract_traj=run_laser(((x1+vx,y1+vy),(vx,vy)),grid)
                        vx=-vx
    laser_traj.insert(0,(x1+vx,y1+vy)) # insert the first new point of the trajectory
    x,y=laser_traj[0][0],laser_traj[0][1] # grab x and y points
    ### now that we've handled the special cases of the laser at the origin
    ### we can propagate the rest of the trajectory with a while loop
    
    for point in refract_traj: # save any of the refracted points at the end so they don't mess up the queue
        laser_traj.append(point)        

    refract_traj=[] # re initialize an empty array to hold new refracted points

    counter=0 # use this to end the loop if the laser is stuck within the grid
    # this loop will update new positions to the start of the trajectory list
    while pos_check(laser_traj[0],grid)==True and absorbed==False and counter<limiter:
        counter+=1
        ### BLOCK CONDITIONALS
        # if it hits from above or below the y dir flips
        if pos_check((x,y+1),grid)==True:
            if grid[y+1,x]=='A':
                vy=-vy
            elif grid[y+1,x]=='B': # opaque
                absorbed=True # this tag makes it so that the while loop closes
            elif grid[y+1,x]=='C':
                # refract_traj=run_laser(((x+2*vx,y+2*vy),(vx,vy)),grid)
                refract_traj=run_laser(((x+vx,y+vy),(vx,vy)),grid)
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
                # refract_traj=run_laser(((x+2*vx,y+2*vy),(vx,vy)),grid)
                refract_traj=run_laser(((x+vx,y+vy),(vx,vy)),grid)
                vy=-vy
        # if it hits from left or right the x dir flips
        if pos_check((x+1,y),grid)==True:
            if grid[y,x+1]=='A':
                vx=-vx
            elif grid[y,x+1]=='B':
                absorbed=True
            elif grid[y,x+1]=='C':
                # refract_traj=run_laser(((x+2*vx,y+2*vy),(vx,vy)),grid)
                refract_traj=run_laser(((x+vx,y+vy),(vx,vy)),grid)
                vx=-vx
        if pos_check((x-1,y),grid)==True:
            if grid[y,x-1]=='A':
                vx=-vx 
            elif grid[y,x-1]=='B':
                absorbed=True
            elif grid[y,x-1]=='C':
                # refract_traj=run_laser(((x+2*vx,y+2*vy),(vx,vy)),grid)
                refract_traj=run_laser(((x+vx,y+vy),(vx,vy)),grid)
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

def get_open(grid):
    ''' gets list of spaces in a grid where a block can be placed
    ***Args
        grid: np array
    ***Returns
        open_spaces: list, tuple, int
            IMPORTANT: returns coords as yx in same order as numpy indexing'''
    open_spaces=[]
    x_dim,y_dim = np.shape(grid)[1], np.shape(grid)[0]
    for i in range(x_dim):
        for j in range(y_dim):
            if grid[j,i]=='o':
                open_spaces.append((i,j))
    return open_spaces

def get_configs_v2(grid,num_blocks):
    ##### TRYING A NEW STRATEGY TO TRY TO MAKE ITERATION FASTER
    ##### iterate through each space in the grid and update the possible choices 
    ##### (remove a block as a choice when the number exceeds the number input)
    '''
    Args: num_blocks tuple (num_A,num_B,num_C)'''
    configs=[] # intialize
    opens=get_open(grid)
    final_A,final_B,final_C=num_blocks[0],num_blocks[1],num_blocks[2]
    final_O=len(opens)-final_A-final_B-final_C # num of open blocks we need in the final puzzle
    final_nums=[final_A,final_B,final_C,final_O]

    def get_choices(grid):
        num_A,num_B,num_C,num_O=0,0,0,0 # initialize
        x_dim,y_dim = np.shape(grid)[1], np.shape(grid)[0]
        for i in range(x_dim): # go through the grid and count each type
            for j in range(y_dim):
                if grid[j,i]=='A':
                    num_A+=1
                elif grid[j,i]=='B':
                    num_B+=1
                elif grid[j,i]=='C':
                    num_C+=1
                elif grid[j,i]=='0': # the 0 represents a space being intentionally left open (as opposed to 'o' being unvistited)
                    num_O+=1
        choices=[] # initialize
        for k in range(len(['A','B','C','0'])):
            if [num_A,num_B,num_C,num_O][k]<[final_A,final_B,final_C,final_O][k]:
                choices.append([final_A,final_B,final_C,final_O][k])
        return choices
    
    poss_choices=['A','B','C','O']
    def get_choices_new(num_list):
        choices=[] # initialize
        for k in range(len(poss_choices)):
            if num_list[k]<final_nums[k]:
                choices.append(poss_choices[k])
        return choices

    def config_iter_v2(num_list,iter):
        if iter==len(opens)-1: # this makes it so that we only save the configurations in the last iteration
            choices=get_choices_new(num_list)
            for c2 in range(len(choices)):
                for k in range(len(poss_choices)):
                    if choices[c2]==poss_choices[k]:
                        num_list[k]+=1
                        break
                space=opens[iter]
                grid[space[1],space[0]]=choices[c2] # place the block in an open space
                # print(grid)
                grid_list=grid.tolist() # convert to list to avoid problems with np datatypes
                if grid_list not in configs:
                    configs.append(grid_list) # save that placement to the list of possible configurations
                num_list[k]+=-1
        else:
            choices=get_choices_new(num_list)
            for c1 in range(len(choices)):
                for k in range(len(poss_choices)):
                    if choices[c1]==poss_choices[k]:
                        num_list[k]+=1
                        break
                space=opens[iter]
                grid[space[1],space[0]]=choices[c1]
                config_iter_v2(num_list,iter+1)
                num_list[k]+=-1
        return
    
    num_list=[0,0,0,0] # initialize with no choices made yet
    config_iter_v2(num_list,0)

    # assert num_list==final_nums

    return configs


def get_configs(grid,blocks):
    ''' have to input list of blocks not number of blocks'''
    # print('getting possible board configs (this may take a while)')
    configs=[]
    
    if len(blocks)>len(get_open(grid)):
        ### put some raise error here for too many blocks
        return
    
    def config_iteration(grid,iter):
        if iter==len(blocks)-1: # this makes it so that we only save the configurations in the last iteration
            opens=get_open(grid)
            for i in range(len(opens)):
                space=opens[i]
                grid[space[1],space[0]]=blocks[iter] # place the block in an open space
                grid_list=grid.tolist() # convert to list to avoid problems with np datatypes
                if grid_list not in configs:
                    configs.append(grid_list) # save that placement to the list of possible configurations
                grid[space[1],space[0]]='o' # remove the block so it can be placed in the next open space
            return
        else:
            opens=get_open(grid)
            for i in range(len(opens)):
                space=opens[i]
                grid[space[1],space[0]]=blocks[iter]
                config_iteration(grid,iter+1)
                grid[space[1],space[0]]='o'

    config_iteration(grid,0)

    return configs

def game_solver_v2(grid,num_blocks,lasers,points):
    ### CORRECTLY SOLVES TINY-5 AND SHOWSTOPPER-4
    ### CORRECLTY SOLVED NUMBERED-6 BUT IT TOOK 6 MINUTES
    ### FAILED ON DARK-1
    
    ''' finds configuration which hits all target points
    ***Args: all are outputs from the bff reader function
        grid: np array
        block_list: list, str
        lasers: list, tuple, tuple, int
        points: list, tuple, int'''
    
    configs=get_configs_v2(grid,num_blocks) # use function to get possible configs
    counter=0
    # we will iterate through the different configs and save the one that works
    print('testing board configurations')
    for config in configs:
        counter+=1
        config_grid=np.array(config) # remember that the configs returns a list of lists, we need to get back to np array
        lasers_trajs=[] # initialize
        # run each laser in the puzzle
        for laser in lasers:
            laser_traj=run_laser(laser,config_grid)
            for point in laser_traj:
                lasers_trajs.append(point)
        target_num=0 # initialize
        for target in points:
            if target in lasers_trajs:
                target_num+=1 # increase the number for each point that gets hit
                # could try to redo this with the all function but right now it's working so let's just be happy about that
        if target_num==len(points): # if we hit all the points we save the solved grid and break the loop
            print('Solved!')
            solved_grid=config_grid
            return solved_grid, lasers_trajs
    print('Solver failed')
    return 

def game_solver(grid,block_list,lasers,points):
    ### CORRECTLY SOLVES TINY-5 AND SHOWSTOPPER-4
    ### CORRECLTY SOLVED NUMBERED-6 BUT IT TOOK 6 MINUTES
    ### FAILED ON DARK-1
    
    ''' finds configuration which hits all target points
    ***Args: all are outputs from the bff reader function
        grid: np array
        block_list: list, str
        lasers: list, tuple, tuple, int
        points: list, tuple, int'''
    
    configs=get_configs(grid,block_list) # use function to get possible configs
    counter=0
    # we will iterate through the different configs and save the one that works
    print('testing board configurations')
    for config in configs:
        counter+=1
        config_grid=np.array(config) # remember that the configs returns a list of lists, we need to get back to np array
        lasers_trajs=[] # initialize
        # run each laser in the puzzle
        for laser in lasers:
            laser_traj=run_laser(laser,config_grid)
            for point in laser_traj:
                lasers_trajs.append(point)
        target_num=0 # initialize
        for target in points:
            if target in lasers_trajs:
                target_num+=1 # increase the number for each point that gets hit
                # could try to redo this with the all function but right now it's working so let's just be happy about that
        if target_num==len(points): # if we hit all the points we save the solved grid and break the loop
            print('Solved!')
            solved_grid=config_grid
            return solved_grid, lasers_trajs
    print('Solver failed')
    return 

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
    
    x_dim,y_dim = np.shape(grid)[1], np.shape(grid)[0]

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
    filename='tiny_5.bff'
    grid,num_blocks,lasers,points=read_bff('bff_files/'+filename)
    solution,trajs=game_solver(grid,get_block_list(num_blocks),lasers,points)
    print(solution)

    grid,num_blocks,lasers,points=read_bff('bff_files/'+filename)
    solution,trajs=game_solver_v2(grid,num_blocks,lasers,points)
    print(solution)

    game_plotter(trajs,solution,points)

    ### FOR TESTING CONFIGS
    # start_time=time.time()
    # new_configs=get_configs_v2(grid,num_blocks)
    # print('new minutes to configs')
    # print((time.time()-start_time)/60)


    # grid,num_blocks,lasers,points=read_bff('bff_files/'+filename)
    # start_time=time.time()
    # orig_configs=get_configs(grid,get_block_list(num_blocks))
    # print('orig minutes to configs')
    # print((time.time()-start_time)/60)


    # print(len(orig_configs))
    # print(len(new_configs))

    # configs=get_configs_v2(grid,num_blocks)
    # for config in configs:
    #     print(np.array(config))
    
    # ### BROKEN
    # test_grid=np.array(configs[1]) # this one is broken so keep checking this
    # lasers_trajs=[]
    # for laser in lasers:
    #     laser_traj=run_laser(laser,test_grid)
    #     for point in laser_traj:
    #         lasers_trajs.append(point)
    # game_plotter(lasers_trajs,test_grid,points)



    

    
    
    
    
    
    




