#    The index, name and meaning of each column of the branch matrix is given
#    below:
#
#    columns 1-11 must be included in input matrix (in case file)
#     1  F_BUS       f, from bus number
#     2  T_BUS       t, to bus number
#     3  BR_R        r, resistance (p.u.)
#     4  BR_X        x, reactance (p.u.)
#     5  BR_B        b, total line charging susceptance (p.u.)
#     6  RATE_A      rateA, MVA rating A (long term rating)
#     7  RATE_B      rateB, MVA rating B (short term rating)
#     8  RATE_C      rateC, MVA rating C (emergency rating)
#     9  TAP         ratio, transformer off nominal turns ratio
#     10 SHIFT       angle, transformer phase shift angle (degrees)
#     11 BR_STATUS   initial branch status, 1 - in service, 0 - out of service
#     12 ANGMIN      minimum angle difference, angle(Vf) - angle(Vt) (degrees)
#     13 ANGMAX      maximum angle difference, angle(Vf) - angle(Vt) (degrees)
#                    (The voltage angle difference is taken to be unbounded below
#                     if ANGMIN < -360 and unbounded above if ANGMAX > 360.
#                     If both parameters are zero, it is unconstrained.)
#
#    columns 14-17 are added to matrix after power flow or OPF solution
#    they are typically not present in the input matrix
#     14 PF          real power injected into "from" end of branch (MW)
#     15 QF          reactive power injected into "from" end of branch (MVAr)
#     16 PT          real power injected into "to" end of branch (MW)
#     17 QT          reactive power injected into "to" end of branch (MVAr)
#
#    columns 18-21 are added to matrix after OPF solution
#    they are typically not present in the input matrix
#                    (assume OPF objective function has units, u)
#     18 MU_SF       Kuhn-Tucker multiplier on MVA limit at "from" bus (u/MVA)
#     19 MU_ST       Kuhn-Tucker multiplier on MVA limit at "to" bus (u/MVA)
#     20 MU_ANGMIN   Kuhn-Tucker multiplier lower angle difference limit (u/degree)
#     21 MU_ANGMAX   Kuhn-Tucker multiplier upper angle difference limit (u/degree)

#    MATPOWER
#    Copyright (c) 1996-2016, Power Systems Engineering Research Center (PSERC)
#    by Ray Zimmerman, PSERC Cornell
#
#    This file is part of MATPOWER.
#    Covered by the 3-clause BSD License (see LICENSE file for details).
#    See https://matpower.org for more info.

# define the indices
F_BUS = 0 # f, from bus number
T_BUS = 1 # t, to bus number
BR_R = 2 # r, resistance (p.u.)
BR_X = 3 # x, reactance (p.u.)
BR_B = 4 # b, total line charging susceptance (p.u.)
RATE_A = 5 # rateA, MVA rating A (long term rating)
RATE_B = 6 # rateB, MVA rating B (short term rating)
RATE_C = 7 # rateC, MVA rating C (emergency rating)
TAP = 8 # ratio, transformer off nominal turns ratio
SHIFT = 9 # angle, transformer phase shift angle (degrees)
BR_STATUS = 10 # initial branch status, 1 - in service, 0 - out of service
ANGMIN = 11 # minimum angle difference, angle(Vf) - angle(Vt) (degrees)
ANGMAX = 12 # maximum angle difference, angle(Vf) - angle(Vt) (degrees)

# included in power flow solution, not necessarily in input
PF = 13 # real power injected at "from" bus end (MW)       (not in PTI format)
QF = 14 # reactive power injected at "from" bus end (MVAr) (not in PTI format)
PT = 15 # real power injected at "to" bus end (MW)         (not in PTI format)
QT = 16 # reactive power injected at "to" bus end (MVAr)   (not in PTI format)

# included in opf solution, not necessarily in input
# assume objective function has units, u
MU_SF = 17 # Kuhn-Tucker multiplier on MVA limit at "from" bus (u/MVA)
MU_ST = 18 # Kuhn-Tucker multiplier on MVA limit at "to" bus (u/MVA)
MU_ANGMIN = 19 # Kuhn-Tucker multiplier lower angle difference limit (u/degree)
MU_ANGMAX = 20 # Kuhn-Tucker multiplier upper angle difference limit (u/degree)
