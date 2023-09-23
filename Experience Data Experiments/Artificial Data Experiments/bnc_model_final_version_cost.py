
import networkx as nx
import gurobipy
import random
import math
import numpy as np
import matplotlib.pyplot as plt
from gurobipy import Model, GRB, quicksum
from branching import Branch
import csv
import time
import gc
import support_20 as sup

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

def get_route_cost(route):

    total_cost = 0
    for indnum in range(len(route)-1):
        total_cost += c[route[indnum],route[indnum+1]]
    return total_cost

def two_opt(route):
    
    best = route
    improved = True
    while improved:
        improved = False
        for i in range(1, len(route)-2):
            for j in range(i+1, len(route)):
                if j-i == 1: 
                    continue
                new_route = route[:]
                new_route[i:j] = route[j-1:i-1:-1]
                if get_route_cost(new_route) < get_route_cost(best):  
                        best = new_route
                        improved = True
        route = best
    return best

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

def route_identificator(routes):
    a = routes
    sifirsizlar = [b for b in a]

    print("routes_before: ",sifirsizlar)

    sifirlilar = []
    for i in a:
        if i[0]== 0:
            sifirlilar.append(i)

    for i in sifirlilar:
        if i in sifirsizlar:
            sifirsizlar.remove(i)

    routes = []     
    for ele in sifirlilar:
        route = []
        route.append(ele)
        while True:
            found = 0
            item_to_search = route[len(route)-1][1]
            for i in sifirsizlar:
                if i[0] == item_to_search:
                    route.append(i)
                    found = 1
                    to_remove = i
            if found == 0:
                break
            else:
                sifirsizlar.remove(to_remove)    
        routes.append(route)
    subroutes = []
    if sifirsizlar:
        while True:
            subroute = []
            item_to_start = random.choice(sifirsizlar)
            subroute.append(item_to_start)
            sifirsizlar.remove(item_to_start)
            cust_to_finish = item_to_start[0]
            while True:
                found = 0
                item_to_search = subroute[len(subroute)-1][1]
                for i in sifirsizlar:
                    if i[0] == item_to_search:
                        subroute.append(i)
                        found = 1
                        to_remove = i
                if found == 0:
                    break
                else:
                    sifirsizlar.remove(to_remove)    
            subroutes.append(subroute)
            if len(sifirsizlar) == 0:
                break

def get_multistar_cuts(solution,cutpool):

    vals = solution.copy()
    temp_active_arcs = [a for a in A if vals[a] > 0]
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
                if cut_candidate not in cutpool:
                    print("added the multistar cut of: ",cut_candidate)
                    cutpool.append(cut_candidate)
            countnum += 1
    return cutpool

def get_capcuts(solution, cutpool):
    
    vals = solution.copy()
    temp_active_arcs = [a for a in A if vals[a] > 0]
    for times in range(len(N) - 5):
        ele_num = random.randint(times+3,len(N))
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
            cutpool.append(cut_candidate)
    return cutpool


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

def subtourelim(model,solution,cutpool):
    
    
    set_pool = []
    vals = solution.copy()

    temp_active_arcs = [a for a in A if vals[a] > 0]
    returnval = True
    subroutes = somethingnew(temp_active_arcs)

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
                        return cutpool
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
                    if cut_candidate in cutpool:
                        print(cut_candidate," is in the cut pool so its not added. Current cut pool:")
                    else:
                        print(cut_candidate, " is added to the cutpool")
                        cutpool.append(cut_candidate)
                        returnval = False
                        continue       
    return cutpool,returnval    

