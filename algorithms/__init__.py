
from .search_uninformed import bfs_decide, dfs_decide
from .search_informed import greedy_decide, astar_decide
from .local_search import hill_climbing_decide, local_beam_search_decide
from .csp_search import backtracking_decide, forward_checking_decide
from .belief_search import sensorless_decide, and_or_decide
from .adversarial import minimax_decide, alpha_beta_decide

ALGORITHM_FUNCS = {
    "bfs": bfs_decide,
    "dfs": dfs_decide,
    "greedy": greedy_decide,
    "astar": astar_decide,
    "local_beam": local_beam_search_decide,
    "hill_climbing": hill_climbing_decide,
    "backtracking": backtracking_decide,
    "forward_checking": forward_checking_decide,
    "sensorless": sensorless_decide,
    "and_or": and_or_decide,
    "minimax": minimax_decide,
    "alpha_beta": alpha_beta_decide,
}

def get_decision_function(algo_key):
    return ALGORITHM_FUNCS.get(algo_key, ALGORITHM_FUNCS["astar"])
