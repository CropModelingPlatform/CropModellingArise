from math import *
def Ra(lat, J):
    pi = 3.14159265
    latrad = pi * lat / 180
    Dr = 1 + 0.033 * cos(2 * pi * J / 365)
    Declin = 0.409 * sin((2 * pi * J / 365) - 1.39)
    SolarAngle = tan(latrad) * tan(Declin)
    SolarAngle = -atan(-SolarAngle / sqrt(-SolarAngle * SolarAngle + 1)) + 2 * atan(1)
    Ra_ = (SolarAngle * sin(latrad) * sin(Declin)) + (cos(latrad) * cos(Declin) * sin(SolarAngle))
    Ra_ = 24 * 60 * 0.082 * Dr * Ra_ / pi
    return Ra_


def ET0pm_Tdew(lat, Alt, J, Tn, Tx, Tm, Tdewn, Tdewx, Vm, Rg):
    """
        Calculates ET0 according to FAO Penman-Monteith Equation (Bull.FAO#56)
        altitude Alt in m,
        J in number of the day in the year
        Tn, Tx and Tm respectively minimal,maximal and mean daily temperature in degrees C, Tx, Tm,
        Tdewn, Tdewx, respectively minimal and maximal dewpoint temperature in degrees C
        Vm,average wind distance perr day  in km,
        Rg global radiation in MJ/m2/day
        All variables assumed measured at 2m above soil
    """
    sigma = 0.000000004903
    if (lat is None or Alt is None or J is None or Tn is None or Tx is None or  Tm is None or Tdewn is None or Tdewx is None or  Vm is None or  Rg is None):
        return None
    else:
        gamma = 101.3 * ((293 - 0.0065 * (Alt)) / 293) ** 5.26
        gamma = 0.000665 * gamma
        E0SatTn = 0.6108 * exp(17.27 * Tn / (Tn + 237.3))
        E0SatTx = 0.6108 * exp(17.27 * Tx / (Tx + 237.3))
        SlopeSat = 4098 * (0.6108 * exp(17.27 * Tm / (Tm + 237.3))) / ((Tm + 237.3) ** 2)
        Ea = 0.5 * 0.6108 * (exp(17.27 * Tdewx / (Tdewx + 237.3)) + exp(17.27 * Tdewn / (Tdewn + 237.3)))
        VPD = ((E0SatTn + E0SatTx) / 2) - Ea
        adv = gamma * 900 * Vm * VPD / (Tm + 273)
        Rso = (0.00002 * Alt + 0.75) * Ra(lat, J)
        Rns = (1 - 0.23) * Rg
        Rnl = Rg / Rso
        if Rnl > 1 : Rnl = 1
        Rnl = (Rnl * 1.35 - 0.35) * (-0.14 * sqrt(Ea) + 0.34)
        Tn = Tn + 273.16
        Tx = Tx + 273.16
        Rnl = sigma * (Tn ** 4 + Tx ** 4) * Rnl / 2
        #radiation balance assuming soil heat flux is 0 at a day time step
        Rad = 0.408 * SlopeSat * (Rns - Rnl)
        #ajout des deux termes
        return (Rad + adv) / (SlopeSat + gamma * (0.34 * Vm + 1))
