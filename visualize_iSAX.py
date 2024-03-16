import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import argparse

import utils
from usual_values import return_breakpoints_n_bits

parser = argparse.ArgumentParser()
parser.add_argument("--ts-file", type=str, default=None,
                    help="File in which the time series you want to visualize is located."\
                        "If no file is provided, a random smoothed time series is generated.")
parser.add_argument('-w',  type=int, default=10,
                    help="Length of the iSAX word representation.")
parser.add_argument('--n-bits-fixed', type=int, default=2,
                    help="Fixed number of bits used to represent iSAX individual symbols (like SAX).")

parser.add_argument('--n-bits-file',type=str, default=None,
                    help="File in which the list of per-symbol number of bits is located."\
                        "The list will be truncated or padded to length w."\
                        "If set, has precedence over --n-bits-fixed.")

args = parser.parse_args()

if args.ts_file is None:
    length = 128
    a = np.random.randn(length)
    time_series = a + np.roll(a,1) + np.roll(a,2) + np.roll(a,3) + np.roll(a,4)
    # add temporal coherence
else:
    raise NotImplementedError #open csv or other format
    # length = len(time_series)

w = args.w

ts_normalized = utils.rescale_normalize_ts(time_series, length, w, 0)

ts_blocks = np.array_split(ts_normalized, w)
ts_paa = utils.compute_paa(ts_blocks)

if args.n_bits_file is None:
    n_bits_list = [args.n_bits_fixed]*w
else:
    raise NotImplementedError

ts_isax = utils.paa_to_isax(ts_paa, n_bits_list)

fig, ax = plt.subplots()

ax.plot(np.linspace(0,w,length),ts_normalized, label="Normalized and time-stretched time series")
ax.plot(np.arange(w).repeat(2)+np.arange(2*w)%2,np.repeat(ts_paa,2), label="PAA values")

for i, dim in enumerate(ts_isax):
    symbol, n_bits = dim
    bp = return_breakpoints_n_bits(n_bits)
    if 0 < symbol < utils.n_bits_to_cardinality(n_bits)-1:
        beta_l, beta_u = bp[symbol-1:symbol+1]
    elif not symbol:
        beta_l, beta_u = ax.get_ylim()[0], bp[symbol]
    else:
        beta_l, beta_u = bp[symbol-1], ax.get_ylim()[1]
    ax.add_patch(Rectangle((i,beta_l),1, beta_u - beta_l, alpha=0.1))

plt.xlabel("iSAX word dimension")
plt.ylabel("Value")
plt.title(f"iSAX representation (blue rectangles) of length {w} of a time series")
plt.legend()
plt.show()