# MATPOWER Case Frames

Parse MATPOWER case into pandas DataFrame.

Unlike the [tutorial](https://github.com/yasirroni/matpower-pip#extra-require-oct2py-or-matlabengine) on [`matpower-pip`](https://github.com/yasirroni/matpower-pip), this package support parsing MATPOWER case using `re` instead of `Oct2Py` and Octave. After that, you can further parse the data into any format supported by you solver.

## Installation

```plaintext
pip install matpowercaseframes
```

## Usage

```python
from matpowercaseframes import CaseFrames

case_path = 'case9.m'
cf = CaseFrames(case_path)

print(cf.gencost)
```

If you have `matpower` installed via `pip install matpower` (did not require `matpower[octave]`), you can easily navigate MATPOWER case using:

```python
import os
from matpower import path_matpower # require `pip install matpower`
from matpowercaseframes import CaseFrames

case_name = 'case9.m'
case_path = os.path.join(path_matpower, 'data', case_name)
cf = CaseFrames(case_path)

print(cf.gencost)
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

## Acknowledgement

This repository was supported by the [Faculty of Engineering, Universitas Gadjah Mada](https://ft.ugm.ac.id/en/) under the supervision of [Mr. Sarjiya](https://www.researchgate.net/profile/Sarjiya_Sarjiya). If you use this package for your research, we are very glad if you cite any relevant publication under Mr. Sarjiya's name as a thanks (but you are not responsible to). You can found his publications on the [semantic scholar](https://www.semanticscholar.org/author/Sarjiya/2267414) or [IEEE](https://ieeexplore.ieee.org/author/37548066400).

This package is a a fork and simplification from [psst](https://github.com/ames-market/psst) MATPOWER parser, thus we greatly thanks psst developers and contributors.
