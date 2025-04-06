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
    ids=['A','B','C','o','x']

    # loop through each line in the file 
    for i in range(len(lines)):
        
        if lines[i]=="GRID START":
            # if we read GRID START then we will loop through the subsequent lines that represent the grid rows
            for j in range (i+1,len(lines)):
                if lines[j]=="GRID STOP":
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
        # x_dim=len(rows[0].split(' '))
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
    ### moved around all the conditionals so that it only checks for blocks in x or y but not both based on y index parity
    ### should make for fewer logic checks
    ### also played with how the refract behavior works
    ### and changed it so that all the sandwich conditions have an inbuilt return
    ### testing it now
    
    '''runs laser from starting point with trajectory until it leaves the board
    *** Args
        laser: tuple, tuple, int
            laser as a tuple of starting coords (x,y) and trajectory (vx,vy)
        grid: np array
    *** Returns
        laser_traj: list, tuple, int
            list of laser positions in reverse
    '''
    block_ids=['A','B','C']
    # defining this to use in sandwich logic
    x_dim,y_dim = np.shape(grid)[1], np.shape(grid)[0]
    limiter=(x_dim*y_dim)**2
    # using this limiter so that the while loop can close if there's an infinite reflection

    # grab initial positions and velocities from the laser input
    x,y=laser[0][0],laser[0][1]
    vx,vy=laser[1][0],laser[1][1]
    # first point of the trajectory
    laser_traj=[laser[0]]

    # initializing
    absorbed=False 
    
    counter=0 # use this to end the loop if the laser is stuck within the grid
    # this loop will update new positions to the start of the trajectory list
    while pos_check(laser_traj[0],grid)==True and absorbed==False and counter<limiter:

        refract_traj=[] # initialize an empty array to hold new refracted points
        counter+=1
        
        if y % 2 ==0: # if the laser can start with a block above or below it
            ### first check if block is sandwiched
            ### SANDWICH CONDITIONS
            ### some of these will return the function if true
            if pos_check((x,y+1),grid)==True and pos_check((x,y-1),grid)==True and grid[y,x+1] in block_ids and grid[y,x-1] in block_ids:
                if grid[y+1,x]=='A' or grid[y+1,x]=='B' and grid[y-1,x]=='A' or grid[y-1,x]=='B':
                    return laser_traj 
                    # if it's stuck between any of these two blocks it can't go anywhere, return the original position
                elif grid[y+1,x]=='C' and grid[y-1,x]=='C':
                    # if it's between two refract blocks then we will propagate two new lasers in the positive and negative dir
                    traj_pos=run_laser(((x+vx,y+vy),(vx,vy)),grid) 
                    traj_neg=run_laser(((x+vx,y-vy),(vx,-vy)),grid) 
                    for point_pos in traj_pos:
                        laser_traj.append(point_pos) 
                    for point_neg in traj_neg:
                        laser_traj.append(point_neg)
                    return laser_traj
                elif grid[y+1,x]=='C' and grid[y-1,x]=='A':
                    vy=abs(vy) # if the clear block is in positive direction, laser propagates in positive
                    traj=run_laser(((x+vx,y+vy),(vx,vy)),grid)
                    for point in traj:
                        refract_traj.append(point)
                elif grid[y+1,x]=='A' and grid[y-1,x]=='C':
                    vy=-abs(vy) # if the clear block is in negative direction, laser propagates in positive
                    traj=run_laser(((x+vx,y+vy),(vx,vy)),grid)
                    for point in traj:
                        refract_traj.append(point)
            ### BLOCK CONDITIONALS
            # these do not cause a return so the while loop will continue to propagate laser positions
            elif pos_check((x,y+1),grid)==True and vy>0: # adding conditional here for the velocity to be in the right direction for a hit
                if grid[y+1,x]=='A':
                    vy=-vy 
                elif grid[y+1,x]=='B': # opaque
                    absorbed=True # this tag makes it so that the while loop closes
                elif grid[y+1,x]=='C':
                    refract_traj=run_laser(((x,y),(vx,-vy)),grid)
                    # start a new laser with the inverted velocity to reflect back from the hit position (xy)
                    # the original laser will propagate through with the same velocity
            elif pos_check((x,y-1),grid)==True and vy<0:
                if grid[y-1,x]=='A':
                    vy=-vy
                elif grid[y-1,x]=='B':
                    absorbed=True
                elif grid[y-1,x]=='C':
                    refract_traj=run_laser(((x,y),(vx,-vy)),grid)
                    # start a new laser with the inverted velocity to reflect back from the same position (xy)
                    # the original laser will propagate through with the same velocity
        else: # laser can have a block left or right
            ### SANDWICH CONDITIONS
            if pos_check((x+1,y),grid)==True and pos_check((x-1,y),grid)==True and grid[y,x+1] in block_ids and grid[y,x-1] in block_ids:
                if grid[y,x+1]=='A' or grid[y,x+1]=='B' and grid[y,x-1]=='A' or grid[y,x-1]=='B':
                    return laser_traj 
                    # if it's stuck between any of these two blocks it can't go anywhere, return the original position
                elif grid[y,x+1]=='C' and grid[y,x-1]=='C':
                    # if it's between two refract blocks then we will propagate two new lasers in the positive and negative dir
                    traj_pos=run_laser(((x+vx,y+vy),(vx,vy)),grid) 
                    traj_neg=run_laser(((x-vx,y+vy),(-vx,+vy)),grid) 
                    for point_pos in traj_pos:
                        laser_traj.append(point_pos) 
                    for point_neg in traj_neg:
                        laser_traj.append(point_neg)
                    return laser_traj
                elif grid[y,x+1]=='C' and grid[y,x-1]=='A':
                    vx=abs(vx) # if the clear block is in positive direction, laser propagates in positive
                    traj=run_laser(((x+vx,y+vy),(vx,vy)),grid)
                    for point in traj:
                        refract_traj.append(point)
                elif grid[y,x+1]=='A' and grid[y,x-1]=='C':
                    vx=-abs(vx) # if the clear block is in negative direction, laser propagates in positive
                    traj=run_laser(((x+vx,y+vy),(vx,vy)),grid)
                    for point in traj:
                        refract_traj.append(point)
            ### BLOCK CONDITIONALS
            # these do not cause a return so the while loop will continue to propagate laser positions
            elif pos_check((x+1,y),grid)==True and vx>0: # adding conditional here for the velocity to be in the right direction for a hit
                if grid[y,x+1]=='A':
                    vx=-vx
                elif grid[y,x+1]=='B': # opaque
                    absorbed=True # this tag makes it so that the while loop closes
                elif grid[y,x+1]=='C':
                    refract_traj=run_laser(((x,y),(-vx,vy)),grid)
                    # start a new laser with the inverted velocity to reflect back from the hit position (xy)
                    # the original laser will propagate through with the same velocity
            elif pos_check((x-1,y),grid)==True and vx<0:
                if grid[y,x-1]=='A':
                    vx=-vx
                elif grid[y,x-1]=='B':
                    absorbed=True
                elif grid[y,x-1]=='C':
                    refract_traj=run_laser(((x,y),(-vx,vy)),grid)
                    # start a new laser with the inverted velocity to reflect back from the same position (xy)
                    # the original laser will propagate through with the same velocity
        for point in refract_traj:
            laser_traj.append(point) # add all the refracted points to the end so they don't mess up the queue
        laser_traj.insert(0,(x+vx,y+vy)) # add the newest point to the front and grab new xy
        x,y=laser_traj[0][0],laser_traj[0][1]
    # have to delete the last new point that broke the loop
    del laser_traj[0]
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

