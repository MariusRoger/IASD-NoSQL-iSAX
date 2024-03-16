# IASD-NoSQL-iSAX
Reimplementation of the iSAX method for the IASD NoSQL course's final project


The `visualize_iSAX.py` function plots an iSAX representation of a time series.  
Its parameters are :
- `--ts-file` (text string)  
The file in which the time series you want to visualize is located.  
If no file is provided, a random smoothed time series is generated.  
*This functionality has not been implemented yet.*

- `-w` (integer, default=10)  
The length of the iSAX word representation.

- `--n-bits-fixed` (integer, default=2)  
A fixed number of bits used to represent all iSAX individual symbols (like SAX).  
The cardinality is $2^{n\_bits}$.

- `--n-bits-file` (text string)  
The file in which the list of per-symbol number of bits is located.  
The list will be truncated or padded to length w.  
If set, has priority over `--n-bits-fixed`.  
*This functionality has not been implemented yet.*