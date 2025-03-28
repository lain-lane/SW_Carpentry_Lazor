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
    '''interpret rows list into grid as a numpy array'''
    y_dim=len(rows)
    x_dim=len(rows[0].split(' '))
    return np.zeros((x_dim,y_dim))

if __name__=="__main__":
    rows,blocks,lasers,points=read_bff('bff_files/yarn_5.bff')
    print(rows)
    print(blocks)
    print(lasers)
    print(points)

    grid=grid_reader(rows)
    print(grid)