def main():

    rnd = np.random
    rnd.seed(0)
    demands = []
    vehicle_capacity = 80
    
    rnd = np.random
    rnd.seed(0)
    
    global n
    n = 45
    global N
    N = [i for i in range(1, n+1)]
    print(N)
    global V
    V = [0] + N
    print(V)
    x_coordinates = rnd.rand(len(V))*200
    y_coordinates = rnd.rand(len(V))*100
    global xc
    xc = x_coordinates
    global yc
    yc = y_coordinates
    rnd.seed(random.randint(1,50))
    demand_dict = {(i):random.randint(5,15) for i in range(1,n+1)}
        
    global algo_start
    algo_start = time.time()
    global A
    A = [(i, j) for i in V for j in V if i != j]
    global U
    U = [(i, j) for i in N for j in V if i != j]
    print("demands: " , demand_dict)

    print("vehicle_capacity: ",vehicle_capacity)
    print("x_coordinates: ", x_coordinates)
    print("y_coordinates: ", y_coordinates)
    print("vehicle_capacity: ", vehicle_capacity)
    print(A)
    global c
    c = {(i, j): np.hypot(xc[i]-xc[j], yc[i]-yc[j]) for i, j in A}
    cost_matrix = normalize_cost(c)
    print(c)
    global support
    support = sup.get_support()
    for i in range(len(N) +1):
        support[i,i] = 0.000000000001
    for i,j in A:
        if support[i,j] == 0:
            support[i,j] = 0.000000000001

    support_matrix = support.copy()
    global Q
    Q = vehicle_capacity
    global q
    q = demand_dict
    q[0]=0
    global cut_list
    cut_list = []
    global time_data
    time_data = []

    
    demand_sum = 0

    for i in N:
        demand_sum += q[i]
    print(demand_sum)

    vehicles_needed = math.ceil(demand_sum / Q)

    print(vehicles_needed)
    number_of_vehicles = vehicles_needed
    print('Q: ',Q)  
    global mdl
    mdl = Model('CVRP')
    global x
    x = mdl.addVars(A, vtype=GRB.CONTINUOUS)
    
    global allcuts
    global allcapcuts
    global eniyi
    mdl.modelSense = GRB.MINIMIZE
    mdl.setObjective(quicksum(x[i, j]*cost_matrix[i, j] for i, j in A))

    mdl.addConstrs(quicksum(x[i, j] for j in V if j != i) == 1 for i in N)
    mdl.addConstrs(quicksum(x[i, j] for i in V if i != j) == 1 for j in N)
    mdl.addConstr(quicksum(x[0,j] for j in N) == vehicles_needed)
    
    for i,j in A:
        mdl.addConstr(x[i,j] >= 0)
    for i,j in A:
        mdl.addConstr(x[i,j] <= 1)
    
    global orj_cntrs_count
    orj_cntrs_count = len(N) + len(N) + 1 + len(A) + len(A)

    mdl._vars = x

    mdl.Params.MIPGap = 0.000000000001
    mdl.Params.TimeLimit = 1000
    mdl.Params.cutPasses = 2000000
    mdl.relax()
    mdl.update()
    mdl._obj = None
    mdl._bd = None
    mdl._data = []
    mdl._start = time.time()
    mdl.optimize()
    strnode = Branch(cost_matrix=cost_matrix,support_matrix=support_matrix,parent=None,customer_list=N,all_vertexes=V,edge_list=A,vehicle_capacity=vehicle_capacity,demand_dict=demand_dict,branchvals=list(),cutpool=list(),vehicles_needed=number_of_vehicles,model=mdl,orjcnum=orj_cntrs_count,x=x,parentsol=0,glmcutpool=list(),capcuts=list())
    strnode.solution = {a: x[a].x for a in A}
    #print("strnode.solution: ",strnode.solution)
    best_sol , best_sol_value = BnBDFS(strnode,0.1)
    algo_end = time.time()
    algo_duration = algo_end - algo_start
    print("algorithm took " , algo_duration, " seconds!")
    print(best_sol)
    
    active_arcs = [a for a in A if best_sol[a] > 0.99]
    
    plt.rcParams["figure.figsize"] = (60,40)
    for i, j in active_arcs:
        plt.plot([xc[i], xc[j]], [yc[i], yc[j]], c='g', zorder=0)
    for i in N:
        plt.annotate('$q_%d=%d$' % (i, q[i]), (xc[i]+1, yc[i]),fontsize = 8)
    plt.plot(xc[0], yc[0], c='r', marker='s')
    plt.scatter(xc[1:], yc[1:], c='b')

    plt.show()


