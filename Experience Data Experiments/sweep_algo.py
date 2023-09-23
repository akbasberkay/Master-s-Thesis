import obtained_x_coordinates as xco
import obtained_y_coordinates as yco
import obtained_support_values as sup
import distance_data as dist
import random
import sys
import math
import numpy as np


from math import atan
 
# Function to find the
# angle between two lines
def findAngle(M1, M2, bolge):
    PI = 3.14159265
     
    # Store the tan value  of the angle
    angle = abs((M2 - M1) / (1 + M1 * M2))
 
    # Calculate tan inverse of the angle
    ret = atan(angle)
 
    # Convert the angle from
    # radian to degree
    val = (ret * 180) / PI
    # Print the result
    angle_before = round(val, 4)
    if bolge == 1:
        return_angle = angle_before
    elif bolge == 2:
        return_angle = 90 + (90 - angle_before) 
    elif bolge == 3:
        return_angle = 180 + angle_before
    elif bolge == 4:
        return_angle = 360 - angle_before
    return return_angle

def angle_between(p1, p2):
    if p1[0] == p2[0]:
        egim = (p2[1] - p1[1]) / 0.0000000001
    else:
        egim = (p2[1] - p1[1]) / (p2[0] - p1[0])
    bolge = 0
    if p2[1] > p1[1] and p2[0] > p1[0]:
        bolge = 1
    elif p2[1] > p1[1] and p2[0] < p1[0]:
        bolge = 2
    elif p2[1] < p1[1] and p2[0] < p1[0]:
        bolge = 3
    elif p2[1] < p1[1] and p2[0] > p1[0]:
        bolge = 4
    return findAngle(egim,0,bolge=bolge)

def main(num_of_cust):
    demand_dict = {(i):random.randint(5,15) for i in range(1,51)}

    x_coordinates = xco.x_values()
    y_coordinates = yco.y_values()
    vehicle_capacity = 70

    n = int(num_of_cust)
    N = [i for i in range(1, n+1)]
    V = [0] + N
    A = [(i, j) for i in V for j in V if i != j]
    cost_matrix = dist.get_distance_data()
    depot = (x_coordinates[0],y_coordinates[0])
    angle_dict = dict()
    for i in N:
        """ print("key1coords_x:", x_coordinates[i])
        print("key1coords_y:",y_coordinates[i])
        angle = math.atan(
                        (y_coordinates[i] - y_coordinates[0]) / (x_coordinates[i] - x_coordinates[0])
                          )
        print(math.degrees(angle)) # """
        second_point = (x_coordinates[i],y_coordinates[i])
        angle_dict[i] = angle_between(depot, second_point)
    print(sorted(angle_dict.items(),key=lambda x:x[1]))
    angle_sorted_customers = [i[0] for i in sorted(angle_dict.items(),key=lambda x:x[1])]
    print(angle_sorted_customers)
    routes = []
    subroute = []
    while angle_sorted_customers:
        print("subroute", subroute)
        print("angle_sorted_customers", angle_sorted_customers)
        cust_to_add = angle_sorted_customers[0]
        subroute.append(cust_to_add)
        subroute_demand_sum = 0
        for ele in subroute:
            subroute_demand_sum += demand_dict[ele]
        if subroute_demand_sum > vehicle_capacity:
            subroute.pop()
            routes.append(subroute)
            subroute = []
        else:
            angle_sorted_customers.pop(0)
        if not angle_sorted_customers:
            routes.append(subroute)
    print(routes)
    all_arcs = []
    for route in routes:
        all_arcs.append([0,route[0]])
        for ind in range(len(route) -1 ):
            all_arcs.append([route[ind],route[ind+1]])
        all_arcs.append([route[-1],0])
    print(all_arcs)
if __name__ == "__main__":
    main(sys.argv[1])