def get_configs(grid,num_blocks):
    ''' returns list of each possible configuration (as a nested list)
    ***Args: 
        grid: np array
        num_blocks: tuple (num_A,num_B,num_C)
    *** Returns:
        configs: list, list, list, int
    '''
    configs=[] # intialize
    opens=get_open(grid)
    final_A,final_B,final_C=num_blocks[0],num_blocks[1],num_blocks[2]
    final_O=len(opens)-final_A-final_B-final_C # num of open blocks we need in the final puzzle
    final_nums=[final_A,final_B,final_C,final_O] # store final numbers we need in one array
    
    poss_choices=['A','B','C','O']
    def get_choices_new(num_list):
        choices=[] # initialize
        for k in range(len(poss_choices)):
            if num_list[k]<final_nums[k]:
                choices.append(poss_choices[k])
        return choices

    # loop through the different open positions and test each choice of block or open
    def config_iter(num_list,iter):
        if iter==len(opens)-1: # this makes it so that we only save the configurations in the last iteration
            choices=get_choices_new(num_list)
            for c2 in range(len(choices)):
                for k in range(len(poss_choices)):
                    if choices[c2]==poss_choices[k]:
                        num_list[k]+=1
                        break
                space=opens[iter]
                grid[space[1],space[0]]=choices[c2] # place the block in an open space
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
                config_iter(num_list,iter+1)
                num_list[k]+=-1
        return
    
    print('getting configurations')
    num_list=[0,0,0,0] # initialize with no choices made yet
    config_iter(num_list,0)

    # assert num_list==final_nums

    return configs