def BnBDFS(starting_node,MIPGap):
    allcuts = list()
    allglmcuts = list()
    allcapcuts = list()
    mdl_upper_bound = 1000000000000000000000000000
    mdl_lower_bound = 0
    best_known_solution = []
    eniyi = dict()
    best_known_solution_value = 0
    stack = [starting_node]
    loop_counter = 0
    degismeme = 0
    found_int_count = 0
    cutlist,rota_olurlu = subtourelim(starting_node.model,starting_node.solution,[])
    for y in cutlist:
        if y not in allcuts:
            allcuts.append(y)

    starting_node.cutpool = allcuts
    starting_node.glmcutpool = allglmcuts
    starting_node.capcuts = allcapcuts
    while len(stack) > 0:

        print("---------------------time_data: ",time_data)
        branch_instance = stack.pop()
        print("len_stack: ",len(stack))
        print(branch_instance.branchvals)
        print("explored: ",branch_instance.explored,"fathomed: ",branch_instance.fathomed)
        if branch_instance.explored == False and branch_instance.fathomed == False:
            print("-------------------------------------ilk if e girdim---------------------------------------------")
            for cut in allcuts:
                if cut not in branch_instance.cutpool:
                    print("found that cut ", cut, "is not in the cutpool so added!")
                    branch_instance.cutpool.append(cut)
            for cut in allcapcuts:
                if cut not in branch_instance.capcuts:
                    print("found that cut ", cut, "is not in the cutpool so added!")
                    branch_instance.capcuts.append(cut)
            solution_vars , solution_value = branch_instance.solve_new_branch()
            print("-------------solution vars------------------",solution_vars)
            if branch_instance.check_for_infeasible_or_onbounded():
                print("-------------------------------------ikinci if e girdim---------------------------------------------")
                if loop_counter > 0:
                    cutlist = [ele for ele in branch_instance.cutpool]
                    glmcuts = [ele for ele in branch_instance.glmcutpool]
                    capcuts = [ele for ele in branch_instance.capcuts]
                    for ele in cutlist:
                        if ele not in allcuts:
                            allcuts.append(ele)
                    for ele in capcuts:
                        if ele not in allcapcuts:
                            allcapcuts.append(ele)
                    cuts_updated,rota_olurlu = subtourelim(branch_instance.model,branch_instance.solution,cutlist)
                    for y in cuts_updated:
                        if y not in allcuts:
                            allcuts.append(y)
                    added_multistar_cuts = get_multistar_cuts(branch_instance.solution,glmcuts)
                    for cut in added_multistar_cuts:
                        if cut not in allglmcuts:
                            allglmcuts.append(cut)
                    added_capcuts = get_capcuts(branch_instance.solution,capcuts)
                    for cut in added_capcuts:
                        if cut not in allcapcuts:
                            allcapcuts.append(cut)
                    branch_instance.cutpool = allcuts
                    branch_instance.glmcutpool = allglmcuts
                    branch_instance.capcuts = allcapcuts
                print(solution_value,mdl_upper_bound)
                print(best_known_solution)
                if branch_instance.check_for_integrality() and solution_value > mdl_upper_bound:
                    print("integral but higher than upper bound")
                    branch_instance.fathomed = True
                    branch_instance.model = None
                    branch_instance.cutpool = []
                    branch_instance.capcuts = []
                    gc.collect()
                    continue
                if branch_instance.check_for_integrality() and solution_value < mdl_upper_bound:
                    best_known_solution = solution_vars
                    best_known_solution_value = solution_value
                    branch_instance.model = None
                    branch_instance.cutpool = []
                    branch_instance.capcuts = []
                    branch_instance.fathomed = True
                    if rota_olurlu:
                        mdl_upper_bound = solution_value
                        eniyi = solution_vars
                        print("eniyi",eniyi)
                        timestamp = [mdl_upper_bound,(time.time() - algo_start)]
                        time_data.append(timestamp)
                        degismeme = 0
                        found_int_count += 1
                        figname = 'Cost_comparison_n0%d.png' % n
                        figname.format(found_int_count)
                        stack = [l for l in stack if l.parentsol <= mdl_upper_bound]
                        active_arcs = [a for a in A if eniyi[a] > 0.99]
                        plt.rcParams["figure.figsize"] = (60,40)
                        for i, j in active_arcs:
                            plt.plot([xc[i], xc[j]], [yc[i], yc[j]], c='g', zorder=0)
                        for i in N:
                            plt.annotate('$q_%d=%d$' % (i, q[i]), (xc[i]+1, yc[i]),fontsize = 8)
                        plt.plot(xc[0], yc[0], c='r', marker='s')
                        plt.scatter(xc[1:], yc[1:], c='b')
                        plt.savefig(figname)
                        plt.clf()
                    print("integral and lower than upper bound")
                    continue
                if not branch_instance.check_for_integrality() and solution_value > mdl_upper_bound:
                    print("not integral but higher than upper bound")
                    branch_instance.fathomed = True
                    branch_instance.model = None
                    branch_instance.cutpool = []
                    branch_instance.capcuts = []
                    gc.collect()
                    continue
                if not branch_instance.check_for_integrality() and not branch_instance.fathomed and solution_value <= mdl_upper_bound:
                    branch_instance.find_branching_variable(sense="cost")
                    print("------------branching var: ",branch_instance.branching_variable)
                    child1_first = True
                    if child1_first:
                        branch_instance.branch_to_child2()
                        stack.append(branch_instance.child2) 
                        print("child2 brvals: ",branch_instance.child2.branchvals)  
                        branch_instance.branch_to_child1()
                        stack.append(branch_instance.child1) 
                        print("child1 brvals: ",branch_instance.child1.branchvals)  
                    else:
                        branch_instance.branch_to_child1()
                        stack.append(branch_instance.child1) 
                        print("child1 brvals: ",branch_instance.child1.branchvals)  
                        branch_instance.branch_to_child2()
                        stack.append(branch_instance.child2) 
                        print("child2 brvals: ",branch_instance.child2.branchvals)  
            else:
                branch_instance.fathomed = True
            branch_instance.explored = True
        loop_counter += 1
        degismeme += 1
        if eniyi:
            print("eniyi: ",eniyi)
        if loop_counter > 10000000:
            break
        if ( mdl_upper_bound - mdl_lower_bound ) / mdl_upper_bound < MIPGap:
            break
    return best_known_solution,best_known_solution_value

    
if __name__ == "__main__":
    main()