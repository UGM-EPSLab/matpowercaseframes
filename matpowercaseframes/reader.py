# Copyright (c) 2020, Battelle Memorial Institute
# Copyright 2007 - 2022: numerous others credited in AUTHORS.rst
# Copyright 2022: https://github.com/yasirroni/

from __future__ import absolute_import, print_function

import re

from .utils import int_else_float_except_string


def find_name(string):
    return re.search("function\\s*mpc\\s*=\\s*(?P<data>.*?)\n", string).groupdict()[
        "data"
    ]


def find_attributes(string):
    pattern = "mpc\\.(?P<attribute>.*?)\\s*=\\s*"
    return re.findall(pattern, string, re.DOTALL)


def parse_file(attribute, string):
    match = search_file(attribute, string)

    if match is None:
        return None
    else:
        _list = []
        for line in match.splitlines():
            line = line.split("%")[0]
            line = line.replace(";", "")
            if line.strip():
                if attribute in ["version", "bus_name", "branch_name", "gen_name"]:
                    _list.append([line.strip().strip("'")])
                else:
                    _list.append(
                        [int_else_float_except_string(s) for s in line.strip().split()]
                    )
        return _list


def search_file(attribute, string):
    if attribute in ["bus_name", "branch_name", "gen_name"]:
        pattern = r"mpc\.{}\s*=\s*\{{[\n]?(?P<data>.*?)[\n]?\}};".format(attribute)
    elif attribute in ["version", "baseMVA"]:
        pattern = r"mpc\.{}\s*=\s*(?P<data>.*?);".format(attribute)
    else:
        # ["gen", "gencost", "bus", "branch", "dcline", "dclinecost"] or any keys
        pattern = r"mpc\.{}\s*=\s*\[[\n]?(?P<data>.*?)[\n]?\];".format(attribute)

    match = re.search(pattern, string, re.DOTALL)

    if match is None:
        return None
    else:
        match = match.groupdict().get("data", None)
        return match.strip("'").strip('"')
