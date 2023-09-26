# MATPOWER Case Frames

Parse MATPOWER case into pandas DataFrame.

Unlike the [tutorial](https://github.com/yasirroni/matpower-pip#extra-require-oct2py-or-matlabengine) on [`matpower-pip`](https://github.com/yasirroni/matpower-pip), this package supports parsing MATPOWER case using `re` instead of `Oct2Py` and Octave. After that, you can further parse the data into any format supported by your solver.

## Installation

```plaintext
pip install matpowercaseframes
```

## Usage

The main utility of `matpowercaseframes` is to help read `matpower` data in user-friendly format as follows,

```python
from matpowercaseframes import CaseFrames

case_path = 'case9.m'
cf = CaseFrames(case_path)

print(cf.gencost)
```

If you have `matpower` installed via `pip install matpower` (did not require `matpower[octave]`), you can easily navigate `matpower` case using:

```python
import os
from matpower import path_matpower # require `pip install matpower`
from matpowercaseframes import CaseFrames

case_name = 'case9.m'
case_path = os.path.join(path_matpower, 'data', case_name)
cf = CaseFrames(case_path)

print(cf.gencost)
```

Furthermore, `matpowercaseframes` also support generating data that is acceptable by `matpower` via `matpower-pip` package (require `matlab` or `octave`),

```python
from matpowercaseframes import CaseFrames

case_path = 'case9.m'
cf = CaseFrames(case_path)
mpc = cf.to_dict()

m = start_instance()
m.runpf(mpc)
```

To save all `DataFrame` to a single `xlsx` file, use:

```python
from matpowercaseframes import CaseFrames

case_path = 'case9.m'
cf = CaseFrames(case_path)

cf.to_excel('PATH/TO/DIR/case9.xlsx')
```

If you use `matpower[octave]`, `CaseFrames` also support `oct2py.io.Struct` as input using:

```python
from matpower import start_instance
from matpowercaseframes import CaseFrames

m = start_instance()

# support mpc before runpf
mpc = m.loadcase('case9', verbose=False)
cf = CaseFrames(mpc)
print(cf.gencost)

# support mpc after runpf
mpc = m.runpf(mpc, verbose=False)
cf = CaseFrames(mpc)
print(cf.gencost)

m.exit()
```

## Acknowledgment

This repository was supported by the [Faculty of Engineering, Universitas Gadjah Mada](https://ft.ugm.ac.id/en/) under the supervision of [Mr. Sarjiya](https://www.researchgate.net/profile/Sarjiya_Sarjiya). If you use this package for your research, we are very glad if you cite any relevant publication under Mr. Sarjiya's name as thanks (but you are not responsible to cite). You can find his publications in the [semantic](https://www.semanticscholar.org/author/Sarjiya/2267414) scholar](https://www.semanticscholar.org/author/Sarjiya/2267414) or [IEEE](https://ieeexplore.ieee.org/author/37548066400).

This package is a fork and simplification from [psst](https://github.com/ames-market/psst) MATPOWER parser, thus we greatly thank psst developers and contributors.
