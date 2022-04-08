# Copyright (c) 2020, Battelle Memorial Institute
# Copyright 2007 - 2022: numerous others credited in AUTHORS.rst
# Copyright 2022: https://github.com/yasirroni/

import os

import pandas as pd
import numpy as np

from .reader import find_name, find_attributes, parse_file, search_file

from .constants import COLUMNS, ATTRIBUTES

class CaseFrames(object):
    def __init__(self, filename, update_index=True):
        self._read_matpower(filename)
        if update_index:
            self._update_index()

    def _read_matpower(self, filename):
        self._attributes = list()
        self.filename = filename

        with open(filename) as f:
            string = f.read()

        for attribute in find_attributes(string):
            if attribute not in ATTRIBUTES:
                #? Should we support custom attributes?
                continue
            
            _list = parse_file(attribute, string)
            if _list is not None:
                if attribute == "version" or attribute == "baseMVA":
                    setattr(self, attribute, _list[0][0])
                elif attribute in ['bus_name', 'branch_name', 'gen_name']:
                    idx = pd.Index(_list)
                    setattr(self, attribute, idx)
                else:
                    cols = max([len(l) for l in _list])
                    columns = COLUMNS.get(attribute, [i for i in range(0, cols)])
                    columns = columns[:cols]
                    if cols > len(columns):
                        if attribute != "gencost":
                            msg = (f"Number of columns in {attribute} ({cols}) are greater than expected number.")
                            raise IndexError(msg)
                        columns = columns[:-1] + ["{}_{}".format(columns[-1], i) for i in range(cols - len(columns), -1, -1)]
                    else:
                        df = pd.DataFrame(_list, columns=columns)

                    setattr(self, attribute, df)
                self._attributes.append(attribute)

        self.name = find_name(string)

        try:
            # TODO:
            # Check what is this
            self.gencost.loc[self.gencost["COST_2"] == 0, "NCOST"] = 2
        except:
            pass

    def _update_index(self):
        if 'bus_name' in self._attributes:
            self.bus.set_index(self.bus_name, drop=False, inplace=True)
        else:
            self.bus.set_index(pd.RangeIndex(1,len(self.bus.index)+1,1), drop=False, inplace=True)

        if 'branch_name' in self._attributes:
            self.branch.set_index(self.branch_name, drop=False, inplace=True)
        else:
            self.branch.set_index(pd.RangeIndex(1,len(self.branch.index)+1,1), drop=False, inplace=True)
        
        if 'gen_name' in self._attributes:
            self.gen.set_index(self.gen_name, drop=False, inplace=True)
        else:
            self.gen.set_index(pd.RangeIndex(1,len(self.gen.index)+1,1), drop=False, inplace=True)
