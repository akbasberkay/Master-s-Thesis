from gurobipy import Model, GRB, quicksum
import matplotlib.pyplot as plt
import numpy as np
import gurobipy
import math
import random

class Graph_struct:
    def __init__(self, M):
        self.M = M
        self.adj = [[] for i in range(M)]

    def DFS_Utililty(self, temp, v, visited):

        visited[v] = True

        temp.append(v)

        for i in self.adj[v]:
            if visited[i] == False:
                temp = self.DFS_Utililty(temp, i, visited)
        return temp

    def add_edge(self, v, w):
        self.adj[v].append(w)
        self.adj[w].append(v)

    def connected_components(self):
        visited = []
        conn_compnent = []
        for i in range(self.M):
            visited.append(False)
        for v in range(self.M):
            if visited[v] == False:
                temp = []
                conn_compnent.append(self.DFS_Utililty(temp, v, visited))
        return conn_compnent

def somethingnew(temp_active_arcs):
    tacopy = temp_active_arcs.copy()
    for i,j in temp_active_arcs:
        if i == 0 or j == 0:
            item = (i,j)
            tacopy.remove(item)           
    my_instance = Graph_struct(len(V))
    for ele in tacopy:
        i = ele[0]
        j = ele[1]
        my_instance.add_edge(i,j)
    conn_comp = my_instance.connected_components()
    conn_comp = conn_comp[1:]
    return conn_comp

def subtourelim(model,where):
    
    if where == GRB.Callback.MIPSOL:
        set_pool = []
        print("------------------------------------------------------")
        vals = model.cbGetSolution(model._vars)
        temp_active_arcs = gurobipy.tuplelist((i, j) for i, j in model._vars.keys()
                             if vals[i, j] > 0.5)
        print("temp_active_arcs: ", temp_active_arcs)
        subroutes = somethingnew(temp_active_arcs)
        print("subroutes: " , subroutes)
        if subroutes:
            for route in subroutes:
                chosen_set = route.copy()
                
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
                        returnval = False
                        continue  
        
        for berkay in range(100):
            for times in range(len(N) - 5):
                ele_num = times+3
                set_s = random.sample(N,ele_num)
                arcs_inside_s = []
                for ele in A:
                    if ele[0] in set_s and ele[1] in set_s:
                        arcs_inside_s.append(ele)
                l_h_s = 0
                for ele in arcs_inside_s:
                    l_h_s += vals[ele]
                k_value = 0
                for cust in set_s:
                    k_value += q[cust]
                k_value = k_value / Q
                r_h_s = len(set_s) - k_value
                if l_h_s > r_h_s:
                    cut_candidate = list()
                    cut_candidate.append(arcs_inside_s)
                    cut_candidate.append(r_h_s)
                    print("added the capcut of: ",cut_candidate)
                    model.cbLazy(gurobipy.quicksum(x[i,j] for i,j in cut_candidate[0]) <= cut_candidate[1])

        for ele_num in range(2,len(N) - 1):
            countnum = 0
            while ( ele_num + countnum ) < len(N): 
                nucleus = random.sample(N,ele_num)
                e_n = [(i,j, Q) for i,j in temp_active_arcs if i in nucleus and j in nucleus]
                not_nucleus = N.copy()
                for cust in nucleus:
                    not_nucleus.remove(cust)
                cross_list_array = [(i,j, q[j]) for i in nucleus for j in not_nucleus]
                array_to_add = [(j,i, q[j]) for i in nucleus for j in not_nucleus]
                for ele in array_to_add:
                    cross_list_array.append(ele)
                l_h_s_val = 0
                for arc in e_n:
                    somevar = (arc[0], arc[1])
                    l_h_s_val += Q * vals[somevar]
                for arc in array_to_add:
                    somevar = (arc[0], arc[1])
                    l_h_s_val += arc[2] * vals[somevar]
                demand_sum = 0
                for j in nucleus:
                    demand_sum += q[j]
                r_h_s = Q * len(nucleus) - demand_sum
                if l_h_s_val > r_h_s:
                    cut_candidate = list()
                    cut_candidate.append(e_n)
                    cut_candidate.append(cross_list_array)
                    cut_candidate.append(r_h_s)
                    model.cbLazy(gurobipy.quicksum(x[i,j] * k for i,j,k in cut_candidate[0]) + gurobipy.quicksum(x[i,j] * k for i,j,k in cut_candidate[1]) <= cut_candidate[2])
                countnum += 1
rnd = np.random
rnd.seed(0)
all_arcs = []


n = 25
Q = 30
N = [i for i in range(1, n+1)]
V = [0] + N
q = {i: rnd.randint(1, 10) for i in N}

loc_x = rnd.rand(len(V))*200
loc_y = rnd.rand(len(V))*100

A = [(i, j) for i in V for j in V if i != j]
c = {(i, j): np.hypot(loc_x[i]-loc_x[j], loc_y[i]-loc_y[j]) for i, j in A}

demand_sum = 0
for i in N:
    demand_sum += q[i]
print(demand_sum)

vehicles_needed = math.ceil(demand_sum / Q)

print(vehicles_needed)


mdl = Model('CVRP')
x = mdl.addVars(c.keys(), obj=c, vtype=GRB.BINARY, name='x')
mdl._vars = x
u = mdl.addVars(N, vtype=GRB.CONTINUOUS)

mdl.modelSense = GRB.MINIMIZE
mdl.setObjective(quicksum(x[i, j]*c[i, j] for i, j in A))

mdl.addConstrs(quicksum(x[i, j] for j in V if j != i) == 1 for i in N)
mdl.addConstrs(quicksum(x[i, j] for i in V if i != j) == 1 for j in N)
mdl.addConstr(quicksum(x[0,j] for j in V if j != 0) >= vehicles_needed)
mdl.addConstrs((x[i, j] == 1) >> (x[j,i] == 0 ) for i, j in A)
mdl.addConstrs((x[i, j] == 1) >> (u[i]+q[j] == u[j]) for i, j in A if i != 0 and j != 0)
mdl.addConstrs(u[i] >= q[i] for i in N)
mdl.addConstrs(u[i] <= Q for i in N)
mdl.Params.lazyConstraints = 1
mdl.Params.MIPGap = 0.01
mdl.relax()
mdl.optimize(subtourelim)
active_arcs = [a for a in A if x[a].x > 0.99]
print(active_arcs)
for i, j in active_arcs:
    plt.plot([loc_x[i], loc_x[j]], [loc_y[i], loc_y[j]], c='g', zorder=0)
plt.plot(loc_x[0], loc_y[0], c='r', marker='s')
plt.scatter(loc_x[1:], loc_y[1:], c='b')
plt.show()