def game_solver(grid,num_blocks,lasers,points):
    ### CORRECTLY SOLVES numbered_6, showstopper_4, tiny_5, dark_1, mad_1, mad_3, mad_4, mad_5, mad_6, braid_6
    ### FAILED on mad_2
    ### mad_7 and yarn_5 take too long to run (don't know if they solve or not)

    
    ''' finds configuration which hits all target points
    ***Args: all are outputs from the bff reader function
        grid: np array
        block_list: list, str
        lasers: list, tuple, tuple, int
        points: list, tuple, int'''
    
    configs=get_configs(grid,num_blocks) # use function to get possible configs
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
        if all(point in lasers_trajs for point in points)==True:  # if we hit all the points we save the solved grid and break the loop 
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
    for traj in laser_traj:
        las_x.append(traj[0])
        las_y.append(traj[1])
    plt.scatter(las_x,las_y,c='r',marker='.')

    plt.gca().set_xlim([0,x_dim-1])
    plt.gca().set_ylim([0,y_dim-1])
    plt.gca().invert_yaxis()

    plt.show()

if __name__=="__main__":
    
    filename='mad_1.bff'
    grid,num_blocks,lasers,points=read_bff('bff_files/'+filename)
    print(grid)

    # real_solution=np.array(grid)
    # real_solution[5,3]='C'
    # real_solution[3,1],real_solution[1,5],real_solution[3,7]='A','A','A'
    # print(real_solution)

    solution,trajs=game_solver(grid,num_blocks,lasers,points)
    # new_configs=get_configs(grid,num_blocks)
    # print(len(new_configs))
    # test_board=np.array(new_configs[0])
    # traj=run_laser(lasers[0],test_board)
    game_plotter(trajs,solution,points)


    # for k in range(len(new_configs)):
    #     board=np.array(new_configs[k])
    #     if (board==real_solution).all():
    #         print('k')
    #         print(k)

    # test_board=np.array(new_configs[10])
    # print(test_board)
    # traj=run_laser(lasers[0],test_board)
    # print('final')
    # print(traj)
    # game_plotter(trajs,solution,points)

    # ### FOR TESTING CONFIGS
    # start_time=time.time()
    # new_configs=get_configs_v2(grid,num_blocks)
    # print('new minutes to configs')
    # print((time.time()-start_time)/60)

    # grid,num_blocks,lasers,points=read_bff('bff_files/'+filename)
    # start_time=time.time()
    # orig_configs=get_configs(grid,get_block_list(num_blocks))
    # print('orig minutes to configs')
    # print((time.time()-start_time)/60)


    




    

    
    
    
    
    
    




