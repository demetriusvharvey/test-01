"""Pre-registered prospective paired testing helpers; no inference from absent data."""
import random


def bh_adjust(p_values):
    """Benjamini–Hochberg adjusted p-values in original order, including missing."""
    valid=[(i,float(p)) for i,p in enumerate(p_values) if p is not None and 0<=p<=1]
    ordered=sorted(valid,key=lambda item:item[1]);result=[None]*len(p_values);n=len(ordered);previous=1.0
    for rank in range(n,0,-1):
        index,p=ordered[rank-1];previous=min(previous,p*n/rank);result[index]=min(1.0,previous)
    return result

def paired_block_test(day_differences,seed=20261028,iterations=10000):
    """Two-sided day-block sign permutation of model minus market log loss."""
    groups=[values for values in day_differences.values() if values]
    n=sum(len(g) for g in groups)
    if n<30 or len(groups)<10:return None
    sums=[sum(g) for g in groups];observed=sum(sums)/n;rng=random.Random(seed);extreme=0
    for _ in range(iterations):
        value=sum(total*(1 if rng.randrange(2) else -1) for total in sums)/n
        if abs(value)>=abs(observed)-1e-15:extreme+=1
    return {'games':n,'game_days':len(groups),'mean_difference':observed,
            'p_value':(extreme+1)/(iterations+1),'iterations':iterations,'seed':seed}
