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
        update_index=True,
        load_case_engine=None,
        allow_any_keys=False,
        columns_templates=None,
    ):
        """
        Load data and initialize the CaseFrames class.

        Args:
            data (str | dict | oct2py.io.Struct | np.ndarray):
                - str: File path to .m file or MATPOWER case name.
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
        # TODO: support read excel
        # TODO: support Path object
        if columns_templates is None:
            self.columns_templates = copy.deepcopy(COLUMNS)
        else:
            self.columns_templates = {**COLUMNS, **columns_templates}

        if isinstance(data, str):
            # TYPE: str of path
            path = self._get_path(data)

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
            update_index = False
        else:
            message = (
                f"Not supported source type {type(data)}. Data must be a str path to"
                f" .m file, or oct2py.io.Struct, dict, or structured NumPy array."
            )
            raise TypeError(message)

        if update_index:
            self._update_index()

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
            path (str): File path or MATPOWER case name.

        Returns:
            str: Resolved file path.

        Raises:
            FileNotFoundError: If the file or MATPOWER case cannot be found.
        """
        if os.path.isfile(path):
            return path

        path_added_m = path + ".m"
        if os.path.isfile(path_added_m):
            return path_added_m

        if MATPOWER_EXIST:
            path_added_matpower = os.path.join(matpower.path_matpower, f"data/{path}")
            if os.path.isfile(path_added_matpower):
                return path_added_matpower

            path_added_matpower_m = os.path.join(
                matpower.path_matpower, f"data/{path_added_m}"
            )
            if os.path.isfile(path_added_matpower_m):
                return path_added_matpower_m

        raise FileNotFoundError

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
            list_ = parse_file(attribute, string)
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
                value = pd.Index(list_, name=attribute)
            else:  # bus, branch, gen, gencost, dcline, dclinecost
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

    def _update_index(self):
        """
        Update the index of the bus, branch, and generator tables based on naming.
        """
        if "bus_name" in self._attributes:
            self.bus.set_index(self.bus_name, drop=False, inplace=True)
        else:
            self.bus.set_index(
                pd.RangeIndex(1, len(self.bus.index) + 1), drop=False, inplace=True
            )

        if "branch_name" in self._attributes:
            self.branch.set_index(self.branch_name, drop=False, inplace=True)
        else:
            self.branch.set_index(
                pd.RangeIndex(1, len(self.branch.index) + 1), drop=False, inplace=True
            )

        if "gen_name" in self._attributes:
            self.gen.set_index(self.gen_name, drop=False, inplace=True)
            try:
                self.gencost.set_index(self.gen_name, drop=False, inplace=True)
            except AttributeError:
                pass
        else:
            self.gen.set_index(
                pd.RangeIndex(1, len(self.gen.index) + 1), drop=False, inplace=True
            )
            try:
                self.gencost.set_index(
                    pd.RangeIndex(1, len(self.gen.index) + 1), drop=False, inplace=True
                )
            except AttributeError:
                pass

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

    def to_csv(self, path, prefix="", suffix=""):
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
