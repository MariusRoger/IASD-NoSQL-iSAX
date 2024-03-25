from utils import *


def compute_isax_simple(T, w:int, n_bits:int, epsilon:float) -> iSAX_word:
    """
        Computes the iSAX representation of a time series T and S, parameterized by :
        - the length of the representation
        - a cardinality represented by their number of bits (second field of an iSAX symbol)
        - epsilon : threshold to limit normalization of noise
    """
    return compute_isax(T, w, [n_bits]*w, epsilon)

def compute_isax(T, w:int, n_bits_list:list[int], epsilon:float, existing_iSAX:iSAX_word = None) -> iSAX_word:
    """
        Computes the iSAX representation of a time series T and S, parameterized by :
        - a list of cardinalities represented by their number of bits (second field of an iSAX symbol)
        - epsilon : threshold to limit normalization of noise
        - a prior on the iSAX representation, when we just need to update some of the values
        if used, only dimensions with a n_bits in n_bits_list negative or different from existing_iSAX are recomputed 
    """
    assert len(n_bits_list) == w
    prev_iSAX_exists = existing_iSAX is not None
    if prev_iSAX_exists:
        assert len(existing_iSAX) == w
    
    if epsilon < 0:
        raise ValueError(f"epsilon {epsilon} must not be strictly negative.")
    
    T_len = T.shape[0]
    if T_len == 0:
        raise ValueError("T must not be empty.")
    
    T_normalized = rescale_normalize_ts(T, T_len, w, epsilon)
    blocks = array_split(T_normalized, w)

    if prev_iSAX_exists:
        new_iSAX = existing_iSAX.copy()
        for dim in range(w):
            if n_bits_list[dim] >= 1 and n_bits_list[dim] != existing_iSAX[dim][1]:
                new_iSAX[dim] = paa_to_isax(compute_paa(blocks[dim:dim+1]), n_bits_list[dim:dim+1])
    else:
        n_bits_list_check = list(map(lambda x: max(x,1), n_bits_list))
        new_iSAX = paa_to_isax(compute_paa(blocks), n_bits_list_check)

    return new_iSAX