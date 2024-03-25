from math import sqrt, ceil
from numpy import array, array_split, zeros_like
from bisect import bisect_left

from usual_values import return_breakpoints_n_bits, n_bits_to_cardinality

#  type aliases
iSAX_symbol = tuple[int,int]
iSAX_word = list[iSAX_symbol]
PAA_word = list[float]

def normalize_ts(T, epsilon:float = 0):
    # I need to understand how to properly hint ndarray types
    """
        T : ndarray[float]
        epsilon : float

        return : ndarray[float]

        computes (T - mean) / std with a safeguard :
        if the std of T is too small, a zero array is returned
    """    
    T_std = T.std()
    if T_std <= epsilon:
        return zeros_like(T)

    return (T - T.mean())/T_std


def rescale_normalize_ts(T, T_len:int, w:int, epsilon:float):
    """
        Computes (T - mean) / std with safeguards :
        - if the length of T is smaller than w, a "time stretch" is performed
        - if the std of T is too small, a zero array is returned
    """
    if T_len < w:
        T_rescaled = T.repeat(ceil(w/T_len))
        # implicit time stretch of data for it to be longer than the iSAX word length
        return normalize_ts(T_rescaled, epsilon)
    else:
        return normalize_ts(T, epsilon)


def compute_paa(blocks:list) -> float:
    """Average each block in the list of blocks"""
    return [block.mean() for block in blocks]


def paa_to_isax(T_paa:PAA_word, n_bits_list:list[int]) -> iSAX_word:
    if len(T_paa) != len(n_bits_list):
        raise IndexError(f"Length of T_paa ({len(T_paa)}) must be equal to length of n_bits_list ({len(n_bits_list)}).")
    
    return [(bisect_left(return_breakpoints_n_bits(n_bits), T_i), n_bits) for T_i, n_bits in zip(T_paa, n_bits_list)]


def mindist_paa_isax(T_paa: PAA_word, S_isax: iSAX_word, n:int) -> float:
    """Compute the function mindist_paa_isax (see iSAX paper) between T_paa and S_isax"""
    if len(T_paa) != len(S_isax):
        raise IndexError(f"Length of T_paa ({len(T_paa)}) must be equal to length of S_isax ({len(S_isax)}).")
    
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
    """
        Promotes the smaller-cardinality i-th symbol to the cardinality of the other
        between iSAX representations T and S, according to the algorithm in the iSAX paper
    """
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
    """
        Promotes per-dimension the smaller-cardinality symbol to the cardinality of the corresponding symbol
        in the other iSAX representation, between T and S, according to the algorithm in the iSAX paper
    """
    if len(T) != len(S):
        raise ValueError(f"Length of T ({len(T)}) must be equal to length of S ({len(S)}).")
    
    n = len(T)
    T_out, S_out = [None]*n, [None]*n

    for index, T_i_S_i in enumerate(zip(T, S)):
        T_out[index], S_out[index] = promote_repr_symbol(*T_i_S_i)    
    return (T_out, S_out)


def downgrade_repr_word_to_one(T:iSAX_word) -> iSAX_word:
    """
        Downgrades per-dimension the high-cardinality symbols to cardinality 1.
        This is useful for lazy creation of the root nodes.
    """
    return [(letter[0] >> (letter[1] - 1), 1) for letter in T]


def increase_dim_split_isax(T:iSAX_word, split_dim:int, child:int):
    S = T.copy()
    S[split_dim] = ((T[split_dim][0] << 1)+child, T[split_dim][1]+1)
    return S


def isax_to_string(T:iSAX_word) -> str:
    return '_'.join([f'{symbol}.{card}' for symbol, card in T])

def string_to_isax(s:str) -> iSAX_word:
    return [tuple(int(x) for x in T_i.split('.')) for T_i in s.split('_')]


def compute_binary_possible_vectors(n:int) -> list[list[bool]]:
    return [[ (i % (2 << power)) >= (1 << power) for power in range(n)] for i in range(1 << n)]