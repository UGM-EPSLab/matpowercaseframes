import pandas as pd
from pandas.testing import assert_frame_equal, assert_index_equal

from .core import ReservesFrames


def assert_attributes_equal(obj1, obj2):
    if set(obj1.attributes) != set(obj2.attributes):
        missing_in_obj2 = set(obj1.attributes) - set(obj2.attributes)
        missing_in_obj1 = set(obj2.attributes) - set(obj1.attributes)
        msg = "CaseFrames have different attributes:\n"
        if missing_in_obj2:
            msg += f"  Missing in obj2: {missing_in_obj2}\n"
        if missing_in_obj1:
            msg += f"  Missing in obj1: {missing_in_obj1}\n"
        raise AssertionError(msg)


def assert_cf_equal(cf1, cf2):
    """
    Assert that two CaseFrames objects are equal.

    Args:
        cf1: First CaseFrames object
        cf2: Second CaseFrames object

    Raises:
        AssertionError: If the CaseFrames objects are not equal
    """
    assert_attributes_equal(cf1, cf2)

    for attribute in cf1.attributes:
        try:
            df1 = getattr(cf1, attribute)
            df2 = getattr(cf2, attribute)

            if isinstance(df1, pd.DataFrame):
                try:
                    assert_frame_equal(df1, df2)
                except AssertionError as e:
                    print(f"  ✗ DataFrame '{attribute}' does not match:")
                    print(f"    cf1.{attribute} shape: {df1.shape}")
                    print(f"    cf2.{attribute} shape: {df2.shape}")
                    print(f"    cf1.{attribute} dtypes:\n{df1.dtypes}")
                    print(f"    cf2.{attribute} dtypes:\n{df2.dtypes}")
                    print(f"    cf1.{attribute}:\n{df1}")
                    print(f"    cf2.{attribute}:\n{df2}")
                    raise AssertionError(
                        f"DataFrame '{attribute}' mismatch:\n{str(e)}"
                    ) from e

            elif isinstance(df1, pd.Index):
                try:
                    assert_index_equal(df1, df2)
                except AssertionError as e:
                    print(f"  ✗ Index '{attribute}' does not match:")
                    print(f"    cf1.{attribute}: {df1.tolist()}")
                    print(f"    cf2.{attribute}: {df2.tolist()}")
                    raise AssertionError(
                        f"Index '{attribute}' mismatch:\n{str(e)}"
                    ) from e

            elif isinstance(df1, ReservesFrames):
                try:
                    assert_reserves_equal(df1, df2)
                except AssertionError as e:
                    raise AssertionError(
                        f"ReservesFrames '{attribute}' mismatch:\n{str(e)}"
                    ) from e

            else:
                # for scalar values (version, baseMVA, etc.)
                try:
                    assert df1 == df2
                except (AssertionError, ValueError) as e:
                    print(f"  ✗ Value '{attribute}' does not match:")
                    print(f"    cf1.{attribute}: {df1} (type: {type(df1)})")
                    print(f"    cf2.{attribute}: {df2} (type: {type(df2)})")
                    raise AssertionError(
                        f"Value '{attribute}' mismatch: {df1} != {df2}"
                    ) from e

        except Exception as e:
            print(f"  ✗ Error comparing attribute '{attribute}': {e}")
            raise


def assert_reserves_equal(reserves1, reserves2):
    """
    Assert that two ReservesFrames objects are equal.

    Args:
        reserves1: First ReservesFrames object
        reserves2: Second ReservesFrames object
        attribute_name: Name of the reserves attribute for error messages
        verbose: If True, print detailed error messages

    Raises:
        AssertionError: If the ReservesFrames objects are not equal
    """
    if set(reserves1.attributes) != set(reserves2.attributes):
        missing_in_reserves2 = set(reserves1.attributes) - set(reserves2.attributes)
        missing_in_reserves1 = set(reserves2.attributes) - set(reserves1.attributes)
        msg = ""
        if missing_in_reserves2:
            msg += f"  Missing in reserves2: {missing_in_reserves2}\n"
        if missing_in_reserves1:
            msg += f"  Missing in reserves1: {missing_in_reserves1}\n"
        raise AssertionError(msg)

    for attr in reserves1.attributes:
        df1 = getattr(reserves1, attr)
        df2 = getattr(reserves2, attr)
        try:
            assert_frame_equal(df1, df2)
        except AssertionError as e:
            print(f"    ✗ reserves.{attr} does not match:")
            print(f"      reserves1.{attr} shape: {df1.shape}")
            print(f"      reserves2.{attr} shape: {df2.shape}")
            print(f"      reserves1.{attr}:\n{df1}")
            print(f"      reserves2.{attr}:\n{df2}")
            raise AssertionError(f"reserves.{attr} mismatch:\n{str(e)}") from e
