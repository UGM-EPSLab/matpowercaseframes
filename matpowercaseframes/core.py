# Copyright (c) 2020, Battelle Memorial Institute
# Copyright 2007 - 2022: numerous others credited in AUTHORS.rst
# Copyright 2022: https://github.com/yasirroni/

import copy
import os

import numpy as np
import pandas as pd

from .constants import ATTRIBUTES, COLUMNS
from .reader import find_attributes, find_name, parse_file

try:
    import matpower

    MATPOWER_EXIST = True
except ImportError:
    MATPOWER_EXIST = False


class CaseFrames:
    def __init__(
        self,
        data=None,
        load_case_engine=None,
        prefix="",
        suffix="",
        allow_any_keys=False,
        update_index=True,
        columns_templates=None,
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

        Raises:
            TypeError: If the input data format is unsupported.
            FileNotFoundError: If the specified file cannot be found.
        """
        # TODO: support read directory containing csv
        # TODO: support Path object
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
            self._attributes = []
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

    def setattr(self, name, value):
        if name not in self._attributes:
            self._attributes.append(name)
        self.__setattr__(name, value)

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

        # Create detailed error message
        error_msg = f"Could not find file or directory '{path}'."
        raise FileNotFoundError(error_msg)

    def _read_matpower(self, filepath, allow_any_keys=False):
        """
        Read and parse a MATPOWER file.

        Old attribute is not guaranted to be replaced in re-read. This method is
        intended to be used only during initialization.

        Args:
            filepath (str): Path to the MATPOWER file.
        """
        with open(filepath) as f:
            string = f.read()

        self.name = find_name(string)
        self._attributes = []

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
        self._attributes = []

        for attribute, list_ in struct.items():
            if attribute not in ATTRIBUTES and not allow_any_keys:
                continue

            if attribute == "version" or attribute == "baseMVA":
                value = list_
            elif attribute in ["bus_name", "branch_name", "gen_name"]:
                value = pd.Index([name[0] for name in list_], name=attribute)
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
        self.name = ""
        self._attributes = []
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
        sheets = pd.read_excel(filepath, index_col=0, sheet_name=None)

        self._attributes = []

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

        self._attributes = []

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
        if n_cols > len(columns):
            if attribute not in ("gencost", "dclinecost"):
                msg = (
                    f"Number of columns in {attribute} ({n_cols}) is greater"
                    f" than the expected number."
                )
                raise IndexError(msg)
            columns = columns[:-1] + [
                "{}_{}".format(columns[-1], i)
                for i in range(n_cols - len(columns), -1, -1)
            ]

        return pd.DataFrame(data, columns=columns)

    @property
    def attributes(self):
        """
        List of attributes that have been parsed from the input data.

        Returns:
            list: List of attribute names.
        """
        return self._attributes

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
                    pd.RangeIndex(1, len(attribute_data.index) + 1),
                    drop=False,
                    inplace=True,
                )

        # gencost is optional
        try:
            if "gen_name" in self._attributes:
                self.gencost.set_index(self.gen_name, drop=False, inplace=True)
            else:
                self.gencost.set_index(
                    pd.RangeIndex(1, len(self.gen.index) + 1), drop=False, inplace=True
                )
        except AttributeError:
            pass

        # other attributes
        if allow_any_keys:
            for attribute in self._attributes:
                if attribute in ["bus", "branch", "gen", "gencost"]:
                    continue
                attribute_data = getattr(self, attribute)
                if isinstance(attribute_data, (pd.DataFrame, pd.Series)):
                    # check if index is a RangeIndex
                    if attribute_data.index.dtype == int:
                        # replace the index with a new RangeIndex starting at 1
                        attribute_data.set_index(
                            pd.RangeIndex(start=1, stop=len(attribute_data) + 1),
                            drop=False,
                            inplace=True,
                        )

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
        for attribute in self._attributes:
            df = getattr(self, attribute)
            if isinstance(df, pd.DataFrame):
                df.reset_index(drop=True, inplace=True)
        bus_map = {v: k for k, v in enumerate(self.bus["BUS_I"])}
        self.bus["BUS_I"] = self.bus.index
        self.branch[["F_BUS", "T_BUS"]] = self.branch[["F_BUS", "T_BUS"]].replace(
            bus_map
        )
        self.gen["GEN_BUS"] = self.gen["GEN_BUS"].replace(bus_map)

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
        data = {
            "version": getattr(self, "version", None),
            "baseMVA": getattr(self, "baseMVA", None),
        }
        for attribute in self._attributes:
            if attribute == "version" or attribute == "baseMVA":
                data[attribute] = getattr(self, attribute)
            elif attribute in ["bus_name", "branch_name", "gen_name"]:
                # NOTE: must be in 2D Cell or 2D np.array
                data[attribute] = np.atleast_2d(getattr(self, attribute).values).T
            else:
                data[attribute] = getattr(self, attribute).values.tolist()
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
