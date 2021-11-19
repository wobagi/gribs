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