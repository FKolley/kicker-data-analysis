#! /usr/bin/python
# cython: profile=True

import numpy as np
cimport numpy as np

def football_sim( float p1, float p2, float dt=1., int N=1000000, float re=0.15, float avg_goal_norm=0.04 ):
    '''
    stochstic football simulation.
    p1: average goals per game home team
    p2: average goals per game guest team
    dt: time step
    N: sample size
    re: risk enhencement, increases the probability for a goal
    if the score differs by one. decreases risk if score is equal.
    '''

    cdef int steps = int(90/dt) # number of time steps
    p1 = (p1+avg_goal_norm)/steps # probability of home goal per time step
    p2 = (p2+avg_goal_norm)/steps # probability of guest goal per time step

    cdef np.ndarray r = np.random.ranf( N * steps )
    results = {}
    goals = []

    cdef int home, guest
    cdef float p1_r, p2_r
    cdef int i, t
    
    for i in range( N ):
        home = 0
        guest = 0
        for t in range( steps ):
            p1_r = p1
            p2_r = p2
            if abs(home-guest) == 1:
                p1_r = p1 + re/steps
                p2_r = p2 + re/steps
            elif abs(home-guest) == 0:
                p1_r = p1 - re/steps
                p2_r = p2 - re/steps
            if r[i*steps+t] < p1_r:
                home = home + 1
            elif r[i*steps+t] < p1_r+p2_r:
                guest = guest + 1
        res = (home, guest)
        if res in results.keys():
            results[res] = results[res] + 1
        else:
            results[res] = 1
        goals.append( home+guest )

    # normalize results
    for res in results.keys():
        results[res] = float(results[res]) / N

    return results, goals
