from csv import reader
from numpy import array, arange

# CDF_file = 'normal_CDF_original.csv'
# the original data, from https://en.wikipedia.org/wiki/Standard_normal_table#Cumulative_(less_than_Z)

CDF_file = 'normal_CDF_interpolated.csv'
# the data interpolated by average between 2 consecutive, to increase max cardinality from 250 to 500
# since the largest step between consecutive precomputed values was 0.00399 and 1/0.00399 = 250

normal_CDF = None

with open(CDF_file) as csvfile:
    csvreader = reader(csvfile)
    for row in csvreader:
        normal_CDF = array([float(i) for i in row])

assert normal_CDF is not None

breakpoints = dict()

def compute_breakpoints(cardinality:int) -> None:
    if cardinality > 500 or cardinality <= 1:
        raise ValueError(f"cardinality ({cardinality}) is not between 2 and 500 included")

    indices = array(normal_CDF.searchsorted(arange(1, cardinality) / cardinality))
    # computing the "indices" of the beta_1 to beta_{cardinality-1} from the paper
    # there are cardinality regions so we need cardinality-1 breakpoints
     
    breakpoints[cardinality] = (-4.09 + indices* 8.18/(len(normal_CDF)-1) ).tolist()
    # scaling, since the wikipedia CDF of the normal distribution goes from -4.09 to 0

def return_breakpoints(cardinality:int) -> list[int]:
    if cardinality not in breakpoints:
        compute_breakpoints(cardinality)
    return breakpoints[cardinality]

# in practice we will only use cardinalities powers of 2 for easy bit-shifting
def n_bits_to_cardinality(n_bits:int) -> int:
    return 1 << n_bits
    # the power of 2 is 1 less than the number of bits

def return_breakpoints_n_bits(n_bits:int) -> list[int]:
    return return_breakpoints(n_bits_to_cardinality(n_bits))