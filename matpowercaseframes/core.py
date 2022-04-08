# Copyright (c) 2020, Battelle Memorial Institute
# Copyright 2007 - 2022: numerous others credited in AUTHORS.rst
# Copyright 2022: https://github.com/yasirroni/

import os

import pandas as pd
import numpy as np

from .reader import find_name, find_attributes, parse_file, search_file

from .constants import COLUMNS, ATTRIBUTES

class CaseFrames(object):
    def __init__(self, filename):
        self._read_matpower(filename)

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
                else:
                    cols = max([len(l) for l in _list])
                    columns = COLUMNS.get(attribute, [i for i in range(0, cols)])
                    columns = columns[:cols]
                    if cols > len(columns):
                        if attribute != "gencost":
                            msg = (f"Number of columns in {attribute} ({cols}) are greater than expected number.")
                            raise IndexError(msg)
                        columns = columns[:-1] + ["{}_{}".format(columns[-1], i) for i in range(cols - len(columns), -1, -1)]
                    df = pd.DataFrame(_list, columns=columns)

                    # TODO:
                    # Change to mpc.bus_name
                    # if attribute == "bus_name":
                    #     self.bus.index = df[0]

                    setattr(self, attribute, df)
                self._attributes.append(attribute)

        self.name = find_name(string)

        try:
            # TODO:
            # Check what is this
            self.gencost.loc[self.gencost["COST_2"] == 0, "NCOST"] = 2
        except:
            pass
