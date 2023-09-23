import networkx as nx

import gurobipy
import random

import math

import numpy as np
import matplotlib.pyplot as plt

rnd = np.random
rnd.seed(0)

n = 30  # number of clients
xc = rnd.rand(n+1)*200
yc = rnd.rand(n+1)*100

N = [i for i in range(1, n+1)]
V = [0] + N
A = [(i, j) for i in V for j in V if i != j]
c = {(i, j): np.hypot(xc[i]-xc[j], yc[i]-yc[j]) for i, j in A}
Q = 35
q = {i: rnd.randint(1, 10) for i in N}
number_of_vehicles = 3

demand_sum = 0
for i in N:
    demand_sum += q[i]
print(demand_sum)

vehicles_needed = math.ceil(demand_sum / Q)

print(vehicles_needed)

def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        # make a list of edges selected in the solution
        vals = model.cbGetSolution(mdl._vars)
        temp_active_arcs = [a for a in A if vals[a] >= 0.5]
        print("temp active arcs: " , temp_active_arcs)
        subroutes, violated_tours = constraint_finder(temp_active_arcs) 
        #print("subroutes: " , subroutes)
        #print("capacity violated routes:" , violated_tours)
        if subroutes:
            for route in subroutes:
                chosen_set = route.copy()
                chosen_set = [i[0] for i in chosen_set]                
                print("chosen set: ", chosen_set)
                not_chosen_set = [ele for ele in V]
                for a in chosen_set:
                    if a in V:
                        try:
                            not_chosen_set.remove(a)
                        except:
                            print("-------------------------rotada aptallık var-------------------------")
                demand_sum = 0
                if len(chosen_set) >= 2:
                    for customer in chosen_set:
                        demand_sum += q[customer]
                    left_hand_side_sum = 0
                    cross_list_array = [(i,j) for i in chosen_set for j in not_chosen_set]
                    array_to_add = [(j,i) for i in chosen_set for j in not_chosen_set]
                    for ele in array_to_add:
                        cross_list_array.append(ele)
                    for i,j in cross_list_array:
                        left_hand_side_sum += vals[i,j]
                    right_hand_side_sum = 2 * demand_sum / Q

                    if left_hand_side_sum <= right_hand_side_sum:
                        print("ilk if e girdim")
                        print("chosen set ",chosen_set," violates the subroute capacity inequality, is a cut candidate")
                        cut_candidate = list()
                        cut_candidate.append(cross_list_array)
                        r_h_s = 2 * demand_sum / Q
                        cut_candidate.append(r_h_s)                    
                        print(cut_candidate, " is added to the cutpool")
                        model.cbLazy(gurobipy.quicksum(x[i,j] for i,j in cut_candidate[0]) >= cut_candidate[1])
                
                
        if violated_tours:
            for route in violated_tours:
                print("vehicle capacity elimination route: " , route)
                model.cbLazy(gurobipy.quicksum(x[i,j] for i,j in route) <= len(route) - 1)
                model.cbLazy(gurobipy.quicksum(x[j,i] for i,j in route) <= len(route) - 1)

def constraint_finder(a):
    routes = []
    subroutes = []

    candidate_1 = []
    candidate_2 = []
    final_candidates = []
    subtour_number = 0
    looking_for_subtour = True
    inside_the_loop = True
    somevar = 0
    subtour_search_not_finished = True
    while True:
        found = False
        for i in a:
            if i[0] == 0:
                found = True
                candidate_1.append(i)
                a.remove(i)
        if found:
            continue
        else:
            break
    
