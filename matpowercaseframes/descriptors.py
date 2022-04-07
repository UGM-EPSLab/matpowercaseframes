# Copyright (c) 2020, Battelle Memorial Institute
# Copyright 2007 - 2022: numerous others credited in AUTHORS.rst
# Copyright 2022: https://github.com/yasirroni/

import pandas as pd

import logging
logger = logging.getLogger(__file__)

class Descriptor(object):
    ''' Descriptor Base class for psst case '''
    name = None
    ty = None

    def __get__(self, instance, cls):
        try:
            return instance.__dict__[self.name]
        except KeyError:
            raise AttributeError("'{}' object has no attribute {}".format(instance.__class__.__name__, self.name))

    def __set__(self, instance, value):
        if self.ty is not None and not isinstance(value, self.ty):
            value = self.ty(value)
        if self._is_valid(instance, value):
            instance.__dict__[self.name] = value
        else:
            raise AttributeError('Validation for {} failed. Please check {}'.format(self.name, value))

    def __delete__(self, instance):
        raise AttributeError("Cannot delete attribute {}".format(self.name))

    def _is_valid(self, instance, value):
        return True

class Name(Descriptor):
    ''' Name Descriptor for a case '''
    name = 'name'
    ty = str


class Version(Descriptor):
    ''' Version Descriptor for a case '''
    name = 'version'
    ty = str


class BaseMVA(Descriptor):
    ''' BaseMVA Descriptor for a case '''
    name = 'baseMVA'
    ty = float


class Bus(Descriptor):
    ''' Bus Descriptor for a case '''
    name = 'bus'
    ty = pd.DataFrame


class BusName(Descriptor):
    ''' Bus Name Descriptor for a case '''
    name = 'bus_name'
    ty = pd.DataFrame


class Branch(Descriptor):
    ''' Branch Descriptor for a case '''
    name = 'branch'
    ty = pd.DataFrame


class BranchName(Descriptor):
    ''' Branch Name Descriptor for a case '''
    name = 'branch_name'
    ty = pd.DataFrame


class Gen(Descriptor):
    ''' Gen Descriptor for a case '''
    name = 'gen'
    ty = pd.DataFrame


class GenCost(Descriptor):
    ''' GenCost Descriptor for a case '''
    name = 'gencost'
    ty = pd.DataFrame


class GenName(Descriptor):
    ''' Gen Name for a case '''
    name = 'gen_name'
    ty = pd.DataFrame


class _Attributes(Descriptor):
    name = '_attributes'
    ty = list
