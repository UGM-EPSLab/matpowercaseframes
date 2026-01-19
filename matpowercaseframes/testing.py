import pandas as pd
from pandas.testing import assert_frame_equal, assert_index_equal

from .core import DataFramesStruct


def assert_attributes_equal(struct1, struct2):
    if set(struct1.attributes) != set(struct2.attributes):
        missing_in_struct2 = set(struct1.attributes) - set(struct2.attributes)
        missing_in_struct1 = set(struct2.attributes) - set(struct1.attributes)
        msg = "CaseFrames have different attributes:\n"
        if missing_in_struct2:
            msg += f"  Missing in struct2: {missing_in_struct2}\n"
        if missing_in_struct1:
            msg += f"  Missing in struct1: {missing_in_struct1}\n"
        raise AssertionError(msg)


def assert_frames_struct_equal(struct1, struct2):
    """
    Assert that two DataFramesStruct objects are equal.

    Recursively compares nested DataFramesStruct objects.

    Args:
        struct1: First DataFramesStruct object
        struct2: Second DataFramesStruct object

    Raises:
        AssertionError: If the DataFramesStruct objects are not equal
    """
    assert_attributes_equal(struct1, struct2)

    for attribute in struct1.attributes:
        try:
            value1 = getattr(struct1, attribute)
            value2 = getattr(struct2, attribute)

            if isinstance(value1, pd.DataFrame):
                try:
                    assert_frame_equal(value1, value2)
                except AssertionError as e:
                    print(f"  ✗ DataFrame '{attribute}' does not match:")
                    print(f"    struct1.{attribute} shape: {value1.shape}")
                    print(f"    struct2.{attribute} shape: {value2.shape}")
                    print(f"    struct1.{attribute} dtypes:\n{value1.dtypes}")
                    print(f"    struct2.{attribute} dtypes:\n{value2.dtypes}")
                    print(f"    struct1.{attribute}:\n{value1}")
                    print(f"    struct2.{attribute}:\n{value2}")
                    raise AssertionError(
                        f"DataFrame '{attribute}' mismatch:\n{str(e)}"
                    ) from e

            elif isinstance(value1, pd.Index):
                try:
                    assert_index_equal(value1, value2)
                except AssertionError as e:
                    print(f"  ✗ Index '{attribute}' does not match:")
                    print(f"    struct1.{attribute}: {value1.tolist()}")
                    print(f"    struct2.{attribute}: {value2.tolist()}")
                    raise AssertionError(
                        f"Index '{attribute}' mismatch:\n{str(e)}"
                    ) from e

            elif isinstance(value1, DataFramesStruct):
                # recursive for DataFramesStruct objects, for example ReservesFrames
                try:
                    assert_frames_struct_equal(value1, value2)
                except AssertionError as e:
                    raise AssertionError(
                        f"DataFramesStruct '{attribute}' mismatch:\n{str(e)}"
                    ) from e

            else:
                # for scalar values (version, baseMVA, etc.)
                try:
                    assert value1 == value2
                except (AssertionError, ValueError) as e:
                    print(f"  ✗ Value '{attribute}' does not match:")
                    print(f"    struct1.{attribute}: {value1} (type: {type(value1)})")
                    print(f"    struct2.{attribute}: {value2} (type: {type(value2)})")
                    raise AssertionError(
                        f"Value '{attribute}' mismatch: {value1} != {value2}"
                    ) from e

        except Exception as e:
            print(f"  ✗ Error comparing attribute '{attribute}': {e}")
            raise