#    print("candidate_1 before whiles: ",candidate_1)
#    candidate_3 = candidate_1
#    inside_route = True
#    normal_routes = []
#    candidate_4 = []
#    node_to_look = 0
#    while inside_route:
#        try:
#            someindex = candidate_3.index(node_to_look)
#            candidate_4.append(candidate_3[someindex])
#            
#        except:
#            inside_route = False
    while a != []:
        while inside_the_loop:
            somevar = 0
            for j in a:
                for k in candidate_1:
                    if k[1] == j[0]:
                        someindex = candidate_1.index(k)
                        candidate_1.insert(someindex+1,j)
                        somevar = somevar + 1
                        print(j)
                        a.remove(j)
                        continue  
            if somevar == 0:
                inside_the_loop = False
        inside_the_loop = True
        
        #print("candidate_1 after first while: ",candidate_1)
        
        while subtour_search_not_finished:

            if looking_for_subtour:
                chosen_element = random.choice(a)
                candidate_2.append(chosen_element)
                a.remove(chosen_element)
                subtour_number = subtour_number + 1
                looking_for_subtour = False
            else:
                while inside_the_loop:
                    somevar = 0
                    for p in a:
                        for m in candidate_2:
                            if m[1] == p[0]:
                                candidate_2.append(p)
                                somevar = somevar + 1
                                a.remove(p)
                                continue
                    if somevar == 0:
                        inside_the_loop = False
                        looking_for_subtour = True
                        final_candidates.append(candidate_2)
                        candidate_2 = []
                inside_the_loop = True

            if a == []:
                subtour_search_not_finished = False

    depot_ones = []
    start_index = 0
    end_index = 0
    for i in candidate_1:
        if i[1] == 0:
            end_index = candidate_1.index(i)
            depot_ones.append(candidate_1[start_index:end_index+1])
            start_index = end_index + 1

    vehicle_capacity = 35
    demand_dict = {i: random.randint(1, 10) for i in N}
    demand_dict.update({0:0})
    #print("depot ones: ",depot_ones)
    #print("candidate1 after everything : ",candidate_1)
    #print("candidate2 after everything : ",candidate_2)
    capacity_violated = []
    demand_sum = 0
    for i in range(len(depot_ones)):
        for j in range(len(depot_ones[i])):
            demand_sum += demand_dict[depot_ones[i][j][1]]
        if demand_sum > vehicle_capacity:
            print("route capacity violated in route", depot_ones[i])
            capacity_violated.append(depot_ones[i])
        demand_sum = 0

    return final_candidates,capacity_violated

from gurobipy import Model, GRB, quicksum

mdl = Model('CVRP')

x = mdl.addVars(A, vtype=GRB.BINARY)
#u = mdl.addVars(N, vtype=GRB.CONTINUOUS)
mdl.modelSense = GRB.MINIMIZE
mdl.setObjective(quicksum(x[i, j]*c[i, j] for i, j in A))

mdl.addConstrs(quicksum(x[i, j] for j in V if j != i) == 1 for i in N)
mdl.addConstrs(quicksum(x[i, j] for i in V if i != j) == 1 for j in N)
mdl.addConstr(quicksum(x[0,j] for j in V if j != 0) == vehicles_needed)
mdl.addConstrs((x[i, j] == 1) >> (x[j,i] == 0 ) for i, j in A)

#mdl.addConstrs((x[i, j] == 1) >> (u[i]+q[j] == u[j]) for i, j in A if i != 0 and j != 0)
#mdl.addConstrs(u[i] >= q[i] for i in N)
#mdl.addConstrs(u[i] <= Q for i in N)

mdl._vars = x

mdl.Params.MIPGap = 0.001
mdl.Params.TimeLimit = 300  # seconds
mdl.Params.lazyConstraints = 1
#mdl.update()
mdl.relax()
mdl.optimize(subtourelim)

active_arcs = [a for a in A if x[a].x > 0.99]

for i, j in active_arcs:
    plt.plot([xc[i], xc[j]], [yc[i], yc[j]], c='g', zorder=0)
plt.plot(xc[0], yc[0], c='r', marker='s')
plt.scatter(xc[1:], yc[1:], c='b')
plt.show()
print(active_arcs)
