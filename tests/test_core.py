import os

import numpy as np
import pandas as pd
import pytest

from matpowercaseframes import CaseFrames
from matpowercaseframes.idx import BUS_I, BUS_TYPE

"""
    pytest -n auto -rA --lf -c pyproject.toml --cov-report term-missing --cov=matpowercaseframes tests/
"""

CASE_NAME_CASE9 = "case9.m"
CURDIR = os.path.realpath(os.path.dirname(__file__))
CASE_DIR = os.path.join(os.path.dirname(CURDIR), "data")
CASE_PATH_CASE9 = os.path.join(CASE_DIR, CASE_NAME_CASE9)
ATTRIBUTES_CASE9 = ["version", "baseMVA", "bus", "gen", "branch", "gencost"]

CASE_NAME_CASE118 = "case118.m"
CURDIR = os.path.realpath(os.path.dirname(__file__))
CASE_DIR = os.path.join(os.path.dirname(CURDIR), "data")
CASE_PATH_CASE118 = os.path.join(CASE_DIR, CASE_NAME_CASE118)
ATTRIBUTES_CASE118 = [
    "version",
    "baseMVA",
    "bus",
    "gen",
    "branch",
    "gencost",
    "bus_name",
]
ATTRIBUTES_CASE = {
    "case9": ATTRIBUTES_CASE9,
    "case118": ATTRIBUTES_CASE118,
}


def test_input_str_path():
    CaseFrames(CASE_PATH_CASE9)


def test_input_oct2py_io_Struct():
    from matpower import start_instance

    m = start_instance()

    # before run
    mpc = m.loadcase(CASE_NAME_CASE9, verbose=False)

    # after run
    mpc = m.runpf(mpc, verbose=False)
    _ = CaseFrames(mpc)

    m.exit()


def test_input_oct2py_io_Struct_and_parse_are_identical():
    from matpower import start_instance

    m = start_instance()

    # before run
    mpc = m.loadcase(CASE_NAME_CASE9, verbose=False)
    cf_mpc = CaseFrames(mpc)  # _read_oct2py_struct
    cf_parse = CaseFrames(CASE_NAME_CASE9)  # _read_matpower

    # convert to data type recognizable by numpy from pd.convert_dtypes()
    cf_mpc.infer_numpy()
    cf_parse.infer_numpy()
    for attribute in cf_mpc.attributes:
        df_mpc = getattr(cf_mpc, attribute)
        df_parse = getattr(cf_parse, attribute)

        if isinstance(df_mpc, pd.DataFrame):
            assert df_mpc.columns.equals(df_parse.columns)
            assert df_mpc.equals(df_parse)
        else:
            assert df_mpc == df_parse

    # after run
    mpc = m.runpf(mpc, verbose=False)
    _ = CaseFrames(mpc)

    m.exit()


def test_input_type_error():
    with pytest.raises(TypeError):
        CaseFrames(1)


