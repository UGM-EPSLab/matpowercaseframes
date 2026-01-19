#   The index, name and meaning of each column of the dcline matrix is given
#   below:
#
#   columns 0-16 must be included in input matrix (in case file)
#    0  F_BUS     f, "from" bus number
#    1  T_BUS     t,  "to"  bus number
#    2  BR_STATUS initial dcline status, 1 - in service, 0 - out of service
#    3  PF        MW flow at "from" bus ("from" -> "to")
#    4  PT        MW flow at  "to"  bus ("from" -> "to")
#    5  QF        MVAr injection at "from" bus ("from" -> "to")
#    6  QT        MVAr injection at  "to"  bus ("from" -> "to")
#    7  VF        voltage setpoint at "from" bus (p.u.)
#    8  VT        voltage setpoint at  "to"  bus (p.u.)
#    9  PMIN      lower limit on PF (MW flow at "from" end)
#   10  PMAX      upper limit on PF (MW flow at "from" end)
#   11  QMINF     lower limit on MVAr injection at "from" bus
#   12  QMAXF     upper limit on MVAr injection at "from" bus
#   13  QMINT     lower limit on MVAr injection at  "to"  bus
#   14  QMAXT     upper limit on MVAr injection at  "to"  bus
#   15  LOSS0     constant term of linear loss function (MW)
#   16  LOSS1     linear term of linear loss function (MW/MW)
#                 (loss = LOSS0 + LOSS1 * PF)
#
#   columns 17-22 are added to matrix after OPF solution
#   they are typically not present in the input matrix
#                 (assume OPF objective function has units, u)
#   17  MU_PMIN   Kuhn-Tucker multiplier on lower flow lim at "from" bus (u/MW)
#   18  MU_PMAX   Kuhn-Tucker multiplier on upper flow lim at "from" bus (u/MW)
#   19  MU_QMINF  Kuhn-Tucker multiplier on lower VAr lim at "from" bus (u/MVAr)
#   20  MU_QMAXF  Kuhn-Tucker multiplier on upper VAr lim at "from" bus (u/MVAr)
#   21  MU_QMINT  Kuhn-Tucker multiplier on lower VAr lim at  "to"  bus (u/MVAr)
#   22  MU_QMAXT  Kuhn-Tucker multiplier on upper VAr lim at  "to"  bus (u/MVAr)
#
# See also toggle_dcline.

#   MATPOWER
#   Copyright (c) 2011-2024, Power Systems Engineering Research Center (PSERC)
#   by Ray Zimmerman, PSERC Cornell
#
#   This file is part of MATPOWER.
#   Covered by the 3-clause BSD License (see LICENSE file for details).
#   See https://matpower.org for more info.

# define the indices
F_BUS = 0  # f, "from" bus number
T_BUS = 1  # t,  "to"  bus number
BR_STATUS = 2  # initial dcline status, 1 - in service, 0 - out of service
PF = 3  # MW flow at "from" bus ("from" -> "to")
PT = 4  # MW flow at  "to"  bus ("from" -> "to")
QF = 5  # MVAr injection at "from" bus ("from" -> "to")
QT = 6  # MVAr injection at  "to"  bus ("from" -> "to")
VF = 7  # voltage setpoint at "from" bus (p.u.)
VT = 8  # voltage setpoint at  "to"  bus (p.u.)
PMIN = 9  # lower limit on PF (MW flow at "from" end)
PMAX = 10  # upper limit on PF (MW flow at "from" end)
QMINF = 11  # lower limit on MVAr injection at "from" bus
QMAXF = 12  # upper limit on MVAr injection at "from" bus
QMINT = 13  # lower limit on MVAr injection at  "to"  bus
QMAXT = 14  # upper limit on MVAr injection at  "to"  bus
LOSS0 = 15  # constant term of linear loss function (MW)
LOSS1 = 16  # linear term of linear loss function (MW)
MU_PMIN = 17  # Kuhn-Tucker multiplier on lower flow lim at "from" bus (u/MW)
MU_PMAX = 18  # Kuhn-Tucker multiplier on upper flow lim at "from" bus (u/MW)
MU_QMINF = 19  # Kuhn-Tucker multiplier on lower VAr lim at "from" bus (u/MVAr)
MU_QMAXF = 20  # Kuhn-Tucker multiplier on upper VAr lim at "from" bus (u/MVAr)
MU_QMINT = 21  # Kuhn-Tucker multiplier on lower VAr lim at  "to"  bus (u/MVAr)
MU_QMAXT = 22  # Kuhn-Tucker multiplier on upper VAr lim at  "to"  bus (u/MVAr)
