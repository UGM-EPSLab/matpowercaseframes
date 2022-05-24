#    The index, name and meaning of each column of the gen matrix is given
#    below:
#
#    columns 1-21 must be included in input matrix (in case file)
#     1  GEN_BUS     bus number
#     2  PG          Pg, real power output (MW)
#     3  QG          Qg, reactive power output (MVAr)
#     4  QMAX        Qmax, maximum reactive power output (MVAr)
#     5  QMIN        Qmin, minimum reactive power output (MVAr)
#     6  VG          Vg, voltage magnitude setpoint (p.u.)
#     7  MBASE       mBase, total MVA base of machine, defaults to baseMVA
#     8  GEN_STATUS  status, > 0 - in service, <= 0 - out of service
#     9  PMAX        Pmax, maximum real power output (MW)
#     10 PMIN        Pmin, minimum real power output (MW)
#     11 PC1         Pc1, lower real power output of PQ capability curve (MW)
#     12 PC2         Pc2, upper real power output of PQ capability curve (MW)
#     13 QC1MIN      Qc1min, minimum reactive power output at Pc1 (MVAr)
#     14 QC1MAX      Qc1max, maximum reactive power output at Pc1 (MVAr)
#     15 QC2MIN      Qc2min, minimum reactive power output at Pc2 (MVAr)
#     16 QC2MAX      Qc2max, maximum reactive power output at Pc2 (MVAr)
#     17 RAMP_AGC    ramp rate for load following/AGC (MW/min)
#     18 RAMP_10     ramp rate for 10 minute reserves (MW)
#     19 RAMP_30     ramp rate for 30 minute reserves (MW)
#     20 RAMP_Q      ramp rate for reactive power (2 sec timescale) (MVAr/min)
#     21 APF         area participation factor
#    
#    columns 22-25 are added to matrix after OPF solution
#    they are typically not present in the input matrix
#                    (assume OPF objective function has units, u)
#     22 MU_PMAX     Kuhn-Tucker multiplier on upper Pg limit (u/MW)
#     23 MU_PMIN     Kuhn-Tucker multiplier on lower Pg limit (u/MW)
#     24 MU_QMAX     Kuhn-Tucker multiplier on upper Qg limit (u/MVAr)
#     25 MU_QMIN     Kuhn-Tucker multiplier on lower Qg limit (u/MVAr)

#    MATPOWER
#    Copyright (c) 1996-2016, Power Systems Engineering Research Center (PSERC)
#    by Ray Zimmerman, PSERC Cornell
#
#    This file is part of MATPOWER.
#    Covered by the 3-clause BSD License (see LICENSE file for details).
#    See https://matpower.org for more info.

# define the indices
GEN_BUS     = 0;    # bus number
PG          = 1;    # Pg, real power output (MW)
QG          = 2;    # Qg, reactive power output (MVAr)
QMAX        = 3;    # Qmax, maximum reactive power output at Pmin (MVAr)
QMIN        = 4;    # Qmin, minimum reactive power output at Pmin (MVAr)
VG          = 5;    # Vg, voltage magnitude setpoint (p.u.)
MBASE       = 6;    # mBase, total MVA base of this machine, defaults to baseMVA
GEN_STATUS  = 7;    # status, 1 - machine in service, 0 - machine out of service
PMAX        = 8;    # Pmax, maximum real power output (MW)
PMIN        = 9;   # Pmin, minimum real power output (MW)
PC1         = 10;   # Pc1, lower real power output of PQ capability curve (MW)
PC2         = 11;   # Pc2, upper real power output of PQ capability curve (MW)
QC1MIN      = 12;   # Qc1min, minimum reactive power output at Pc1 (MVAr)
QC1MAX      = 13;   # Qc1max, maximum reactive power output at Pc1 (MVAr)
QC2MIN      = 14;   # Qc2min, minimum reactive power output at Pc2 (MVAr)
QC2MAX      = 15;   # Qc2max, maximum reactive power output at Pc2 (MVAr)
RAMP_AGC    = 16;   # ramp rate for load following/AGC (MW/min)
RAMP_10     = 17;   # ramp rate for 10 minute reserves (MW)
RAMP_30     = 18;   # ramp rate for 30 minute reserves (MW)
RAMP_Q      = 19;   # ramp rate for reactive power (2 sec timescale) (MVAr/min)
APF         = 20;   # area participation factor

# included in opf solution, not necessarily in input
# assume objective function has units, u
MU_PMAX     = 21;   # Kuhn-Tucker multiplier on upper Pg limit (u/MW)
MU_PMIN     = 22;   # Kuhn-Tucker multiplier on lower Pg limit (u/MW)
MU_QMAX     = 23;   # Kuhn-Tucker multiplier on upper Qg limit (u/MVAr)
MU_QMIN     = 24;   # Kuhn-Tucker multiplier on lower Qg limit (u/MVAr)

# Note: When a generator's PQ capability curve is not simply a box and the
# upper Qg limit is binding, the multiplier on this constraint is split into
# it's P and Q components and combined with the appropriate MU_Pxxx and
# MU_Qxxx values. Likewise for the lower Q limits.
