from math import sqrt

from usual_values import return_breakpoints

def mindist_paa_isax(T_paa: list[int], S_isax: list[tuple[int,int]], n:int) -> float:
    if len(T_paa) != len(S_isax):
        raise ValueError("T_paa and S_isax must have the same length")
    
    accumulator = 0
    for T_i, S_i in zip(T_paa, S_isax):
        symbol, cardinality = S_i
        betas = return_breakpoints(cardinality)
        if 0 < symbol < cardinality-1:
            beta_l, beta_u = betas[symbol-1:symbol+1]
            # I decided to use the reverse paradigm compared to the paper :
            # lower symbol values for lower values
            
            d = max(beta_l - T_i, T_i - beta_u, 0)
            # the conditions from the paper are equivalent to strict negativity of these
        
        elif not symbol:
            beta_u = betas[symbol]
            d = max(T_i - beta_u, 0)
        
        else:
            beta_l = betas[symbol-1]
            d = max(beta_l - T_i, 0)

        accumulator += d*d
    return sqrt(accumulator * n / len(T_paa))