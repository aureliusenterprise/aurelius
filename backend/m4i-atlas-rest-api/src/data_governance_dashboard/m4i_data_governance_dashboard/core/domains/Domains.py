from enum import Enum, unique


@unique
class Domains(Enum):
    """
    Mapping for Domains in a Program
    """
    sur = "Survey"
    trea = "Treasury"
    supp = "Supplier and Procurement"
    stm = "Strategy and Markets"
    smd = "Ship Management"
    qhse = "QHSE"
    psc = "Procurement and Supply Chain"
    prof = "Project Office"
    po = "Personnel and Organization"
    ld = "Legal"
    it = "Information Technology"
    fs = "Facility Services"
    fc = "Finance and Control"
    ee = "Engineering and Estimating"
    cor = "Corporate Affairs"
    comm = "Communication"
    com = "Executive Commitee"

# END DataDomains
