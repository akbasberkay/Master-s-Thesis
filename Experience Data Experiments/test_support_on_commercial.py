import numpy as np
import matplotlib.pyplot as plt
import obtained_support_values as sup
import random
import obtained_x_coordinates as xco
import obtained_y_coordinates as yco
import distance_data as dist
import math

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

def normalize_support(sup_matrix):
    max_key = max(sup_matrix, key=sup_matrix.get)
    min_key = min(sup_matrix, key=sup_matrix.get)
    return_sup_matrix = dict()
    for i,j in A:
        normalized_value = (sup_matrix[i,j] - sup_matrix[min_key]) / (sup_matrix[max_key] - sup_matrix[min_key])
        return_sup_matrix[i,j] = normalized_value
    return_symmetric = return_sup_matrix #dict()
    #for i,j in A:
    #    mean = return_sup_matrix[i,j] + return_sup_matrix[j,i] 
    #    return_symmetric[i,j] = mean
    return return_symmetric

def normalize_cost(cost_matrix):
    max_key = max(cost_matrix, key=cost_matrix.get)
    min_key = min(cost_matrix, key=cost_matrix.get)
    return_cost_matrix = dict()
    for i,j in A:
        normalized_value = (cost_matrix[i,j] - cost_matrix[min_key]) / (cost_matrix[max_key] - cost_matrix[min_key])
        return_cost_matrix[i,j] = normalized_value
    return return_cost_matrix

global n
n = 30
global N
N = [i for i in range(1, n+1)]
print(N)
global V
V = [0] + N
print(V)
x_coordinates = xco.x_values()
y_coordinates = yco.y_values()
global xc
xc = x_coordinates
global yc
yc = y_coordinates
#random.seed(20)
q = {(i):random.randint(5,15) for i in range(1,n+1)}
N = [i for i in range(1, n+1)]
V = [0] + N
global A
A = [(i, j) for i in V for j in V if i != j]
cost_matrix = dist.get_distance_data()
c = cost_matrix.copy()
cost_matrix = normalize_cost(c)
Q = 70
global support
support = sup.support_values()
#print("original support Values: ", support)
support_copy = dict()

for i in range(len(N) +1):
    support_copy[i,i] = 0.01
for i,j in A:
    #print("support[ij]: ", support[i,j])
    if support[i,j] == 0:
        support_copy[i,j] = 0.01
    else:
        support_copy[i,j] = support[i,j]
support = normalize_support(support)
support_matrix_something = support.copy()    
#print("support: ", support)
support_matrix_berkay = dict()
for key, value in support_matrix_something.items():
    #print("key:",key)
    #print(value)
    if value:
        support_matrix_berkay[key] = 1 / value
    else:
        support_matrix_berkay[key] = 1 / 0.01
#print("support_berkay values after everything: ", support_matrix_berkay)
#print("cost: ", cost_matrix)
support_matrix = normalize_support(support_matrix_berkay)
print("son sup matrix: ", support_matrix)

def get_rs(demand_dict, vehicle_capacity, set_s):
    demand_sum = 0
    for i in set_s:
        demand_sum += demand_dict[i]
    r_s = math.ceil(demand_sum / vehicle_capacity)
    return r_s

def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        vals = model.cbGetSolution(model._vars)
        sum_ = 0
        for key,value in vals.items():
            sum_ += cost_matrix[key] * vals[key]
        print("Cost_Sum: ", sum_)


from gurobipy import Model, GRB, quicksum


mdl = Model('CVRP')

x = mdl.addVars(A, vtype=GRB.BINARY)
u = mdl.addVars(N, vtype=GRB.CONTINUOUS)
mdl._vars = x
mdl.modelSense = GRB.MINIMIZE
mdl.setObjective(quicksum(x[i, j]*cost_matrix[i, j] for i, j in A) + quicksum(x[i, j]*support_matrix[i, j] for i, j in A))
#mdl.setObjective(quicksum(x[i, j]*cost_matrix[i, j] for i, j in A))

mdl.addConstrs(quicksum(x[i, j] for j in V if j != i) == 1 for i in N)
mdl.addConstrs(quicksum(x[i, j] for i in V if i != j) == 1 for j in N)

mdl.addConstrs((x[i, j] == 1) >> (u[i]+q[j] == u[j])
               for i, j in A if i != 0 and j != 0)
mdl.addConstrs(u[i] >= q[i] for i in N)
mdl.addConstrs(u[i] <= Q for i in N)

mdl.Params.MIPGap = 0.01
#mdl.Params.TimeLimit = 300  # seconds
mdl.optimize(subtourelim)
obj_value = mdl.objVal
solution = {(key,value): x[key,value].X for key,value in x}
print(solution)
active_arcs = [a for a in A if x[a].x > 0.99]
fig = plt.figure()
ax = fig.add_subplot()
title_of_figure = "JD Dataset with " + str(n) + " customers"
ax.set_title(title_of_figure)
for i, j in active_arcs:
    ax.plot([xc[i], xc[j]], [yc[i], yc[j]], c='g', zorder=0)
ax.text(31.195,121.40,"objective_value = " + str(truncate(obj_value, 3)))
ax.plot(xc[0], yc[0], c='r', marker='s')
ax.scatter(xc[1:], yc[1:], c='b')
ax.set_xlabel('latitude')
ax.set_ylabel('longitude')

plt.show()