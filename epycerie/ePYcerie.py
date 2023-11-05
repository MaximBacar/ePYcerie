from connectors.maxi_connector      import Maxi
from connectors.iga_connector       import IGA
from connectors.jeancoutu_connector import JeanCoutu
from connectors.metro_connector     import Metro
from connectors.superc_connector    import SuperC



flyers = {
    "MAXI"      : Maxi.flyer,
    "IGA"       : IGA.flyer,
    "METRO"     : Metro.flyer,
    "SUPERC"    : SuperC.flyer
}

def extract_flyer( store : str, to_csv : bool = False, to_excel : bool = False):
    if store.upper in flyers:
        print(flyers[store.upper]())
    else:
        print("Invalid store")


extract_flyer("MAXI")