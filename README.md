# MATPOWER Case Frames

Parse MATPOWER case into pandas DataFrame

## Usage

```python
import os

from matpowercaseframes.core import CaseFrames
from matpower import path_matpower

case_name = 'case9.m'

case_path = os.path.join(path_matpower, 'data', case_name)

cf = CaseFrames(case_path)

print(cf.gencost)
```

## Acknowledgement

This repository was supported by the [Faculty of Engineering, Universitas Gadjah Mada](https://ft.ugm.ac.id/en/) under the supervision of [Mr. Sarjiya](https://www.researchgate.net/profile/Sarjiya_Sarjiya). If you use this package for your research, we are very glad if you cite any relevant publication under Mr. Sarjiya's name as a thanks (but you are not responsible to). You can found his publications on the [semantic scholar](https://www.semanticscholar.org/author/Sarjiya/2267414) or [IEEE](https://ieeexplore.ieee.org/author/37548066400).