def test_read_value():
    cf = CaseFrames(CASE_PATH_CASE9)

    assert cf.version == "2"
    assert cf.baseMVA == 100

    narr_gencost = np.array(
        [
            [2.000e00, 1.500e03, 0.000e00, 3.000e00, 1.100e-01, 5.000e00, 1.500e02],
            [2.000e00, 2.000e03, 0.000e00, 3.000e00, 8.500e-02, 1.200e00, 6.000e02],
            [2.000e00, 3.000e03, 0.000e00, 3.000e00, 1.225e-01, 1.000e00, 3.350e02],
        ]
    )
    assert np.allclose(cf.gencost, narr_gencost)

    narr_bus = np.array(
        [
            [1, 3, 0, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [2, 2, 0, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [3, 2, 0, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [4, 1, 0, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [5, 1, 90, 30, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [6, 1, 0, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [7, 1, 100, 35, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [8, 1, 0, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
            [9, 1, 125, 50, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        ]
    )
    assert np.allclose(cf.bus, narr_bus)
    assert np.allclose(cf.bus["BUS_I"], narr_bus[:, BUS_I])
    assert np.allclose(cf.bus["BUS_TYPE"], narr_bus[:, BUS_TYPE])

    # TODO:
    # Check all data


def test_read_case_name():
    cf = CaseFrames(CASE_PATH_CASE9)
    assert cf.name == "case9"


def test_get_attributes():
    cf = CaseFrames(CASE_PATH_CASE9)
    assert cf.attributes == ["version", "baseMVA", "bus", "gen", "branch", "gencost"]

    with pytest.raises(AttributeError):
        cf.attributes = ["try", "replacing", "attributes"]

    # TODO: protect from attributes changed by user
    # cf.attributes[0] = 'try'
    # print(cf.attributes[0])
    # print(cf.attributes)


# !WARNING: Refactor to fixture to read file is proven to be slower
#   pytest -n auto --durations=0


@pytest.mark.parametrize(
    "case_path,attributes,output_path,prefix,suffix",
    [
        (
            CASE_PATH_CASE9,
            ATTRIBUTES_CASE9,
            "tests/results/case9/case9_test_to_xlsx.xlsx",
            "",
            "",
        ),
        (
            CASE_PATH_CASE9,
            ATTRIBUTES_CASE9,
            "tests/results/case9_prefix_suffix/case9_test_to_xlsx_prefix_suffix.xlsx",
            "mpc.",
            "_test",
        ),
        (
            CASE_PATH_CASE118,
            ATTRIBUTES_CASE118,
            "tests/results/case118/case118_test_to_xlsx.xlsx",
            "",
            "",
        ),
        (
            CASE_PATH_CASE118,
            ATTRIBUTES_CASE118,
            "tests/results/case118_prefix_suffix/case118_test_to_xlsx_prefix_suffix.xlsx",
            "mpc.",
            "_test",
        ),
    ],
    ids=["case9", "case9_prefix_suffix", "case118", "case118_prefix_suffix"],
)
def test_to_and_read_xlsx(case_path, attributes, output_path, prefix, suffix):
    cf = CaseFrames(case_path)  # read .m file
    cf.to_excel(output_path, prefix=prefix, suffix=suffix)  # write to .xlsx file
    cf = CaseFrames(
        output_path, prefix=prefix, suffix=suffix
    )  # read back from .xlsx file
    for attribute in attributes:
        assert attribute in cf.attributes, (
            f"Missing attribute '{attribute}' in {cf.attributes}"
        )


@pytest.mark.parametrize(
    "case_path,attributes,output_dir,prefix,suffix",
    [
        (CASE_PATH_CASE9, ATTRIBUTES_CASE9, "tests/results/case9", "", ""),
        (
            CASE_PATH_CASE9,
            ATTRIBUTES_CASE9,
            "tests/results/case9_prefix_suffix",
            "mpc.",
            "_test",
        ),
        (CASE_PATH_CASE118, ATTRIBUTES_CASE118, "tests/results/case118", "", ""),
        (
            CASE_PATH_CASE118,
            ATTRIBUTES_CASE118,
            "tests/results/case118_prefix_suffix",
            "mpc.",
            "_test",
        ),
    ],
    ids=["case9", "case9_prefix_suffix", "case118", "case118_prefix_suffix"],
)
def test_to_and_read_csv(case_path, attributes, output_dir, prefix, suffix):
    cf = CaseFrames(case_path)  # read .m file
    cf.to_csv(output_dir, prefix=prefix, suffix=suffix)  # write to .csv directory
    cf = CaseFrames(
        output_dir, prefix=prefix, suffix=suffix
    )  # read back from .csv directory
    for attribute in attributes:
        assert attribute in cf.attributes, (
            f"Missing attribute '{attribute}' in {cf.attributes}"
        )


@pytest.mark.parametrize(
    "case_path,schema_dir,case_name",
    [
        (CASE_PATH_CASE9, "tests/results/case9/schema", "case9"),
        (CASE_PATH_CASE118, "tests/results/case118/schema", "case118"),
    ],
    ids=["case9", "case118"],
)
def test_to_schema(case_path, schema_dir, case_name):
    cf = CaseFrames(case_path)
    cf.to_schema(schema_dir)
    assert os.path.isdir(schema_dir), f"Schema directory '{schema_dir}' was not created"

    schema_files = os.listdir(schema_dir)
    assert len(schema_files) > 0, f"No schema files found in '{schema_dir}'"

    cf = CaseFrames(schema_dir)
    for attribute in ATTRIBUTES_CASE[case_name]:
        assert attribute in cf.attributes, (
            f"Missing attribute '{attribute}' in {cf.attributes}"
        )


def test_to_dict():
    cf = CaseFrames(CASE_PATH_CASE9)
    cf.to_dict()


def test_to_mpc():
    cf = CaseFrames(CASE_PATH_CASE9)
    cf.to_mpc()


def test_reset_index_and_infer_numpy_case9():
    cf = CaseFrames(CASE_PATH_CASE9)
    cf.infer_numpy()

    # original bus IDs are 1-based in MATPOWER
    assert cf.bus["BUS_I"].iloc[0] == 1
    assert cf.branch["F_BUS"].min() >= 1
    assert cf.gen["GEN_BUS"].min() >= 1

    # apply renumbering
    cf.reset_index()

    # after reset, BUS_I must be contiguous 0..n-1
    assert np.array_equal(cf.bus["BUS_I"].values, np.arange(len(cf.bus)))

    # branch endpoints must now reference 0..n-1
    assert cf.branch["F_BUS"].between(0, len(cf.bus) - 1).all()
    assert cf.branch["T_BUS"].between(0, len(cf.bus) - 1).all()

    # gen buses must also reference 0..n-1
    assert cf.gen["GEN_BUS"].between(0, len(cf.bus) - 1).all()
