import argparse
import os
import csv
import sys
from shutil import rmtree as shutil_rmtree
import json

from utils import downgrade_repr_word_to_one
from file_ops import save_index, read_ts_line, get_root_node, insert_ts_leaf
import nodes
from compute_repr import compute_isax_simple

parser = argparse.ArgumentParser()
parser.add_argument("--ts-file", type=str, default=None,
                    help="File in which the time series to index are located.")
parser.add_argument('-w',  type=int, default=None,
                    help="Length of the iSAX word representation.")
parser.add_argument('--n-bits',  type=int, default=None,
                    help="Maximum number of bits for the dimension cardinality."\
                         "Must be between 1 and 8 included.")
parser.add_argument("--index-location", type=str, default="index",
                    help="File in which the index is located.")
parser.add_argument('--overwrite', action="store_true",
                    help="Erases a previously built index at the specified location before building.")
parser.add_argument("--max-per-file", type=int, default=50,
                    help="Maximum number of time series per file in the index.")
parser.add_argument("--save-every", type=int, default=20,
                    help="Interval between two saves of the time series and index.json to the disk.")
parser.add_argument("--skip-columns", type=int, default=None,
                    help="Number of columns to be skipped before the time series.")
parser.add_argument("--epsilon", type=float, default=None,
                    help="Epsilon threshold under which the time series is not normalized.")

args = parser.parse_args()

'''
maybe I could add a save mechanism to start again from the place we stopped

but it would probably slow down the system, and I won't have time to add this now
'''


if args.ts_file is None:
    sys.exit()

w = args.w
if w is not None:
    if w <= 0: raise ValueError(f"w ({w}) must be strictly positive.")

n_bits = args.n_bits
if n_bits is not None:
    if not (0 < n_bits <= 8): raise ValueError(f"n_bits ({n_bits}) must be between 1 and 8 included.")

skip_columns = args.skip_columns
if skip_columns is not None:
    if skip_columns < 0: raise ValueError(f"skip_columns ({skip_columns}) must be positive.")

epsilon = args.epsilon
if epsilon is not None:
    if epsilon < 0: raise ValueError(f"epsilon ({epsilon}) must be positive.")

os.makedirs(args.index_location, exist_ok=True)

root_dir = os.path.join(args.index_location, "root")
json_path = os.path.join(args.index_location, "index.json")

if args.overwrite:
    if os.path.exists(root_dir):
        shutil_rmtree(root_dir)
    if os.path.exists(json_path):
        os.remove(json_path)

# fetching/creating the index dictionary
if os.path.exists(json_path):
    with open(json_path, 'r', encoding='utf-8') as jsonfile:
        index_dict = json.load(jsonfile)
    
    if w is not None:
        if index_dict["w"] != w:
            raise ValueError(f"Parameter w ({w}) does not match index w ({index_dict["w"]}). Please change w or overwrite the index.")
    else:
        w = index_dict["w"]
    
    if n_bits is not None:
        if index_dict["n_bits"] != n_bits:
            raise ValueError(f"Parameter n_bits ({n_bits}) does not match index n_bits ({index_dict["n_bits"]}). Please change n_bits or overwrite the index.")
    else:
        n_bits = index_dict["n_bits"]
        
    if skip_columns is not None:
        if index_dict["skip_columns"] != skip_columns:
            raise ValueError(f"Parameter skip_columns ({skip_columns}) does not match index n_bits ({index_dict["skip_columns"]}). Please change skip_columns or overwrite the index.")
    else:
        skip_columns = index_dict["skip_columns"]

    if epsilon is not None:
        if index_dict["epsilon"] != epsilon:
            raise ValueError(f"Parameter epsilon ({epsilon}) does not match index epsilon ({index_dict["epsilon"]}). Please change epsilon or overwrite the index.")
    else:
        epsilon = index_dict["epsilon"]
        
else:
    if w is None:
        raise ValueError(f"Parameter w must be set when initializing a new index.")
    if n_bits is None:
        raise ValueError(f"Parameter n_bits must be set when initializing a new index.")
    if skip_columns is None:
        raise ValueError(f"Parameter skip_columns must be set when initializing a new index.")
    if epsilon is None:
        raise ValueError(f"Parameter epsilon must be set when initializing a new index.")
    
    index_dict = nodes.init_node(w, n_bits, skip_columns, epsilon)
    save_index(index_dict, json_path)


# I would like to implement bulk loading avery 20 steps or so, but I will probably not have time.

with open(args.ts_file, 'r') as tsvfile:
    tsvreader = csv.reader(tsvfile, delimiter="\t")


    for ts_line in tsvreader:
        time_series = read_ts_line(ts_line, skip_columns)

        isax_repr = compute_isax_simple(time_series, w, n_bits, epsilon)

        isax_downgraded = downgrade_repr_word_to_one(isax_repr)

        root_node = get_root_node(isax_downgraded, index_dict['roots'], root_dir)

        node, node_path = nodes.find_leaf_node(isax_repr, root_node)

        insert_ts_leaf(ts_line, isax_repr, node, node_path=os.path.join(root_dir, node_path),
                       max_per_file=args.max_per_file, max_n_bits=n_bits)

        # things

        save_index(index_dict, json_path)