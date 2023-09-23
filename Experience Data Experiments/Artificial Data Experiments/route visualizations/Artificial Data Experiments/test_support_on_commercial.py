import numpy as np
import matplotlib.pyplot as plt
import support_20 as sup
import random
import math

def normalize_cost(cost_matrix):
    max_key = max(cost_matrix, key=cost_matrix.get)
    min_key = min(cost_matrix, key=cost_matrix.get)
    return_cost_matrix = dict()
    for i,j in A:
        normalized_value = (cost_matrix[i,j] - cost_matrix[min_key]) / (cost_matrix[max_key] - cost_matrix[min_key])
        return_cost_matrix[i,j] = normalized_value
    return return_cost_matrix

global n
n = 20
global N
N = [i for i in range(1, n+1)]
print(N)
global V
V = [0] + N
print(V)
rnd = np.random
rnd.seed(0)
x_coordinates = rnd.rand(len(V))*200
y_coordinates = rnd.rand(len(V))*100
global xc
xc = x_coordinates
global yc
yc = y_coordinates
random.seed(20)
q = {(i):random.randint(5,15) for i in range(1,n+1)}
N = [i for i in range(1, n+1)]
V = [0] + N
A = [(i, j) for i in V for j in V if i != j]
c = {(i, j): np.hypot(xc[i]-xc[j], yc[i]-yc[j]) for i, j in A}
cost_matrix = normalize_cost(c)
Q = 70
global support
support = sup.get_support()
print(support)
support_copy = dict()

for i in range(len(N) +1):
    support_copy[i,i] = 0.001
for i,j in A:
    print("support[ij]: ", support[i,j])
    if support[i,j] == 0:
        support_copy[i,j] = 0.001
    else:
        support_copy[i,j] = support[i,j]
print(support_copy)

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

support_matrix = normalize_support(support_copy) 
print(support_matrix)

final_support = dict()
for i,j in A:
    print((i,j))
    print(support_matrix[i,j])
    if support_matrix[i,j] == 0:
        final_support[i,j] = 1000
    else:
        final_support[i,j] = 1 / support_matrix[i,j]

def get_rs(demand_dict, vehicle_capacity, set_s):
    demand_sum = 0
    for i in set_s:
        demand_sum += demand_dict[i]
    r_s = math.ceil(demand_sum / vehicle_capacity)
    return r_s


from gurobipy import Model, GRB, quicksum


mdl = Model('CVRP')

x = mdl.addVars(A, vtype=GRB.BINARY)
u = mdl.addVars(N, vtype=GRB.CONTINUOUS)

mdl.modelSense = GRB.MINIMIZE
mdl.setObjective(quicksum(x[i, j]*cost_matrix[i, j] for i, j in A))
#asas
mdl.addConstrs(quicksum(x[i, j] for j in V if j != i) == 1 for i in N)
mdl.addConstrs(quicksum(x[i, j] for i in V if i != j) == 1 for j in N)
mdl.addConstrs((x[i, j] == 1) >> (u[i]+q[j] == u[j])
               for i, j in A if i != 0 and j != 0)
mdl.addConstrs(u[i] >= q[i] for i in N)
mdl.addConstrs(u[i] <= Q for i in N)

mdl.Params.MIPGap = 0.01
#mdl.Params.TimeLimit = 300  # seconds
mdl.optimize()

active_arcs = [a for a in A if x[a].x > 0.99]
total_sum = 0
for ele in active_arcs:
    total_sum += cost_matrix[ele]
print("total_sum: ", total_sum)
for i, j in active_arcs:
    plt.plot([xc[i], xc[j]], [yc[i], yc[j]], c='g', zorder=0)
plt.plot(xc[0], yc[0], c='r', marker='s')
plt.scatter(xc[1:], yc[1:], c='b')

plt.show()