#!/usr/bin/env python3

import os
import sys
import pathlib
import argparse
import numpy as np
import fstd2nc
import rpnpy.librmn.all as rmn
from eccodes import GribFile, GribMessage

CONVIP_STYLE_NEW = 2

class Unit():
    """
    Simple unit conversion functions.
    Use pint or other fully fledged lib
    in case more comprehensive conversions are needed.
    """
    @staticmethod
    def ident(value):
        return value

    @staticmethod
    def m_per_s_to_kt(value):
        return value * 1.9438

    @staticmethod
    def K_to_C(value):
        return value - 273.15

    @staticmethod
    def m_to_cm(value):
        return value * 100

    @staticmethod
    def gpm_to_dam(value):
        return value * 0.1

    @staticmethod
    def Pa_to_hPa(value):
        return value * 0.01



class GribMapper():
    IP1_FROM_LEVEL = -1
    NBITS_WRITE = -32  # 

    VARS = {
        "Albedo":
        {
            "nomvar": {0: "AL"}
        },
        "Cloud water":
        {
            "nomvar": "QC"
        },
        "Geopotential Height":
        {
            "nomvar": "GZ",
            "unit": Unit.gpm_to_dam
        },
        "Land-sea mask":
        {
            "nomvar": {0: "MQ"}
        },
        "Orography":  # REAL [m2/s2] --> gpm (geopotential metres)
        {
            "nomvar": {0: "MX"}
        },
        "Pressure reduced to MSL":
        {
            "nomvar": "PN",
            "unit": Unit.Pa_to_hPa
        },
        "Sea ice area fraction":
        {
            "nomvar": {0: "LG"}
        },
        "Sea surface temperature":
        {
            "nomvar": "TM"
        },
        "Skin temperature":
        {
            "nomvar": {0: "TS"},
            "unit": Unit.K_to_C
        },
        "Snow density":
        {
            "nomvar": "DN"
        },
        "Snow depth":
        {
            "nomvar": "SD",
            "unit": Unit.m_to_cm
        },
        "Soil moisture content":
        {
            "nomvar": {0: "HS", 10: "I1", 100: "I1"},
            "ip1": {10: "", 100: ""}
        },
        "Soil Temperature":
        {
            "nomvar": {0: "TP", 100: "I0"},
            "unit": Unit.K_to_C,
            "ip1": {100: 1198}
        },
        "Specific humidity":
        {
            "nomvar": "HU",
        },
        "Surface pressure":
        {
            "nomvar": "P0",
            "unit": Unit.Pa_to_hPa
        },
        "Temperature":
        {
            "nomvar": "TT",
            "unit": Unit.K_to_C
        },
        "U component of wind":
        {
            "nomvar": "UU",
            "unit": Unit.m_per_s_to_kt
        },
        "V component of wind":
        {
            "nomvar": "VV",
            "unit": Unit.m_per_s_to_kt
        },
        "Volumetric soil ice":
        {
            "nomvar": {0: "I2"}  # kg/m2 ?
        }
    }


    def __init__(self, grib):
        self._msg = GribMessage(grib)
        self._level = self._msg["level"]
        self._name = self._msg["name"]

        try:
            self._var = self.VAR[self._name]
        except KeyError:
            raise KeyError(f"No such field in the dictionary: {self._name}")

        self._fstd_id = None
        self._etiket = "G0928V3N"

    def has_grid(self):
        return self._msg["gridDescriptionSectionPresent"] == 1

    def is_latlon(self):
        return self._msg["gridDefinitionDescription"] == "Latitude/longitude "

    def is_valid_level(self):
        return self._msg["typeOfLevel"] in ("isobaricInhPa", "meanSea", "surface")

    def is_convertable(self):
        return self.has_grid() and self.is_latlon()

    def _unit_conversion(self, value):
        try:
            return self._var["unit"](value)
        except:
            return value

    @property
    def level(self):
        return self._level

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
    def _dlon(self):
        return self._msg["iDirectionIncrementInDegrees"]

    @property
    def _dlat(self):
        return self._msg["jDirectionIncrementInDegrees"]

    @property
    def name(self):
        return self._name

    @property
    def data(self):
        field = self._msg["values"]
        values = self._unit_conversion(field)
        d64 = np.reshape(values, (self.ni, self.nj), order='F')
        return np.float32(d64)

    @property
    def nomvar(self):
        try:
            nv = self._var["nomvar"][self._level]
        except:
            nv = self._var["nomvar"][0]
        return f"{nv:<4}"

    def get_fstd_grid_meta(self):
        grtyp = 'L'
        (ig1, ig2, ig3, ig4) = rmn.cxgaig(grtyp, self._lat_zero, self._lon_zero, self._dlat, self._dlon)
        gid = rmn.ezqkdef(self.ni, self.nj, grtyp, ig1, ig2, ig3, ig4)
        return rmn.ezgprm(gid)

    @property
    def ip1(self):
        try:
            var_ip1 = self._var["ip1"][self._level]
        except:
            var_ip1 = rmn.convertIp(CONVIP_STYLE_NEW, self._level, 1)
        return var_ip1

    def fstd_meta(self):
        params = self.get_fstd_grid_meta()
        date_valid = self._msg["validityDate"]
        time_valid = self._msg["validityTime"]
        hour_forec = self._msg["forecastTime"]
        params["dtype"] = 1
        params["shape"] = (self.ni, self.nj, 1)
        params["dateo"] = rmn.newdate(3, date_valid, time_valid) - 3600 * hour_forec
        params["datev"] = rmn.newdate(3, date_valid, time_valid)
        params["deet"] = 3600
        params["npas"] = hour_forec
        params["nbits"] = self._msg["bitsPerValue"]  # shouldn't it be -32 ?
        params["datyp"] = 1  # 5 ?

        rp1a = rmn.FLOAT_IP(self.level, self.level, rmn.LEVEL_KIND_PMB)
        rp2a = rmn.FLOAT_IP(hour_forec, hour_forec, rmn.TIME_KIND_HR)
        rp3a = rmn.FLOAT_IP(0., 0., rmn.KIND_ARBITRARY)
        (ip1, ip2, ip3) = rmn.EncodeIp(rp1a, rp2a, rp3a)           
        params["ip1"] = ip1
        params["ip2"] = ip2
        params["ip3"] = ip3
        params["typvar"] = "P "
        params["nomvar"] = self.nomvar
        params["etiket"] = f"{self._etiket:<12}"
        params["d"] = self.data
        return params

    def _init_fstd_file(self, target, overwrite):
        if target.exists():
            if overwrite:
                target.unlink()
            else:
                raise FileExistsError("The target already exists. Use -o/--overwrite option to overwrite.")
        rmn.fstopt(rmn.FSTOP_MSGLVL, rmn.FSTOPI_MSG_CATAST)
        rmn.fstopt(rmn.FSTOP_TOLRNC, rmn.FSTOPI_MSG_CATAST)
        self._fstd_id = rmn.fstopenall(str(target), rmn.FST_RW)
        return self._fstd_id

    def to_rpn(self, target, overwrite=False):
        self._fstd_id = self._init_fstd_file(target, overwrite)
        try:
            rmn.fstecr(iunit=self._fstd_id, data=self.data, meta=self.fstd_meta(), rewrite=False)
        except rmn.FSTDError:
            raise IOError("Problem writing rpn record")

    def __del__(self):
        if self._fstd_id:
            rmn.fstcloseall()

def cli():
    parser = argparse.ArgumentParser(description="Convert grib files to rpn format")
    parser.add_argument("--source", "-s", type=pathlib.Path, required=True, help="Source directory")
    parser.add_argument("--target", "-t", type=pathlib.Path, required=True, help="Target rpn file")
    parser.add_argument("-o", "--overwrite", action="store_true", help="Overwrite target if exists")
    parser.add_argument("-p", "--progress", action="store_true", help="Show progress bar")
    parser.add_argument("-c", "--color", action="store_true", help="Use output coloring")
    args = parser.parse_args()

    gf = GribFile(args.source)
    gm = GribRPNMapper(gf)
    gm.to_rpn(target=args.target, overwrite=args.overwrite)

if __name__=="__main__":
    cli()
