# Copyright (c) 2020, Battelle Memorial Institute
# Copyright 2007 - 2022: numerous others credited in AUTHORS.rst
# Copyright 2022: https://github.com/yasirroni/

import os

import pandas as pd

from .constants import ATTRIBUTES, COLUMNS
from .reader import find_attributes, find_name, parse_file

try:
    import matpower
    MATPOWER_EXIST = True
except ImportError:
    MATPOWER_EXIST = False


class CaseFrames:
    def __init__(self, data, update_index=True):
        """Convert data into CaseFrames format

        Args:
            data (str|dict):
                str of path | str of matpower case name | dict | oct2py.io.Struct
            update_index (bool, optional):
                Update index numbering if True. Defaults to True.

        Raises:
            TypeError: Error input data invalid.
        """
        if isinstance(data, str):
            # TYPE: str of path | str of matpower case name
            if not os.path.isfile(data):
                # TYPE: str of matpower case name
                if MATPOWER_EXIST:
                    data = os.path.join(matpower.path_matpower, f"data/{data}")
            self._read_matpower(filepath=data)
        elif isinstance(data, dict):
            # TYPE: dict | oct2py.io.Struct
            self._read_struct(struct=data)
        else:
            message = "Source must be str path to .m file or oct2py.io.Struct or dict."
            raise TypeError(message)

        if update_index:
            self._update_index()

    def _read_struct(self, struct):
        self.name = ''

        self._attributes = []
        for attribute, list_ in struct.items():
            if attribute not in ATTRIBUTES:
                # ? Should we support custom attributes?
                continue

            if attribute == "version" or attribute == "baseMVA":
                setattr(self, attribute, list_)
            elif attribute in ['bus_name', 'branch_name', 'gen_name']:
                idx = pd.Index(list_, name=attribute)
                setattr(self, attribute, idx)
            else:
                cols = list_.shape[1]
                # NOTE: .get('key') instead of ['key'] to default range
                columns = COLUMNS.get(attribute, [i for i in range(0, cols)])
                columns = columns[:cols]
                if cols > len(columns):
                    if attribute != "gencost":
                        msg = (f"Number of columns in {attribute} ({cols}) are"
                               f"greater than expected number.")
                        raise IndexError(msg)
                    columns = (columns[:-1]
                               + ["{}_{}".format(columns[-1], i)
                                  for i in range(cols - len(columns), -1, -1)])
                df = pd.DataFrame(list_, columns=columns)
                setattr(self, attribute, df)

            self._attributes.append(attribute)

        return None

    def _read_matpower(self, filepath):
        # ! Old ttribute is not guaranted to be replaced in re-read
        with open(filepath) as f:
            string = f.read()

        self.name = find_name(string)

        self._attributes = []
        for attribute in find_attributes(string):
            if attribute not in ATTRIBUTES:
                # ? Should we support custom attributes?
                continue

            # TODO: migrate using GridCal approach
            list_ = parse_file(attribute, string)
            if list_ is not None:
                if attribute == "version" or attribute == "baseMVA":
                    setattr(self, attribute, list_[0][0])
                elif attribute in ['bus_name', 'branch_name', 'gen_name']:
                    idx = pd.Index([name[0] for name in list_], name=attribute)
                    setattr(self, attribute, idx)
                else:
                    cols = max([len(l) for l in list_])
                    # NOTE: .get('key') instead of ['key'] to default range
                    columns = COLUMNS.get(attribute, [i for i in range(0, cols)])
                    columns = columns[:cols]
                    if cols > len(columns):
                        if attribute != "gencost":
                            msg = (f"Number of columns in {attribute} ({cols}) are"
                                   f"greater than expected number.")
                            raise IndexError(msg)
                        columns = (columns[:-1]
                                   + ["{}_{}".format(columns[-1], i)
                                      for i in range(cols - len(columns), -1, -1)])
                    df = pd.DataFrame(list_, columns=columns)

                    setattr(self, attribute, df)
                self._attributes.append(attribute)

    def _update_index(self):
        if 'bus_name' in self._attributes:
            self.bus.set_index(self.bus_name, drop=False, inplace=True)
        else:
            self.bus.set_index(pd.RangeIndex(1, len(self.bus.index) + 1),
                               drop=False, inplace=True)

        if 'branch_name' in self._attributes:
            self.branch.set_index(self.branch_name, drop=False, inplace=True)
        else:
            self.branch.set_index(pd.RangeIndex(1, len(self.branch.index) + 1),
                                  drop=False, inplace=True)

        if 'gen_name' in self._attributes:
            self.gen.set_index(self.gen_name, drop=False, inplace=True)
            try:
                self.gencost.set_index(self.gen_name, drop=False, inplace=True)
            except AttributeError:
                pass
        else:
            self.gen.set_index(pd.RangeIndex(1, len(self.gen.index) + 1),
                               drop=False, inplace=True)
            try:
                self.gencost.set_index(pd.RangeIndex(1, len(self.gen.index) + 1),
                                   drop=False, inplace=True)
            except AttributeError:
                pass


    def to_excel(self, path):
        with pd.ExcelWriter(path) as writer:
            pd.DataFrame(                
                data={
                    'INFO': {
                        'version': getattr(self, 'version'),
                        'baseMVA': getattr(self, 'baseMVA'),
                    }
                }
            ).to_excel(writer, sheet_name='info')
            for attribute in self._attributes:
                if attribute == "version" or attribute == "baseMVA":
                    # TODO: make self._attributes_non_pandas?
                    continue
                elif attribute in ['bus_name', 'branch_name', 'gen_name']:
                    pd.DataFrame(data={
                        attribute: getattr(self, attribute)
                    }).to_excel(writer, sheet_name=attribute)
                else:
                    getattr(self, attribute).to_excel(writer,
                                                      sheet_name=attribute)
