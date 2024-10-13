# MATPOWER Case Frames

[![PyPI version](https://badge.fury.io/py/matpowercaseframes.svg)](https://pypi.org/project/matpowercaseframes/)

Parse MATPOWER case into pandas DataFrame.

Unlike the [tutorial](https://github.com/yasirroni/matpower-pip#extra-require-oct2py-or-matlabengine) on [`matpower-pip`](https://github.com/yasirroni/matpower-pip), this package supports parsing MATPOWER case using `re` instead of `Oct2Py` and Octave. After that, you can further parse the data into any format supported by your solver.

## Installation

```plaintext
pip install matpowercaseframes
```

## Usage

### Read MATPOWER case by parsing file as string

The main utility of `matpowercaseframes` is to help read `matpower` data in user-friendly format as follows,

```python
from matpowercaseframes import CaseFrames

case_path = 'case9.m'
cf = CaseFrames(case_path)

print(cf.gencost)
```

If you have `matpower` installed via `pip install matpower` (did not requires `matpower[octave]`), you can easily navigate `matpower` case using:

```python
import os
from matpower import path_matpower # require `pip install matpower`
from matpowercaseframes import CaseFrames

case_name = 'case9.m'
case_path = os.path.join(path_matpower, 'data', case_name)
cf = CaseFrames(case_path)

print(cf.gencost)
```

### Read MATPOWER case by running `loadcase`

In some cases, a case file may contain `matlab` code at the end of the file that needs to be executed. An example of such case is `case69.m`. To properly load this type of file, use the method recommended by `matpower`, which is using `loadcase` instead of parsing. To do this, use the `load_case_engine` parameter (requires `matlab` or `octave`), as demonstrated here:

```python
from matpower import start_instance
from matpowercaseframes import CaseFrames

m = start_instance()

case_name = f"case69.m"
cf_lc = CaseFrames(case_name, load_case_engine=m)
cf_lc.branch  # see that the branch is already in p.u., converted by `loadcase`
```

### Convert `oct2py.io.Struct` to `CaseFrames`

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

### Convert `CaseFrames` to `mpc`

Furthermore, `matpowercaseframes` also support generating data that is acceptable by `matpower` via `matpower-pip` package (requires `matlab` or `octave`),

```python
from matpowercaseframes import CaseFrames

case_path = 'case9.m'
cf = CaseFrames(case_path)
mpc = cf.to_mpc()  # identical with cf.to_dict()

m = start_instance()
m.runpf(mpc)
```

### Add custom data

Sometimes, we want to expand `matpower` data containing custom field. For example, given an `mpc.load` as a `dict`, we can attach it to `CaseFrames` using,

```python
from matpower import start_instance
from matpowercaseframes import CaseFrames

m = start_instance()

LOAD_COL = ["LD_ID", "LD_BUS", "LD_STATUS", "LD_PD", "LD_QD"]

mpc = m.loadcase('case9', verbose=False)
cf = CaseFrames(mpc)
cf.setattr_as_df('load', mpc.load, columns_template=LOAD_COL)
```

If data already in `DataFrame`, we can use `setattr` directly as follows,

```python
from matpower import start_instance
from matpowercaseframes import CaseFrames

m = start_instance()

mpc = m.loadcase('case9', verbose=False)
cf = CaseFrames(mpc)
cf.setattr('load', df_load)
```

### Export as `xlsx`

To save all `DataFrame` to a single `xlsx` file, use:

```python
from matpowercaseframes import CaseFrames

case_path = 'case9.m'
cf = CaseFrames(case_path)

cf.to_excel('PATH/TO/DIR/case9.xlsx')
```

## Acknowledgment

1. This repository was supported by the [Faculty of Engineering, Universitas Gadjah Mada](https://ft.ugm.ac.id/en/) under the supervision of [Mr. Sarjiya](https://www.researchgate.net/profile/Sarjiya_Sarjiya). If you use this package for your research, we would be very glad if you cited any relevant publication under Mr. Sarjiya's name as thanks (but you are not responsible for citing). You can find his publications in the [Semantic Scholar](https://www.semanticscholar.org/author/Sarjiya/2267414) or [IEEE](https://ieeexplore.ieee.org/author/37548066400).

1. This repository is working flawlessly with [matpower-pip](https://github.com/yasirroni/matpower-pip). If you use matpower-pip, make sure to cite using the below citation:

    > M. Yasirroni, Sarjiya, and L. M. Putranto, "matpower-pip: A Python Package for Easy Access to MATPOWER Power System Simulation Package," [Online]. Available: <https://github.com/yasirroni/matpower-pip>.
    >
    > M. Yasirroni, Sarjiya, and L. M. Putranto, "matpower-pip". Zenodo, Jun. 13, 2024. doi: 10.5281/zenodo.11626845.

    ```bib
    @misc{matpower-pip,
      author       = {Yasirroni, M. and Sarjiya and Putranto, L. M.},
      title        = {matpower-pip: A Python Package for Easy Access to MATPOWER Power System Simulation Package},
      year         = {2023},
      howpublished = {\url{https://github.com/yasirroni/matpower-pip}},
    }

    @software{yasirroni_2024_11626845,
      author       = {Yasirroni, Muhammad and
                        Sarjiya, Sarjiya and
                        Putranto, Lesnanto Multa},
      title        = {matpower-pip},
      month        = jun,
      year         = 2024,
      publisher    = {Zenodo},
      version      = {8.0.0.2.1.8},
      doi          = {10.5281/zenodo.11626845},
      url          = {\url{https://doi.org/10.5281/zenodo.11626845}},
    }
    ```

1. This package is a fork and simplification from [psst](https://github.com/ames-market/psst) MATPOWER parser, thus we greatly thank psst developers and contributors.
