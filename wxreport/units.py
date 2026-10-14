"""Display conversions. Sources are metric; US claim files read imperial. Raw values stay in the snapshot."""


def f(c):
    return None if c is None else c * 9 / 5 + 32


def mph(ms):
    return None if ms is None else ms * 2.236936


def kt(ms):
    return None if ms is None else ms * 1.943844


def inch(mm):
    return None if mm is None else mm / 25.4


def mi(km):
    return None if km is None else km * 0.621371


def fmt(v, digits=1, unit="", missing="—"):
    if v is None:
        return missing
    return f"{v:.{digits}f}{(' ' + unit) if unit else ''}"


def fmt_precip_in(mm, trace=False, missing="—"):
    """Inches to hundredths; a measured trace or positive amount under 0.005 in prints as '<0.01'."""
    if mm is None:
        return missing
    v = mm / 25.4
    if (v > 0 and v < 0.005) or (v == 0 and trace):
        return "<0.01"
    return f"{v:.2f}"
