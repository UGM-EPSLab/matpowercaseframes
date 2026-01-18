# Copyright (c) 2020, Battelle Memorial Institute
# Copyright 2007 - 2022: numerous others credited in AUTHORS.rst
# Copyright 2022: https://github.com/yasirroni/

import copy
import os
import warnings

import numpy as np
import pandas as pd

from .constants import ATTRIBUTES, COLUMNS
from .reader import find_attributes, find_name, parse_file
from .utils import get_attr, has_attr

try:
    import matpower

    MATPOWER_EXIST = True
except ImportError:
    MATPOWER_EXIST = False


class DataFramesStruct:
    """Base class for struct-like containers with DataFrames."""

    def __init__(self):
        """Initialize the base struct with an empty attributes list."""
        self._attributes = []

    def setattr(self, name, value):
        """
        Set attribute and track it in _attributes list.

        Args:
            name (str): Attribute name.
            value: Attribute value.
        """
        if name not in self._attributes:
            self._attributes.append(name)
        super().__setattr__(name, value)

    def to_dict(self):
        """
        Convert the DataFramesStruct data into a dictionary.


        Returns:
            dict: Dictionary with attribute names as keys and their data as values.
        """
        # TODO: support mpc = cf.to_dict() with reserves data
        data = {}
        for attribute in self._attributes:
            value = getattr(self, attribute)
            if isinstance(value, pd.DataFrame):
                data[attribute] = value.values.tolist()
            elif isinstance(value, DataFramesStruct):
                data[attribute] = value.to_dict()
            else:
                data[attribute] = value

        return data

    def infer_numpy(self):
        """
        Infer and convert data types in all DataFrames to appropriate NumPy-compatible
        types.
        """
        for attribute in self._attributes:
            df = getattr(self, attribute)
            if isinstance(df, pd.DataFrame):
                df = self._infer_numpy(df)
                setattr(self, attribute, df)
            elif isinstance(df, DataFramesStruct):
                df.infer_numpy()

    @staticmethod
    def _infer_numpy(df):
        """
        Infer and convert the data types of a DataFrame to NumPy-compatible types.

        Args:
            df (pd.DataFrame): DataFrame to be processed.

        Returns:
            pd.DataFrame: DataFrame with updated data types.
        """
        df = df.convert_dtypes()

        columns = df.select_dtypes(include=["integer"]).columns
        df[columns] = df[columns].astype(int, errors="ignore")

        columns = df.select_dtypes(include=["float"]).columns
        df[columns] = df[columns].astype(float, errors="ignore")

        columns = df.select_dtypes(include=["string"]).columns
        df[columns] = df[columns].astype(str)

        columns = df.select_dtypes(include=["boolean"]).columns
        df[columns] = df[columns].astype(bool)
        return df

    @property
    def attributes(self):
        """
        List of attributes in this struct object.

        Returns:
            list: List of attribute names.
        """
        return self._attributes

    def __repr__(self):
        """String representation of the struct."""
        attrs = ", ".join(self._attributes)
        return f"{self.__class__.__name__}(attributes=[{attrs}])"


class DataFrameStruct(DataFramesStruct):
    def __init__(self, data, index, colnames):
        super().__init__()

        if data is not None:
            if isinstance(data, dict):
                self.setattr(
                    "table",
                    pd.DataFrame(
                        {k: np.asarray(v).flatten() for k, v in data.items()},
                        index=index,
                    ),
                )
            elif isinstance(data, (np.ndarray, list)):
                self.setattr("table", pd.DataFrame(data, columns=colnames, index=index))
            elif isinstance(data, str):
                # TODO:
                #   1. Support read from file.
                #   2. Differentiate between xdg_table and xdg
                # xgdt = m.loadgenericdata(
                #     data, 'struct', {'colnames', 'data'}, 'xgd_table', cf.to_mpc()
                # )
                raise NotImplementedError(
                    "Reading DataTableFrames from file not yet implemented."
                )
            else:
                raise TypeError(f"Unsupported data type: {type(data)}")

            if index is None:
                self.table.index = pd.RangeIndex(
                    start=1, stop=len(self.table) + 1, name="gen"
                )
        else:
            self.setattr("table", pd.DataFrame(columns=colnames, index=index))

    @property
    def colnames(self):
        """Get column names as 2D array (MATPOWER xgdt format)."""
        return np.atleast_2d(self.table.columns)

    @property
    def data(self):
        """Get data as NumPy array."""
        return self.table.to_numpy()

    @property
    def df(self):
        return self.table

    def to_df(self):
        return self.table

    def to_dict(self):
        return {
            col: self.table[col].values.reshape(-1, 1) for col in self.table.columns
        }

    def infer_numpy(self):
        df = self._infer_numpy(self.table)
        self.table = df

    def __getattr__(self, name):
        """Delegate attribute access to the underlying DataFrame."""
        # if attribute not found in self,
        if name in self.table.columns:
            # try to get it from self.table[name]
            return np.atleast_2d(self.table[name].values)
        else:
            # try to get it from self.table
            return getattr(self.table, name)

    def _repr_html_(self):
        """HTML representation for Jupyter notebooks."""
        return self.table._repr_html_()

    def __repr__(self):
        """String representation."""
        return repr(self.table)

    def __str__(self):
        """String representation for print()."""
        return str(self.table)

    def __getitem__(self, key):
        """Allow indexing like a DataFrame: obj['col'] or obj[0:5]."""
        return self.table[key]

    def __setitem__(self, key, value):
        """Allow setting values like a DataFrame: obj['col'] = values."""
        self.table[key] = value

    def __len__(self):
        """Return number of rows."""
        return len(self.table)

    def __iter__(self):
        """Iterate over column names like a DataFrame."""
        return iter(self.table)


