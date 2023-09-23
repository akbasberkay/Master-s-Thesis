from gurobipy import Model, GRB, quicksum
import gurobipy
import gc

class Branch:
    def __init__(self,cost_matrix,support_matrix,parent,customer_list,all_vertexes,edge_list,vehicle_capacity,demand_dict,branchvals,cutpool,vehicles_needed,model,orjcnum,x,parentsol,glmcutpool,capcuts):
        self.cost_matrix = cost_matrix
        self.support_matrix = support_matrix
        self.parent = parent
        self.customer_list = customer_list
        self.all_vertexes = all_vertexes
        self.edge_list = edge_list
        self.vehicle_capacity = vehicle_capacity
        self.demand_dict = demand_dict
        self.branchvals = branchvals
        self.cutpool = cutpool
        self.vehicles_needed = vehicles_needed
        self.model = model   
        self.orjcnum = orjcnum
        self.x = x
        self.parentsol = parentsol
        self.glmcutpool = glmcutpool
        self.capcuts = capcuts
        self.child1 = None
        self.child2 = None
        self.solution = None
        self.branching_variable = None
        self.fathomed = False
        self.solution_value = 0
        self.explored = False
        self.infeasible_model = False

    def solve_new_branch(self):

        for cut in self.cutpool:

            self.model.addConstr(gurobipy.quicksum(self.x[i,j] for i,j in cut[0]) >= cut[1])
        self.model.update()
        for cut in self.glmcutpool:
            self.model.addConstr(gurobipy.quicksum(self.x[i,j] * k for i,j,k in cut[0]) + gurobipy.quicksum(self.x[i,j] * k for i,j,k in cut[1]) <= cut[2])
        print("branchvals to be removed: ",self.branchvals)
        for val in self.branchvals:
            self.model.addConstr(self.x[val[0]] == val[1])
        for cut in self.capcuts:
            self.model.addConstr(gurobipy.quicksum(self.x[i,j] for i,j in cut[0]) <= cut[1])
        self.model.update()
        self.model.write("model_today.lp")
        self.model.write("model_today.mps")
        self.model.optimize()
        if self.model.STATUS != 2:
            self.infeasible_model = True
        
        try:
            self.solution = {(key,value): self.x[key,value].X for key,value in self.x}
        except:
            self.fathomed= True
            self.solution_value = 100000000000000000
            self.infeasible_model= True 
            self.cutpool = []  
            self.capcuts = []
            gc.collect()

        try:
            self.solution_value = self.model.objVal
        except:
            self.fathomed= True
            self.solution_value = 100000000000000000    
            self.infeasible_model = True
            self.cutpool = []
            self.capcuts = []
            gc.collect()     
        
        self.model.remove(self.model.getConstrs()[self.orjcnum - 1:])
        self.model.update()
               
        return self.solution,self.solution_value
    
    def check_for_infeasible_or_onbounded(self):

        if self.infeasible_model:
            return False
        return True
    
    def find_branching_variable(self,sense):
        returnval = []
        if sense == 'cost':
            print('find_least_cost')
            cost_copy = dict()
            for ele in self.edge_list:
                if self.solution[ele] != 0 and self.solution[ele] != 1:
                    cost_copy[ele] = self.cost_matrix[ele]
            max_key = min(cost_copy, key=cost_copy.get)
            self.branching_variable = max_key
        elif sense == 'support':

            support_copy = dict()

            for ele in self.edge_list:
                if self.solution[ele] != 0 and self.solution[ele] != 1:
                    support_copy[ele] = self.support_matrix[ele]
            max_key = min(support_copy, key=support_copy.get)
            self.branching_variable = max_key
        elif sense == 'cost-support':
            mixed_copy = dict()
            for ele in self.edge_list:
                if self.solution[ele] != 0 and self.solution[ele] != 1:
                    print(ele)
                    mixed_copy[ele] = self.support_matrix[ele]
            print(mixed_copy)
            some_other_dict = {(key,value): self.cost_matrix[key,value] + (1 / mixed_copy[key,value]) for key,value in mixed_copy}
            min_key = min(some_other_dict, key=some_other_dict.get)
            self.branching_variable = min_key

    def check_for_integrality(self):
        print("---------------------check for integrality--------------------------")
        for (key1,key2),value in self.solution.items():

            if value != int(value):
                print("check for integrality false")
                return False
        print("check for integrality true")
        return True
        
    def find_reduced_costs(self):
        reduced_costs = self.model.getAttr(GRB.Attr.RC)
        return reduced_costs
        
    def find_non_integer_variables(self):
        non_integer_vars = []
        for key,value in self.solution:
            if value != 0 and value != 1:
                non_integer_vars.append(key)
        return non_integer_vars
    
    def choosewhich(self):
        if  self.solution[self.branching_variable] >= 1 - self.solution[self.branching_variable]:
            return True
        else:
            return False
        
        return True
    
    def branch_to_child1(self):
        branchval_to_append = [self.branching_variable,1]
        print("self_branchvals: ",self.branchvals)
        print(self.branching_variable)
        print(branchval_to_append)
        some_branchvals = [item for item in self.branchvals]
        some_branchvals.append(branchval_to_append)
        print("some_branch_vals: ",some_branchvals)
        some_upper_bound = 300
        self.child1 = Branch(self.cost_matrix,self.support_matrix,self,self.customer_list,self.all_vertexes,self.edge_list,self.vehicle_capacity,self.demand_dict,some_branchvals,self.cutpool,self.vehicles_needed,self.model,self.orjcnum,self.x,self.solution_value,self.glmcutpool,self.capcuts)
        return True
        
    def branch_to_child2(self):
        branchval_to_append = [self.branching_variable,0]
        print("self_branchvals: ",self.branchvals)
        print(self.branching_variable)
        print(branchval_to_append)
        some_branchvals = [item for item in self.branchvals]
        some_branchvals.append(branchval_to_append)
        print("some_branch_vals: ",some_branchvals)
        some_upper_bound = 300
        self.child2 = Branch(self.cost_matrix,self.support_matrix,self,self.customer_list,self.all_vertexes,self.edge_list,self.vehicle_capacity,self.demand_dict,some_branchvals,self.cutpool,self.vehicles_needed,self.model,self.orjcnum,self.x,self.solution_value,self.glmcutpool,self.capcuts)
        return True