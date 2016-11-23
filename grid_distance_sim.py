
import random 
import math

#Grid size in smartcar simulation
Ny, Nx = 8, 6

#Possible x, y values in the grid
x_values = range(Nx)
y_values = range(Ny)

#Place to store distance and success status
d_list = []
s_list = []

#Repeat many times
random.seed(327)
for i in range(100000):
    
    #Pick Random Starting Location
    x1 = random.choice(x_values)
    y1 = random.choice(y_values)
    
    #Pick Random Destination
    x2 = random.choice(x_values)
    y2 = random.choice(y_values)
	
    #Calculate Manhattan Distance
    d = abs(x1-x2)+abs(y1-y2)
    d_list.append(d)
    
    #See if the car makes it to the target via random
    #   walk similar to untrained smartcar (Max steps
    #   set to match smartcar simulation)
    s = 0
    n_step=0
    while s == 0 and n_step <= 5*d:
        #Decide which way to move
        move = random.choice(['N','S','E','W',None])
        if move == 'N':
            y1 = min(y1+1,max(y_values))
        elif move == 'S':
            y1 = max(y1-1,min(y_values))
        elif move == 'E':
            x1 = min(x1+1,max(x_values))
        elif move == 'W':
            x1 = max(x1-1,min(x_values))
        #See if destination reached
        if (x1,y1) == (x2,y2):
            s = 1
        #increment step count
        n_step += 1
    s_list.append(s)

#expected distance
print float(sum(d_list))/len(d_list)

#estimated probability of reaching destination on time 
print float(sum(s_list))/len(s_list)


