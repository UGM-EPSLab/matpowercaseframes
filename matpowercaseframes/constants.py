COLUMNS = {
    'bus': [
        'BUS_I', 'BUS_TYPE', 'PD', 'QD', 'GS', 'BS', 'BUS_AREA', 'VM', 'VA',
        'BASE_KV', 'ZONE', 'VMAX', 'VMIN', 'LAM_P', 'LAM_Q', 'MU_VMAX',
        'MU_VMIN'
    ],
    'gen': [
        'GEN_BUS', 'PG', 'QG', 'QMAX', 'QMIN', 'VG', 'MBASE', 'GEN_STATUS',
        'PMAX', 'PMIN', 'PC1', 'PC2', 'QC1MIN', 'QC1MAX', 'QC2MIN', 'QC2MAX',
        'RAMP_AGC', 'RAMP_10', 'RAMP_30', 'RAMP_Q', 'APF', 'MU_PMAX',
        'MU_PMIN', 'MU_QMAX', 'MU_QMIN'
    ],
    'branch': [
        'F_BUS', 'T_BUS', 'BR_R', 'BR_X', 'BR_B', 'RATE_A', 'RATE_B',
        'RATE_C', 'TAP', 'SHIFT', 'BR_STATUS', 'ANGMIN', 'ANGMAX', 'PF', 'QF',
        'PT', 'QT', 'MU_SF', 'MU_ST', 'MU_ANGMIN', 'MU_ANGMAX'
    ],
    'gencost': ['MODEL', 'STARTUP', 'SHUTDOWN', 'NCOST', 'COST'],
    'bus_name': ['BUS_NAME'],
    'branch_name': ['BRANCH_NAME'],
    'gen_name': ['GEN_NAME']
}

BUS_TYPES = {
    'PQ': 1,
    'PV': 2,
    'REF': 3,
    'NONE': 4
}

COST_MODELS = {
    'PW_LINEAR': 1,
    'POLYNOMIAL': 2
}

ATTRIBUTES = ('version', 'baseMVA', 'bus', 'branch', 'gen', 'gencost', 'bus_name')

# TODO:
# Support following attributes:
# dcline
# ct
