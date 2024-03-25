import os
from utils import iSAX_word, increase_dim_split_isax, isax_to_string

def init_node(w:int, n_bits:int, skip_columns:int, epsilon:float) -> dict:
    return {'w':w, 'n_bits':n_bits, 'skip_columns':skip_columns, 'epsilon':epsilon, 'roots':[]}

def create_node(T:iSAX_word, split_dim=0) -> dict:
    return {'name':isax_to_string(T), 'word':T, 'split':split_dim, 'children':[], 'count':0}

def insert_ts_node(node:dict) -> None:
    node['count'] += 1

def is_over_max(node:dict, max_per_file:int) -> bool:
    return node['count'] > max_per_file

def is_max_card(node:dict, max_n_bits:int) -> bool:
    return node['word'][node['split']][1] >= max_n_bits

def split_node(node:dict) -> None:
    T = node['word']
    split_dim = node['split']
    node['children'] = [create_node(increase_dim_split_isax(T, split_dim, child), split_dim+1) for child in [0,1]]
    node['count'] = 0

def find_root_node(T:iSAX_word, roots:list) -> dict:
    name = isax_to_string(T)
    for root_node in roots:
        if root_node['name'] == name: return (root_node, True)
    new_root = create_node(T)
    roots.append(new_root)
    return (new_root, False)

def find_leaf_node(T:iSAX_word, node:dict) -> tuple[dict,str]:
    if not node['children']: return node, node['name']
    else:
        child = compute_child_node_find(T, node)
        leaf_node, leaf_path = find_leaf_node(T, node['children'][child])
        return leaf_node, os.path.join(node['name'], leaf_path)

def compute_child_node_find(T:iSAX_word, node:dict) -> bool:
    split_dim = node['split']
    symbol, n_bits = T[split_dim]
    return (symbol >> (n_bits - node['word'][split_dim][1])) % 2 == 1