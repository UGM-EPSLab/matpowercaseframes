# Copyright (c) 2020, Battelle Memorial Institute
# Copyright 2007 - 2022: numerous others credited in AUTHORS.rst
# Copyright 2022: https://github.com/yasirroni/

import os

import pandas as pd
import numpy as np

from .reader import find_name, find_attributes, parse_file, search_file

from .constants import COLUMNS, ATTRIBUTES

from .descriptors import (
    Name,
    Version,
    BaseMVA,
    BusName,
    Bus,
    BusString,
    Branch,
    BranchName,
    Gen,
    GenName,
    GenCost,
    GenFuel,
    Load,
    Period,
    _Attributes,
)

class CaseFrames(object):
    name = Name()
    version = Version()
    baseMVA = BaseMVA()

    bus = Bus()
    branch = Branch()
    gen = Gen()
    gencost = GenCost()

    bus_name = BusName()
    branch_name = BranchName()
    gen_name = GenName()

    _attributes = _Attributes()

    def __init__(self, filename):
        self._read_matpower(filename)

    def _read_matpower(self, filename):
        self._attributes = list()
        self.filename = filename

        with open(filename) as f:
            string = f.read()

        for attribute in find_attributes(string):
            _list = parse_file(attribute, string)
            if _list is not None:
                if len(_list) == 1 and (attribute == "version" or attribute == "baseMVA"):
                    setattr(self, attribute, _list[0][0])
                else:
                    cols = max([len(l) for l in _list])
                    columns = COLUMNS.get(attribute, [i for i in range(0, cols)])
                    columns = columns[:cols]
                    if cols > len(columns):
                        if attribute != "gencost":
                            logger.warning("Number of columns greater than expected number.")
                        columns = columns[:-1] + ["{}_{}".format(columns[-1], i) for i in range(cols - len(columns), -1, -1)]
                    df = pd.DataFrame(_list, columns=columns)

                    if attribute == "bus":
                        df.set_index("BUS_I", inplace=True)
                    if attribute == "bus_name":
                        attribute = "bus_string"

                    if attribute == "bus_name":
                        self.bus.index = df[0]

                    setattr(self, attribute, df)
                self._attributes.append(attribute)

        self.name = find_name(string)

        try:
            # TODO:
            # Check what is this
            self.gencost.loc[self.gencost["COST_2"] == 0, "NCOST"] = 2
        except:
            pass
