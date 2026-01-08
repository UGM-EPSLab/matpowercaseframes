import pandas as pd
from pandas.testing import assert_frame_equal, assert_index_equal


def assert_cf_equal(cf1, cf2):
    for attribute in cf1.attributes:
        df1 = getattr(cf1, attribute)
        df2 = getattr(cf2, attribute)
        if isinstance(df1, pd.DataFrame):
            assert_frame_equal(df1, df2)
        elif isinstance(df1, pd.Index):
            assert_index_equal(df1, df2)
        else:
            try:
                assert df1 == df2
            except ValueError as e:
                print(df1, df2)
                raise ValueError(e)
