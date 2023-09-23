#!/usr/bin/env python3.7

# Copyright 2021, Gurobi Optimization, LLC

# Solve a traveling salesman problem on a randomly generated set of
# points using lazy constraints.   The base MIP model only includes
# 'degree-2' constraints, requiring each node to have exactly
# two incident edges.  Solutions to this model may contain subtours -
# tours that don't visit every city.  The lazy constraint callback
# adds new constraints to cut them off.

import sys
import math
import random
from itertools import combinations
import gurobipy as gp
from gurobipy import GRB, Model, quicksum
import obtained_x_coordinates as xco
import obtained_y_coordinates as yco
import distance_data as dist

from collections import defaultdict

# This class represents a directed graph using adjacency list representation


class Graph:
    def __init__(self):
        self.graph = defaultdict(list)  # default dictionary to store graph
        self.routes = []
    # function to add an edge to graph
    def addEdge(self, u, v):
        self.graph[u].append(v)
        print(self.graph)
    




def normalize_cost(cost_matrix):
    max_key = max(cost_matrix, key=cost_matrix.get)
    min_key = min(cost_matrix, key=cost_matrix.get)
    return_cost_matrix = dict()
    for i, j in A:
        normalized_value = (cost_matrix[i, j] - cost_matrix[min_key]) / \
            (cost_matrix[max_key] - cost_matrix[min_key])
        return_cost_matrix[i, j] = normalized_value
    return return_cost_matrix

# Callback - use lazy constraints to eliminate sub-tours


def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        # make a list of edges selected in the solution
        vals = model.cbGetSolution(model._vars)
        print(vals)
        selected = list(gp.tuplelist((i, j) for i, j in model._vars.keys()
                                     if vals[i, j] > 0))
        print("selected: ", selected)
        g = Graph()
        for ele in selected:
            print("adding edge ", ele, " to the class")
            g.addEdge(ele[0], ele[1])
        # find the shortest cycle in the selected edge list
        # tour = subtour(selected)

        # if len(tour) < n:
        #     print(tour)
        #     # add subtour elimination constr. for every pair of cities in tour
        #     model.cbLazy(gp.quicksum(model._vars[i, j]
        #                              for i, j in combinations(tour, 2))
        #                  <= len(tour)-1)


# Given a tuplelist of edges, find the shortest subtour

def subtour(edges):
    unvisited = list(range(n))
    cycle = range(n+1)  # initial length has 1 more city
    while unvisited:  # true if list is non-empty
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, '*')
                         if j in unvisited]
        if len(cycle) > len(thiscycle):
            cycle = thiscycle
    return cycle


# Parse argument
global n
n = int(10)
global N
N = [i for i in range(1, n+1)]
global V
V = [0] + N
global A
A = [(i, j) for i in V for j in V if i != j]
# Create n random points

random.seed(1)

x_coordinates = xco.x_values()
y_coordinates = yco.y_values()

# Dictionary of Euclidean distance between each pair of points

cost_matrix = dist.get_distance_data()
c = cost_matrix.copy()
cost_matrix = normalize_cost(c)

q = {(i): random.randint(5, 15) for i in range(1, n+1)}
Q = 70
demand_sum = 0
for i in N:
    demand_sum += q[i]
print(demand_sum)

vehicles_needed = math.ceil(demand_sum / Q)
print("vehicles_needed: ", vehicles_needed)
# Create variables
mdl = Model('CVRP')

x = mdl.addVars(A, vtype=GRB.BINARY)
mdl._vars = x
mdl.modelSense = GRB.MINIMIZE
mdl.setObjective(quicksum(x[i, j]*cost_matrix[i, j] for i, j in A))

mdl.addConstrs(quicksum(x[i, j] for j in V if j != i) == 1 for i in N)
mdl.addConstrs(quicksum(x[i, j] for i in V if i != j) == 1 for j in N)
mdl.addConstr(quicksum(x[0, j] for j in N) >= vehicles_needed)
for i, j in A:
    mdl.addConstr(x[i, j] >= 0)
for i, j in A:
    mdl.addConstr(x[i, j] <= 1)
mdl.addConstrs((x[i, j] == 1) >> ((x[j, i] == 0))
               for i, j in A)
# Optimize model
mdl.Params.lazyConstraints = 1
mdl.relax()
mdl.optimize(subtourelim)

# vals = mdl.getAttr('x', vars)

# selected = gp.tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)

# tour = subtour(selected)
# assert len(tour) == n

# print('')
# print('Optimal tour: %s' % str(tour))
# print('Optimal cost: %g' % m.objVal)
# print('')
