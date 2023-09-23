from gurobipy import Model, GRB, quicksum
import numpy as np
import math
import random
import matplotlib.pyplot as plt

rnd = np.random
num_of_customers = [20,25,30,35,40,45]
time_for_20 = []
time_for_25 = []
time_for_30 = []
time_for_35 = []
time_for_40 = []
time_for_45 = []
arcs_for_20 = []
arcs_for_25 = []
arcs_for_30 = []
arcs_for_35 = []
arcs_for_40 = []
arcs_for_45 = []
for ele in num_of_customers:
    for cnt in range(100):
        n = ele
        Q = 80
        N = [i for i in range(1, n+1)]
        V = [0] + N
        rnd.seed(random.randint(1,50))
        q = {i: rnd.randint(1, 10) for i in N}
        q[0] = 0
        rnd.seed(0)
        loc_x = rnd.rand(len(V))*200
        loc_y = rnd.rand(len(V))*100
        arcs_for_savings = [(i, j) for i in V for j in V if i != j]


        savings = {(i, j):    (np.hypot(loc_x[i]-loc_x[0], loc_y[i]-loc_y[0]))
                            +(np.hypot(loc_x[0]-loc_x[j], loc_y[0]-loc_y[j]))
                            -(np.hypot(loc_x[i]-loc_x[j], loc_y[i]-loc_y[j])) for i, j in arcs_for_savings}

        distance = {(i, j): np.hypot(loc_x[i]-loc_x[j], loc_y[i]-loc_y[j]) for i, j in arcs_for_savings}


        demand_sum = 0
        for i in N:
            demand_sum += q[i]
        print(demand_sum)

        r = math.ceil(demand_sum / Q)

        mdl = Model('CVRP')

        x = mdl.addVars(arcs_for_savings, vtype=GRB.BINARY)
        y = mdl.addVars(N, vtype=GRB.CONTINUOUS)
        mdl.setObjective(quicksum(x[i, j] * savings[i, j] for  i, j in arcs_for_savings), GRB.MAXIMIZE )

        mdl.addConstr(quicksum(x[ 0 , j ] for j in N) == r)
        mdl.addConstrs(quicksum(x[ i , j ] for i in V if i != j) == 1 for j in N)
        mdl.addConstrs(quicksum(x[ i , j ] for j in N if i != j) <= 1 for i in N)
        mdl.addConstrs(y[i]+ q[i-1]*x[ i , j ]- Q * ( 1 - x[ i , j ]) <= y[j] for i in N for j in N if i != j)
        mdl.addConstrs(q[ i-1 ] <= y[ i ] for i in N)
        mdl.addConstrs(y[ i ] <= Q for i in N)
        mdl.Params.MIPGap = 0.01
        mdl.optimize()

        active_arcs = [a for a in arcs_for_savings if x[a].x > 0.99]
        print(active_arcs)
        plt.figure()
        for i, j in active_arcs:
            plt.plot([loc_x[i], loc_x[j]], [loc_y[i], loc_y[j]], c='g', zorder=0)
        plt.plot(loc_x[0], loc_y[0], c='r', marker='s')
        plt.scatter(loc_x[1:], loc_y[1:], c='b')
        figname = str(ele) + str(cnt) + '.png'
        plt.savefig(figname)
        plt.close('all')

        if ele == 20:
            arcs_for_20.append(active_arcs)
            time_for_20.append(mdl.Runtime)
        elif ele == 25:
            arcs_for_25.append(active_arcs)
            time_for_25.append(mdl.Runtime)
        elif ele == 30:
            arcs_for_30.append(active_arcs)
            time_for_30.append(mdl.Runtime)
        elif ele == 35:
            arcs_for_35.append(active_arcs)
            time_for_35.append(mdl.Runtime)
        elif ele == 40:
            arcs_for_40.append(active_arcs)
            time_for_40.append(mdl.Runtime)
        elif ele == 45:
            arcs_for_45.append(active_arcs)
            time_for_45.append(mdl.Runtime)

        print("----------------------------------")
        print("at the end of ", ele, " count ", cnt)

        print("arcs_for_20", arcs_for_20)
        print("arcs_for_25", arcs_for_25)
        print("arcs_for_30", arcs_for_30)
        print("arcs_for_35", arcs_for_35)
        print("arcs_for_40", arcs_for_40)
        print("arcs_for_45", arcs_for_45)

        print("time_for_20", time_for_20)
        print("time_for_25", time_for_25)
        print("time_for_30", time_for_30)
        print("time_for_35", time_for_35)
        print("time_for_40", time_for_40)
        print("time_for_45", time_for_45)