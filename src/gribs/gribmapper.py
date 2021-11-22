#!/usr/bin/env python3

import builtins
import pathlib
import numpy as np
import fstd2nc
import rpnpy.librmn.all as rmn
from eccodes import GribFile, GribMessage

from gribs.units import Unit

LVL_SFC = "surface"
LVL_ISBL = "isobaricInhPa"
LVL_ISBY = "isobaricLayer"
LVL_TGL = "heightAboveGround"
LVL_DBLL = "depthBelowLandLayer"
LVL_MSL = "meanSea"
LVL_EATM = "atmosphere"
LVL_NTAT = "nominalTop"

class GribMapper():
    VARS = {
        "Albedo":
        {
            "nomvar": {LVL_SFC: "AL", LVL_ISBL: "AL"}
        },
        "Cloud water":
        {
            "nomvar": {LVL_SFC: "QC", LVL_ISBL: "QC"}
        },
        "Geopotential Height":
        {
            "nomvar": {LVL_SFC: "GZ", LVL_ISBL: "GZ"},
            "unit": Unit.gpm_to_dam
        },
        "Land-sea mask":
        {
            "nomvar": {LVL_SFC: "MQ", LVL_ISBL: "MQ"}
        },
        "Orography":  # REAL [m2/s2] --> gpm (geopotential metres)
        {
            "nomvar": {LVL_SFC: "MX", LVL_ISBL: "MX"}
        },
        "Pressure reduced to MSL":
        {
            "nomvar": {LVL_SFC: "PN", LVL_ISBL: "PN"},
            "unit": Unit.Pa_to_hPa
        },
        "Sea ice area fraction":
        {
            "nomvar": {LVL_SFC: "LG", LVL_ISBL: "LG"}
        },
        "Sea surface temperature":
        {
            "nomvar": {LVL_SFC: "TM", LVL_ISBL: "TM"},
            "unit": Unit.K_to_C
        },
        "Skin temperature":
        {
            "nomvar": {LVL_SFC: "TS", LVL_ISBL: "TS"},
            "unit": Unit.K_to_C
        },
        "Snow density":
        {
            "nomvar": {LVL_SFC: "DN", LVL_ISBL: "DN"}
        },
        "Snow depth":
        {
            "nomvar": {LVL_SFC: "SD", LVL_ISBL: "SD"},
            "unit": Unit.m_to_cm,
            "ip1": {LVL_SFC: "ip1_snod_sfc"}
        },
        "Soil moisture content":
        {
            "nomvar": {LVL_SFC: "HS", LVL_ISBL: "HS", LVL_DBLL: "I1"},
            "ip1": {LVL_DBLL: "ip1_soilw_dbll"}
        },
        "Soil Temperature":
        {
            "nomvar": {LVL_SFC: "TP", LVL_ISBL: "TP", LVL_DBLL: "I0"},
            "unit": Unit.K_to_C,
            "ip1": {LVL_DBLL: "ip1_tsoil_dbll"}
        },
        "Specific humidity":
        {
            "nomvar": {LVL_SFC: "HU", LVL_ISBL: "HU"},
        },
        "Surface pressure":
        {
            "nomvar": {LVL_SFC: "P0", LVL_ISBL: "P0"},
            "unit": Unit.Pa_to_hPa
        },
        "Temperature":
        {
            "nomvar": {LVL_SFC: "TT", LVL_ISBL: "TT"},
            "unit": Unit.K_to_C
        },
        "U component of wind":
        {
            "nomvar": {LVL_SFC: "UU", LVL_ISBL: "UU"},
            "unit": Unit.m_per_s_to_kt
        },
        "V component of wind":
        {
            "nomvar": {LVL_SFC: "VV", LVL_ISBL: "VV"},
            "unit": Unit.m_per_s_to_kt
        },
        "Volumetric soil ice":
        {
            "nomvar": {LVL_SFC: "I2", LVL_ISBL: "I2"}  # kg/m2 ?
        }
    }


    def __init__(self, path):
        grib = GribFile(str(path))
        self._msg = GribMessage(grib)
        self._filepath = pathlib.Path(path)
        self._filename = self._filepath.name
        self._level = self._msg["level"]
        self._level_type = self._msg["typeOfLevel"]
        self._name = self._msg["name"]
        self._verbose = False
        self._fstd_id = None
        self._etiket = ""

        try:
            self._var = self.VARS[self._name]
        except KeyError:
            self._var = {"UNKNOWN": {}}

        try:
            ip1_func = self._var["ip1"][self._level_type]
        except KeyError:
            ip1_func = "ip1_from_level"
        self._ip1 = getattr(self, ip1_func)()

        try:
            self._nomvar = self._var["nomvar"][self._level_type]
        except KeyError:
            self._nomvar = "UNKN"

        try:
            self._unit_func = self._var["unit"]
        except KeyError:
            self._unit_func = Unit.ident

    def __del__(self):
        if self._fstd_id:
            rmn.fstcloseall(self._fstd_id)

    def __repr__(self):
        return f"{self._filename}, nomvar: {self.nomvar}, ip1: {self.ip1}"

    def __str__(self):
        return f"{self._filename}, nomvar: {self.nomvar}, ip1: {self.ip1}"

    @property
    def _dlon(self):
        return self._msg["iDirectionIncrementInDegrees"]

    @property
    def _dlat(self):
        return self._msg["jDirectionIncrementInDegrees"]

    @property
    def data(self):
        field = self._msg["values"]
        values = self._convert_unit(field)
        d64 = np.reshape(values, (self.ni, self.nj), order='F')
        return np.float32(d64)

    @property
    def etiket(self):
        return self._etiket

    @etiket.setter
    def etiket(self, value):
        self._etiket = value

    @property
    def ip1(self):
        return self._ip1

    @ip1.setter
    def ip1(self, value):
        self._ip1 = value

    @property
    def _lat_zero(self):
        return self._msg["latitudeOfFirstGridPoint"] / self._msg["angleDivisor"]

    @property
    def _lon_zero(self):
        return self._msg["longitudeOfFirstGridPoint"] / self._msg["angleDivisor"]

    @property
    def ni(self):
        return self._msg["Ni"]

    @property
    def nj(self):
        return self._msg["Nj"]

    @property
    def name(self):
        return self._name

    @property
    def nomvar(self):
        return f"{self._nomvar:<4}"

    @nomvar.setter
    def nomvar(self, value):
        self._nomvar = value
 
    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, value):
        self._verbose = value

    def _convert_unit(self, value):
        return self._unit_func(value)

    def has_grid(self):
        return self._msg["gridDescriptionSectionPresent"] == 1

    def ip1_soilw_dbll(self):
        """
        The only parameter that distinguishes levels
        of 'soilw' field is scaleFactorOfSecondFixedSurface
        Level 10 is value 2 
        Level 100 is value 1
        It may change in the future.
        """
        factor = int(self._msg["scaleFactorOfSecondFixedSurface"])
        # mapping = {1: 1199, 2: 1198}
        # return mapping[factor]
        return rmn.convertIp(3, factor, 3)  # mode=3, kind=3, NEWSTYLE forced to false
        

    def ip1_snod_sfc(self):
        return 59868832  # ip1 1.0, kind=3

    def ip1_tsoil_dbll(self):
        if self._level_type == LVL_DBLL:
            return 1198

    def ip1_from_level(self):
        if self._level < 1101:
            return rmn.ip1_val(self._level, 2)
        else:
            return rmn.ip1_val(self._level, 3)

    def is_latlon(self):
        return self._msg["gridDefinitionDescription"] == "Latitude/longitude "

    def is_convertable(self):
        return self.has_grid() and self.is_latlon()

    def is_required(self):
        try:
            level_known = self._level_type in self.VARS[self.name]["nomvar"]
            if level_known and self.is_convertable():
                return True
        except KeyError:
            return False
        return False

    def _get_fstd_grid_meta(self):
        grtyp = 'L'
        (ig1, ig2, ig3, ig4) = rmn.cxgaig(grtyp, self._lat_zero, self._lon_zero, self._dlat, self._dlon)
        gid = rmn.ezqkdef(self.ni, self.nj, grtyp, ig1, ig2, ig3, ig4)
        return rmn.ezgprm(gid)

    def _fstd_meta(self):
        params = self._get_fstd_grid_meta()
        date_valid = self._msg["validityDate"]
        time_valid = self._msg["validityTime"]
        hour_forec = self._msg["forecastTime"]
        params["dtype"] = 1
        params["shape"] = (self.ni, self.nj, 1)
        params["dateo"] = rmn.newdate(3, date_valid, time_valid) - 3600 * hour_forec
        params["datev"] = rmn.newdate(3, date_valid, time_valid)
        params["deet"] = 3600
        params["npas"] = 0
        params["nbits"] = -32
        params["datyp"] = 1
        params["ip1"] = self.ip1
        params["ip2"] = 0
        params["ip3"] = 0
        params["typvar"] = "P "
        params["nomvar"] = self.nomvar
        params["etiket"] = f"{self._etiket:<12}"
        params["d"] = self.data
        return params

    def _init_fstd_file(self, target, overwrite):
        if target.exists() and overwrite:
            target.unlink()
        if not self._verbose:
            rmn.fstopt(rmn.FSTOP_MSGLVL, rmn.FSTOPI_MSG_CATAST)
            rmn.fstopt(rmn.FSTOP_TOLRNC, rmn.FSTOPI_MSG_CATAST)
        self._fstd_id = rmn.fstopenall(str(target), rmn.FST_RW)
        return self._fstd_id

    def list(self, print=builtins.print):
        print(f"{self._filename}: "
              f"{self.name}, "
              f"level: {self._level}, "
              f"min: {np.min(self.data)}, "
              f"max: {np.max(self.data)}, "
              f"units: {self._msg['parameterUnits']}")

    def plot(self):
        raise NotImplementedError

    def to_rpn(self, target, overwrite=False):
        self._fstd_id = self._init_fstd_file(target, overwrite)
        try:
            rmn.fstecr(iunit=self._fstd_id, data=self.data, meta=self._fstd_meta(), rewrite=True)
        except rmn.FSTDError:
            raise IOError("Problem writing rpn record")
        rmn.fstcloseall(self._fstd_id)
        self._fstd_id = None

    def to_csv(self, target, overwrite=False):
        with open(target, "a") as f:
            f.write(str(self))