class ReservesFrames(DataFramesStruct):
    """A struct-like container for reserves data, similar to CaseFrames."""

    def __init__(self, data=None, allow_any_keys=False):
        """
        Initialize ReservesFrames with optional data.

        Args:
            data (dict, optional): Dictionary containing reserves DataFrames.
                Expected keys: 'zones', 'req', 'cost', 'qty'
        """
        super().__init__()
        if data is not None:
            if isinstance(data, dict):
                if not allow_any_keys:
                    for key, value in data.items():
                        if key in COLUMNS["reserves"]:
                            self.setattr(key, value)
                else:
                    for key, value in data.items():
                        self.setattr(key, value)
            else:
                raise TypeError(f"ReservesFrames data must be a dict, got {type(data)}")


class CaseFrames(DataFramesStruct):
    def __init__(
        self,
        data=None,
        load_case_engine=None,
        prefix="",
        suffix="",
        allow_any_keys=False,
        update_index=True,
        columns_templates=None,
        reset_index=False,
    ):
        """
        Load data and initialize the CaseFrames class.

        Args:
            data (str | dict | oct2py.io.Struct | np.ndarray):
                - str: File path to MATPOWER case name, .m file, or .xlsx file.
                - dict: Data from a structured dictionary.
                - oct2py.io.Struct: Octave's oct2py struct.
                - np.ndarray: Structured NumPy array with named fields.
            update_index (bool, optional):
                Whether to update the index numbering. Defaults to True.
            load_case_engine (object, optional):
                External engine used to call MATPOWER `loadcase` (e.g. Octave). Defaults
                to None. If None, parse data using matpowercaseframes.reader.parse_file.
            prefix (str, optional):
                Prefix for each attribute when reading from Excel or CSV directory.
                Defaults to an empty string.
            suffix (str, optional):
                Suffix for each attribute when reading from Excel or CSV directory.
                Defaults to an empty string.
            allow_any_keys (bool, optional):
                Whether to allow any keys beyond the predefined ATTRIBUTES. Defaults to
                False.
            columns_templates (dict, optional):
                Custom column templates for DataFrames. Defaults to None.
            reset_index (bool, optional):
                Whether to reset indices to 0-based numbering. Defaults to False.

        Raises:
            TypeError: If the input data format is unsupported.
            FileNotFoundError: If the specified file cannot be found.
        """
        # TODO: support Path object
        super().__init__()
        if columns_templates is None:
            self.columns_templates = copy.deepcopy(COLUMNS)
        else:
            self.columns_templates = {**COLUMNS, **columns_templates}

        self._read_data(
            data=data,
            load_case_engine=load_case_engine,
            prefix=prefix,
            suffix=suffix,
            allow_any_keys=allow_any_keys,
        )
        if update_index and self._attributes:
            self._update_index(allow_any_keys=allow_any_keys)
        if reset_index:
            self.reset_index()

    def _read_data(
        self,
        data=None,
        load_case_engine=None,
        prefix="",
        suffix="",
        allow_any_keys=False,
    ):
        if isinstance(data, str):
            # TODO: support Path
            # TYPE: str of path
            path = self._get_path(data)

            # check if path is a directory (for CSV files)
            if os.path.isdir(path):
                self._read_csv_dir(
                    dirpath=path,
                    prefix=prefix,
                    suffix=suffix,
                    allow_any_keys=allow_any_keys,
                )
                self.name = os.path.basename(path)
            else:
                path_no_ext, ext = os.path.splitext(path)

                if ext == ".m":
                    # read `.m` file
                    if load_case_engine is None:
                        # read with matpower parser
                        self._read_matpower(
                            filepath=path,
                            allow_any_keys=allow_any_keys,
                        )
                    else:
                        # read using loadcase
                        mpc = load_case_engine.loadcase(path)
                        self._read_oct2py_struct(
                            struct=mpc,
                            allow_any_keys=allow_any_keys,
                        )
                elif ext == ".xlsx":
                    # read `.xlsx` file
                    self._read_excel(
                        filepath=path,
                        prefix=prefix,
                        suffix=suffix,
                        allow_any_keys=allow_any_keys,
                    )
                    self.name = os.path.basename(path_no_ext)
                else:
                    message = f"Can't find data at {os.path.abspath(data)}"
                    raise FileNotFoundError(message)
        elif isinstance(data, dict):
            # TYPE: dict | oct2py.io.Struct
            self._read_oct2py_struct(
                struct=data,
                allow_any_keys=allow_any_keys,
            )
        elif isinstance(data, np.ndarray):
            # TYPE: structured NumPy array
            # TODO: also support from.mat file via scipy.io
            # TODO: when is the input from numpy array?
            if data.dtype.names is None:
                message = f"Source is {type(data)} but not a structured NumPy array."
                raise TypeError(message)
            self._read_numpy_struct(
                array=data,
                allow_any_keys=allow_any_keys,
            )
        elif data is None:
            self.name = ""
        else:
            message = (
                f"Not supported source type {type(data)}. Data must be a str path to"
                f" .m file, or oct2py.io.Struct, dict, or structured NumPy array."
            )
            raise TypeError(message)

    def setattr_as_df(self, name, value, columns_template=None):
        """
        Convert value to df and assign to attributes.

        Args:
            name (str): Attribute name.
            value: Data that can be converted into DataFrame.
            columns_template: List of column names used for DataFrame column header.
        """
        df = self._get_dataframe(name, value, columns_template=columns_template)
        self.setattr(name, df)

    def update_columns_templates(self, columns_templates):
        self.columns_templates.update(columns_templates)

    @staticmethod
    def _get_path(path):
        """
        Determine the correct file path for the given input.

        Args:
            path (str): File path, directory path, or MATPOWER case name.

        Returns:
            str: Resolved file path or directory path.

        Raises:
            FileNotFoundError: If the file or MATPOWER case cannot be found.
        """
        # directory exist on path (for CSV directory)
        if os.path.isdir(path):
            return path

        # file exist on path
        if os.path.isfile(path):
            return path

        # file exist on path if given a `.m` ext
        path_added_m = path + ".m"
        if os.path.isfile(path_added_m):
            return path_added_m

        # file exist on path if given a `.xlsx` ext
        path_added_xlsx = path + ".xlsx"
        if os.path.isfile(path_added_xlsx):
            return path_added_xlsx

        # looking file in matpower-pip directory
        if MATPOWER_EXIST:
            path_added_matpower = os.path.join(matpower.path_matpower, f"data/{path}")
            if os.path.isfile(path_added_matpower):
                return path_added_matpower

            path_added_matpower_m = os.path.join(
                matpower.path_matpower, f"data/{path_added_m}"
            )
            if os.path.isfile(path_added_matpower_m):
                return path_added_matpower_m

        message = f"Can't find data at {os.path.abspath(path)}"
        raise FileNotFoundError(message)

    def _read_matpower(self, filepath, allow_any_keys=False):
        """
        Read and parse a MATPOWER file.

        Old attribute is not guaranted to be replaced in re-read. This method is
        intended to be used only during initialization.

        Args:
            filepath (str): Path to the MATPOWER file.
        """
        # TODO: support reserves
        with open(filepath) as f:
            string = f.read()

        self.name = find_name(string)

        for attribute in find_attributes(string):
            if attribute not in ATTRIBUTES and not allow_any_keys:
                continue

            # TODO: compare with GridCal approach
            list_ = parse_file(attribute, string)  # list_ in nested list array
            if list_ is not None:
                if attribute == "version" or attribute == "baseMVA":
                    value = list_[0][0]
                elif attribute in ["bus_name", "branch_name", "gen_name"]:
                    value = pd.Index([name[0] for name in list_], name=attribute)
                else:  # bus, branch, gen, gencost, dcline, dclinecost
                    n_cols = max([len(l) for l in list_])
                    value = self._get_dataframe(attribute, list_, n_cols)

                self.setattr(attribute, value)

    def _read_oct2py_struct(self, struct, allow_any_keys=False):
        """
        Read data from an Octave struct or dictionary.

        Args:
            struct (dict):
                Data in structured dictionary or Octave's oct2py struct format.
        """
        self.name = ""

        for attribute, list_ in struct.items():
            if attribute not in ATTRIBUTES and not allow_any_keys:
                continue

            if attribute == "version" or attribute == "baseMVA":
                value = list_
            elif attribute in ["bus_name", "branch_name", "gen_name"]:
                value = pd.Index([name[0] for name in list_], name=attribute)
            elif attribute in ["reserves"]:
                dfs = reserves_data_to_dataframes(list_)
                value = ReservesFrames(dfs)
            else:  # bus, branch, gen, gencost, dcline, dclinecost
                list_ = np.atleast_2d(list_)
                n_cols = list_.shape[1]
                value = self._get_dataframe(attribute, list_, n_cols)

            self.setattr(attribute, value)

        return None

    def _read_numpy_struct(self, array, allow_any_keys=False):
        """
        Read data from a structured NumPy array.

        Args:
            array (np.ndarray): Structured NumPy array with named fields.
        """
        # TODO: support reserves
        self.name = ""
        for attribute in array.dtype.names:
            if attribute not in ATTRIBUTES and not allow_any_keys:
                continue

            if attribute == "version" or attribute == "baseMVA":
                value = array[attribute].item().item()
            elif attribute in ["bus_name", "branch_name", "gen_name"]:
                value = pd.Index(array[attribute].item(), name=attribute)
            else:  # bus, branch, gen, gencost, dcline, dclinecost
                data = array[attribute].item()
                n_cols = data.shape[1]
                value = self._get_dataframe(attribute, data, n_cols)

            self.setattr(attribute, value)

    def _read_excel(self, filepath, prefix="", suffix="", allow_any_keys=False):
        """
        Read data from an Excel file.

        Args:
            filepath (str): File path for the Excel file.
            prefix (str): Sheet prefix for each attribute in the Excel file.
            suffix (str): Sheet suffix for each attribute in the Excel file.
        """
        # TODO: support reserves
        sheets = pd.read_excel(filepath, index_col=0, sheet_name=None)

        # info sheet to extract general metadata
        info_sheet_name = f"{prefix}info{suffix}"
        if info_sheet_name in sheets:
            info_data = sheets[info_sheet_name]

            value = info_data.loc["version", "INFO"].item()
            self.setattr("version", str(value))

            value = info_data.loc["baseMVA", "INFO"].item()
            self.setattr("baseMVA", value)

        # iterate through the remaining sheets
        for attribute, sheet_data in sheets.items():
            # skip the info sheet
            if attribute == info_sheet_name:
                continue

            # remove prefix and suffix to get the attribute name
            if prefix and attribute.startswith(prefix):
                attribute = attribute[len(prefix) :]
            if suffix and attribute.endswith(suffix):
                attribute = attribute[: -len(suffix)]

            # check attribute rule
            if attribute not in ATTRIBUTES and not allow_any_keys:
                continue

            if attribute in ["bus_name", "branch_name", "gen_name"]:
                # convert back to an index
                value = pd.Index(sheet_data[attribute].values.tolist(), name=attribute)
            else:
                value = sheet_data

            self.setattr(attribute, value)

    def _read_csv_dir(self, dirpath, prefix="", suffix="", allow_any_keys=False):
        """
        Read data from a directory of CSV files.

        Args:
            dirpath (str): Directory path containing the CSV files.
            prefix (str): File prefix for each attribute CSV file.
            suffix (str): File suffix for each attribute CSV file.
            allow_any_keys (bool): Whether to allow any keys beyond ATTRIBUTES.
        """
        # TODO: support reserves
        # create a dictionary mapping attribute names to file paths
        csv_data = {}
        for csv_file in os.listdir(dirpath):
            if csv_file.endswith(".csv"):
                # remove prefix and suffix to get the attribute name
                attribute = csv_file[:-4]  # remove '.csv' extension

                if prefix and attribute.startswith(prefix):
                    attribute = attribute[len(prefix) :]
                if suffix and attribute.endswith(suffix):
                    attribute = attribute[: -len(suffix)]

                csv_data[attribute] = os.path.join(dirpath, csv_file)

        # info CSV to extract general metadata
        info_name = "info"
        if info_name in csv_data:
            info_data = pd.read_csv(csv_data[info_name], index_col=0)

            value = info_data.loc["version", "INFO"].item()
            self.setattr("version", str(value))

            value = info_data.loc["baseMVA", "INFO"].item()
            self.setattr("baseMVA", value)

        # iterate through the remaining CSV files
        for attribute, filepath in csv_data.items():
            # skip the info file
            if attribute == info_name:
                continue

            # check attribute rule
            if attribute not in ATTRIBUTES and not allow_any_keys:
                continue

            # read CSV file
            sheet_data = pd.read_csv(filepath, index_col=0)

            if attribute in ["bus_name", "branch_name", "gen_name"]:
                # convert back to an index
                value = pd.Index(sheet_data[attribute].values.tolist(), name=attribute)
            else:
                value = sheet_data

            self.setattr(attribute, value)

    def _get_dataframe(self, attribute, data, n_cols=None, columns_template=None):
        """
        Create a DataFrame with proper columns from raw data.

        Args:
            attribute (str): Name of the attribute.
            data (list | np.ndarray): Data for the attribute.
            n_cols (int): Number of columns in the data.

        Returns:
            pd.DataFrame: DataFrame with appropriate columns.

        Raises:
            IndexError:
                If the number of columns in the data exceeds the expected number.
        """
        data = np.atleast_2d(data)
        if n_cols is None:
            n_cols = data.shape[1]

        # NOTE: .get('key') instead of ['key'] to default range
        # TODO: support custom COLUMNS
        if columns_template is None:
            # get columns_template, default to range
            columns_template = self.columns_templates.get(
                attribute, list(range(n_cols))
            )

        columns = columns_template[:n_cols]

        # special case for gencost and dclinecost
        if n_cols > len(columns):
            if attribute not in ("gencost", "dclinecost"):
                msg = (
                    f"Number of columns in {attribute} ({n_cols}) is greater"
                    f" than the expected number."
                )
                raise IndexError(msg)
            NCOST = n_cols - len(columns)
            # Warning if mixed models exist
            gencost_models = data[:, 0]
            first_row_model = int(gencost_models[0])  # TODO: support mixed models
            unique_models = np.unique(gencost_models).astype(int)

            if len(unique_models) > 1:
                warnings.warn(
                    f"Mixed cost models detected in {attribute}: "
                    f"{unique_models.tolist()}. "
                    f"Using model type {first_row_model} from first row. "
                    "Mixed models are not fully supported.",
                    UserWarning,
                    stacklevel=2,
                )

            if first_row_model == 1:  # PW_LINEAR
                ncost_cols = [
                    f"{prefix}{i}"
                    for i in range(1, (NCOST // 2) + 1)
                    for prefix in ("X", "Y")
                ]
                columns = columns + ncost_cols
            else:  # POLYNOMIAL
                columns = columns + [f"C{i}" for i in range(NCOST - 1, -1, -1)]

        return pd.DataFrame(data, columns=columns)

    def _update_index(self, allow_any_keys=False):
        """
        Update the index of the bus, branch, and generator tables based on naming. If
        naming is not available, index start from 1 to N.
        """
        for attribute, attribute_name in zip(
            ["bus", "branch", "gen"], ["bus_name", "branch_name", "gen_name"]
        ):
            attribute_data = getattr(self, attribute)
            try:
                attribute_name_data = getattr(self, attribute_name)
                attribute_data.set_index(attribute_name_data, drop=False, inplace=True)
            except AttributeError:
                attribute_data.set_index(
                    pd.RangeIndex(1, len(attribute_data.index) + 1, name=attribute),
                    drop=False,
                    inplace=True,
                )

        # gencost is optional
        # NOTE: try except is better than checking hasattr for common possitive
        try:
            if "gen_name" in self._attributes:
                self.gencost.set_index(self.gen_name, drop=False, inplace=True)
            else:
                self.gencost.set_index(
                    pd.RangeIndex(1, len(self.gen.index) + 1, name="gen"),
                    drop=False,
                    inplace=True,
                )
        except AttributeError:
            # for when self.gencost doesn't exist
            pass

        # NOTE: try hasattr is better than try except for common negative
        if hasattr(self, "reserves"):
            self.reserves.zones.columns = pd.RangeIndex(
                start=1, stop=len(self.gen.index) + 1, name="gen"
            )

        # other attributes
        if allow_any_keys:
            self._update_index_any()

    def _update_index_any(self):
        for attribute in self._attributes:
            if attribute in ["bus", "branch", "gen", "gencost", "reserves"]:
                continue
            attribute_data = getattr(self, attribute)
            if isinstance(attribute_data, (pd.DataFrame, pd.Series)):
                # check if index is a RangeIndex
                if attribute_data.index.dtype == int:
                    # replace the index with a new RangeIndex starting at 1
                    attribute_data.set_index(
                        pd.RangeIndex(
                            start=1, stop=len(attribute_data) + 1, name=attribute
                        ),
                        drop=False,
                        inplace=True,
                    )

    def reset_index(self):
        """
        Reset indices and remap bus-related indices to 0-based values.

        This method ensures that:
            1. All DataFrames in the case have their row indices reset.
            2. Bus numbers (BUS_I) are renumbered from 0 to n-1.
            3. References to buses in branch (F_BUS, T_BUS) and gen (GEN_BUS) tables
            are updated consistently with the new numbering.

        Notes:
            - This method requires `infer_numpy` to be called beforehand,
            as mapping does not support float-backed integers.
            - Support for additional tables (e.g., dcline) is not yet implemented.

        Returns:
            None: The CaseFrames object is modified in place.
        """
        # store original gen index mapping before resetting, used in reserves
        gen_map = {v: k for k, v in enumerate(self.gen.index)}

        for attribute in self._attributes:
            df = getattr(self, attribute)
            if isinstance(df, pd.DataFrame):
                idx_name = df.index.name
                df.reset_index(drop=True, inplace=True)
                df.index.name = idx_name

        bus_map = {v: k for k, v in enumerate(self.bus["BUS_I"])}
        self.bus["BUS_I"] = self.bus.index
        self.branch[["F_BUS", "T_BUS"]] = self.branch[["F_BUS", "T_BUS"]].replace(
            bus_map
        )
        self.gen["GEN_BUS"] = self.gen["GEN_BUS"].replace(bus_map)

        if hasattr(self, "reserves"):
            reserves = self.reserves
            for attribute in ["zones", "req"]:
                df = getattr(reserves, attribute)
                if isinstance(df, pd.DataFrame):
                    idx_name = df.index.name
                    df.reset_index(drop=True, inplace=True)
                    df.index.name = idx_name
            self.reserves.zones.columns = self.gen.index

            if hasattr(self.reserves, "cost"):
                self.reserves.cost = self.reserves.cost.rename(index=gen_map)
                self.reserves.cost.index.name = "gen"
            if hasattr(self.reserves, "qty"):
                self.reserves.qty = self.reserves.qty.rename(index=gen_map)
                self.reserves.qty.index.name = "gen"

    def add_schema_case(self, F=None):
        # add case to follow casefromat/schema
        # !WARNING:
        # this might be deprecated in the future if matpower define this later
        case_name = getattr(self, "name", "")
        version = getattr(self, "version", None)
        baseMVA = getattr(self, "baseMVA", None)
        if F:
            self.setattr_as_df("case", [[case_name, version, baseMVA, F]])
        else:
            self.setattr_as_df("case", [[case_name, version, baseMVA]])

    def to_pu(self):
        """
        Create a new CaseFrame object with data in p.u. and rad.

        Returns:
            CaseFrames: CaseFrames object with data in p.u. and rad.
        """
        # TODO: resclace cost based on mode
        cf = copy.deepcopy(self)

        if "bus" in self.attributes:
            columns = ["PD", "QD", "GS", "BS"]
            columns_exist = [col for col in columns if col in cf.bus.columns]
            cf.bus[columns_exist] = cf.bus[columns_exist] / self.baseMVA
            columns = ["LAM_P", "LAM_Q"]
            columns_exist = [col for col in columns if col in cf.bus.columns]
            cf.bus[columns_exist] = cf.bus[columns_exist] * self.baseMVA
            cf.bus["VA"] = cf.bus["VA"] * np.pi / 180

        if "gen" in self.attributes:
            columns = [
                "PG",
                "QG",
                "QMAX",
                "QMIN",
                "PMAX",
                "PMIN",
                "PC1",
                "PC2",
                "QC1MIN",
                "QC1MAX",
                "QC2MIN",
                "QC2MAX",
                "RAMP_AGC",
                "RAMP_10",
                "RAMP_30",
                "RAMP_Q",
            ]
            columns_exist = [col for col in columns if col in cf.gen.columns]
            cf.gen[columns_exist] = cf.gen[columns_exist] / self.baseMVA

            columns = ["MU_PMAX", "MU_PMIN", "MU_QMAX", "MU_QMIN"]
            columns_exist = [col for col in columns if col in cf.gen.columns]
            cf.gen[columns_exist] = cf.gen[columns_exist] * self.baseMVA

        if "branch" in self.attributes:
            columns = ["RATE_A", "RATE_B", "RATE_C", "PF", "QF", "PT", "QT"]
            columns_exist = [col for col in columns if col in cf.branch.columns]
            cf.branch[columns_exist] = cf.branch[columns_exist] / self.baseMVA

            columns = ["MU_SF", "MU_ST"]
            columns_exist = [col for col in columns if col in cf.branch.columns]
            cf.branch[columns_exist] = cf.branch[columns_exist] * self.baseMVA

            columns = ["SHIFT", "ANGMIN", "ANGMAX"]
            columns_exist = [col for col in columns if col in cf.branch.columns]
            cf.branch[columns_exist] = cf.branch[columns_exist] * np.pi / 180

            columns = ["MU_ANGMIN", "MU_ANGMAX"]
            columns_exist = [col for col in columns if col in cf.branch.columns]
            cf.branch[columns_exist] = cf.branch[columns_exist] * 180 / np.pi

        return cf

    def to_excel(self, path, prefix="", suffix=""):
        """
        Save the CaseFrames data into a single Excel file.

        Args:
            path (str): File path for the Excel file.
            prefix (str): Sheet prefix for each attribute for the Excel file.
            suffix (str): Sheet suffix for each attribute for the Excel file.
        """

        # make dir
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # add extension if not exists
        base, ext = os.path.splitext(path)
        if ext.lower() not in [".xls", ".xlsx"]:
            path = base + ".xlsx"

        # convert to xlsx
        with pd.ExcelWriter(path) as writer:
            pd.DataFrame(
                data={
                    "INFO": {
                        "version": getattr(self, "version", None),
                        "baseMVA": getattr(self, "baseMVA", None),
                    }
                }
            ).to_excel(writer, sheet_name=f"{prefix}info{suffix}")
            for attribute in self._attributes:
                if attribute == "version" or attribute == "baseMVA":
                    continue
                elif attribute in ["bus_name", "branch_name", "gen_name"]:
                    pd.DataFrame(data={attribute: getattr(self, attribute)}).to_excel(
                        writer, sheet_name=f"{prefix}{attribute}{suffix}"
                    )
                else:
                    getattr(self, attribute).to_excel(
                        writer, sheet_name=f"{prefix}{attribute}{suffix}"
                    )

    def to_csv(self, path, prefix="", suffix="", attributes=None):
        """
        Save the CaseFrames data into multiple CSV files.

        Args:
            path (str): Directory path where the CSV files will be saved.
            prefix (str): Sheet prefix for each attribute for the CSV files.
            suffix (str): Sheet suffix for each attribute for the CSV files.
        """
        # make dir
        os.makedirs(path, exist_ok=True)

        pd.DataFrame(
            data={
                "INFO": {
                    "version": getattr(self, "version", None),
                    "baseMVA": getattr(self, "baseMVA", None),
                }
            }
        ).to_csv(os.path.join(path, f"{prefix}info{suffix}.csv"))

        for attribute in self._attributes:
            if attribute == "version" or attribute == "baseMVA":
                continue
            elif attribute in ["bus_name", "branch_name", "gen_name"]:
                pd.DataFrame(data={attribute: getattr(self, attribute)}).to_csv(
                    os.path.join(path, f"{prefix}{attribute}{suffix}.csv")
                )
            else:
                getattr(self, attribute).to_csv(
                    os.path.join(path, f"{prefix}{attribute}{suffix}.csv")
                )

    def to_dict(self):
        """
        Convert the CaseFrames data into a dictionary.

        The value of the data will be in str, numeric, and list.

        Returns:
            dict: Dictionary with attribute names as keys and their data as values.
        """
        # default version and baseMVA to None
        data = {
            "version": None,
            "baseMVA": None,
        }
        for attribute in self._attributes:
            value = getattr(self, attribute)
            if attribute in ["bus_name", "branch_name", "gen_name"]:
                # NOTE: must be in 2D Cell or 2D np.array
                data[attribute] = np.atleast_2d(value.values).T
            elif isinstance(value, pd.DataFrame):
                data[attribute] = value.values.tolist()
            elif isinstance(value, DataFramesStruct):
                data[attribute] = value.to_dict()
            else:
                data[attribute] = value
        return data

    def to_mpc(self):
        """
        Convert the CaseFrames data into a format compatible with MATPOWER (as a
        dictionary).

        The value of the data will be in str, numeric, and list.

        Returns:
            dict: MATPOWER-compatible dictionary with data.
        """
        return self.to_dict()

    def to_schema(self, path, prefix="", suffix=""):
        """
        Convert to format compatible with caseformat/schema.

        This method also mutate the CaseFormat by adding "case" as a new
        attribute if not exists.

        See more:
            https://github.com/caseformat/schema
        """

        if "case" not in self._attributes:
            self.add_schema_case()
        self.to_csv(path, prefix=prefix, suffix=suffix)


def reserves_data_to_dataframes(reserves):
    """
    Convert all mpc.reserves struct data to DataFrames.

    Args:
        reserves: dict or oct2py.io.Struct of mpc.reserves object from MATPOWER

    Returns:
        dict or oct2py.io.Struct containing:
            - 'zones': Reserve zones DataFrame
            - 'req': Reserve requirements DataFrame
            - 'cost': Reserve costs DataFrame (if exists)
            - 'qty': Reserve quantities DataFrame (if exists)
    """
    dfs = {}

    zones_data = get_attr(reserves, "zones")
    n_zones, n_gens = np.array(zones_data).shape
    dfs["zones"] = pd.DataFrame(
        zones_data,
        index=pd.RangeIndex(start=1, stop=n_zones + 1, name="zone"),
        columns=pd.RangeIndex(start=1, stop=n_gens + 1, name="gen"),
    )

    zone_sum = dfs["zones"].sum(axis=0)
    idx_gen_with_reserves = zone_sum[zone_sum > 0].index

    dfs["req"] = pd.DataFrame(
        get_attr(reserves, "req"),
        index=pd.RangeIndex(start=1, stop=n_zones + 1, name="zone"),
        columns=["PREQ"],
    )

    if has_attr(reserves, "cost"):
        dfs["cost"] = pd.DataFrame(
            get_attr(reserves, "cost"), index=idx_gen_with_reserves, columns=["C1"]
        )

    if has_attr(reserves, "qty"):
        dfs["qty"] = pd.DataFrame(
            get_attr(reserves, "qty"), index=idx_gen_with_reserves, columns=["PQTY"]
        )

    return dfs


class xGenDataTableFrames(DataFrameStruct):
    """
    A struct-like and DataFrame-like container for xGenData with MATPOWER
    compatibility. Support standard DataFrame operations.
    """

    def __init__(self, data=None, colnames=None, index=None):
        """
        Initialize DataTableFrames with optional data.

        Args:
            data (np.ndarray | list | dict, optional): Data for DataTableFrames.
            colnames (list, optional): Column names. Defaults to None.
            index (pd.Index, optional): Row index. Defaults to None.
        """
        if data is not None and colnames is None:
            if isinstance(data, dict):
                colnames = list(data.keys())
            else:
                n_col = np.atleast_2d(data).shape[1]
                colnames = COLUMNS["xgd_table"][:n_col]
        elif colnames is not None:
            colnames = np.asarray(colnames).flatten()
        else:
            colnames = []
            # if not allow_any_keys:
            #     # TODO: remove columns in data that are not in COLUMNS
            #     colnames = [
            #         col
            #         for col in colnames
            #         if col in COLUMNS["xgd_table"]
            #     ]

        super().__init__(data=data, index=index, colnames=colnames)

    def to_dict(self):
        """
        Convert to combined dict with both xgd and xgd_table formats.

        Returns:
            dict: Combined dictionary with:
                - Column names as keys with 2D array values (xgd format)
                - 'colnames' and 'data' keys (xgd_table format)
        """
        xgd_dict = self.to_xgd()
        xgdt_dict = self.to_xdgt()
        return {**xgd_dict, **xgdt_dict}

    def to_xgdt(self):
        """
        Convert to xgd_table format (for loadgenericdata).

        Returns:
            dict: Dictionary with 'colnames' (2D array) and 'data' (2D array)
        """
        return {
            "colnames": self.colnames,
            "data": self.data,
        }

    def to_xgd(self):
        """
        Convert to xgd struct format (for loadxgendata/MOST functions).

        Returns:
            dict: Dictionary where keys are column names and values are 2D arrays (n, 1)
        """
        return super().to_dict()
