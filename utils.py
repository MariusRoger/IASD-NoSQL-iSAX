from math import sqrt

from usual_values import return_breakpoints_n_bits, n_bits_to_cardinality

#  type aliases
iSAX_symbol = tuple[int,int]
iSAX_word = list[iSAX_symbol]
PAA_word = list[float]

def mindist_paa_isax(T_paa: PAA_word, S_isax: iSAX_word, n:int) -> float:
    if len(T_paa) != len(S_isax):
        raise ValueError("T_paa and S_isax must have the same length")
    
    accumulator = 0
    for T_i, S_i in zip(T_paa, S_isax):
        symbol, n_bits = S_i
        betas = return_breakpoints_n_bits(n_bits)
        if 0 < symbol < n_bits_to_cardinality(n_bits)-1:
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


def promote_repr_symbol(T_i:iSAX_symbol, S_i:iSAX_symbol) -> tuple[iSAX_symbol, iSAX_symbol]:
    if T_i[1] > S_i[1]:
        a_symbol, a_card = T_i
        b_symbol, b_card = S_i
    elif S_i[1] > T_i[1]:
        a_symbol, a_card = S_i
        b_symbol, b_card = T_i
    else:
        return T_i, S_i
    
    A = (a_symbol, a_card)
    diff_card = a_card - b_card
    prefix = a_symbol >> diff_card

    if b_symbol == prefix:
        return (A, A)
    elif b_symbol < prefix:
        B = (((b_symbol +1) << diff_card) - 1, a_card)
        # bit shift and add ones at the end    
    else:
        B = (b_symbol << diff_card, a_card)

    return (A, B) if T_i[1] > S_i[1] else (B,A)


def promote_repr_word(T:iSAX_word, S:iSAX_word) -> tuple[iSAX_word, iSAX_word]:
    if len(T) != len(S):
        raise ValueError("T and S must have the same length")
    
    n = len(T)
    T_out, S_out = [None]*n, [None]*n

    for index, T_i_S_i in enumerate(zip(T, S)):
        T_out[index], S_out[index] = promote_repr_symbol(*T_i_S_i)    
    return (T_out, S_out)