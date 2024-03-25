import os
import json
import csv
import numpy as np

from utils import string_to_isax, iSAX_word
from nodes import split_node, is_over_max, compute_child_node_find, insert_ts_node,\
    is_max_card, find_root_node

def save_index(index_dict:dict, json_path:str) -> None:
    with open(json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(index_dict, jsonfile, ensure_ascii=False, indent=4)


def read_ts_line(ts_line:list, skip_columns=0):
    return np.array(list(map(float, ts_line[skip_columns:])))


def read_indexed_ts_line(idx_ts_line:list):
    return string_to_isax(idx_ts_line[0])

def write_indexed_ts_line(idx_ts_line:list, tsvwriter) -> None:
    tsvwriter.writerow(idx_ts_line)


def get_root_node(idx_isax:str, roots:list, root_dir:str):
    root_node, existing = find_root_node(idx_isax, roots)

    if not existing:
        os.mkdir(os.path.join(root_dir, root_node['name']))
    return root_node


# if there are more than the max number of TS, then :
def split_leaf(node:dict, node_path:str, max_per_file:int, max_n_bits:int) -> None:
    if is_max_card(node, max_n_bits):
        print(f"Warning : node {node['name']} is at maximum cardinality. It will not be split further.")
        # I will replace this in due time with a proper warning object
        return
    previous_data_path = os.path.join(node_path, 'leaf.tsv')

    split_node(node)
    child0, child1 = node['children']
    child0_path = os.path.join(node_path, child0['name'])
    child1_path = os.path.join(node_path, child1['name'])

    child0_data_path = os.path.join(child0_path, 'leaf.tsv')
    child1_data_path = os.path.join(child1_path, 'leaf.tsv')

    with open(previous_data_path, 'r', encoding='utf-8') as tsvfile_read:
        tsvreader = csv.reader(tsvfile_read, delimiter="\t")

        with open(child0_data_path, 'w', encoding='utf-8') as tsvfile_write0:
            tsvwriter0 = csv.writer(tsvfile_write0, delimiter="\t")

            with open(child1_data_path, 'w', encoding='utf-8') as tsvfile_write1:
                tsvwriter1 = csv.writer(tsvfile_write1, delimiter="\t")

                for idx_ts_line in tsvreader:
                    T = read_indexed_ts_line(idx_ts_line)

                    if compute_child_node_find(T, node):
                        write_indexed_ts_line(idx_ts_line, tsvwriter1)
                        insert_ts_node(child1)
                    else:
                        write_indexed_ts_line(idx_ts_line, tsvwriter0)
                        insert_ts_node(child0)

    os.remove(previous_data_path)
    
    if is_over_max(child0, max_per_file):
        split_leaf(child0, child0_path, max_per_file, max_n_bits)
    if is_over_max(child1, max_per_file):
        split_leaf(child1, child1_path, max_per_file, max_n_bits)


def insert_ts_leaf(ts_line:list, idx_isax:str, node:dict, node_path:str, max_per_file:int, max_n_bits:int) -> None:
    data_path = os.path.join(node_path, 'leaf.tsv')
    insert_ts_node(node)

    with open(data_path, 'a', encoding='utf-8') as tsvfile:
            tsvwriter = csv.writer(tsvfile, delimiter="\t")
            tsvwriter.writerow([idx_isax], ts_line)
    
    if is_over_max(node, max_per_file):
        split_leaf(node, node_path, max_per_file, max_n_bits)


def query_ts_leaf():
    pass