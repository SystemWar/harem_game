"""Malé deterministické stavební bloky pro rozhodování herních agentů."""

from collections import deque
from math import isfinite


def vyber_nejlepsi_uzitek(kandidati):
    """Vrátí identifikátor kandidáta s nejvyšším skóre; při shodě drží pořadí."""
    nejlepsi = None
    nejlepsi_skore = float("-inf")
    for ident, skore in kandidati:
        try:
            hodnota = float(skore)
        except (TypeError, ValueError):
            continue
        if not isfinite(hodnota):
            continue
        if nejlepsi is None or hodnota > nejlepsi_skore:
            nejlepsi = ident
            nejlepsi_skore = hodnota
    return nejlepsi


def vzdalenosti_od_cilu(graf, cile):
    """Vrátí nejkratší vzdálenost každého dosažitelného uzlu od sady cílů."""
    vzdalenosti = {}
    fronta = deque()
    for cil in cile:
        if cil in graf and cil not in vzdalenosti:
            vzdalenosti[cil] = 0
            fronta.append(cil)
    while fronta:
        aktualni = fronta.popleft()
        for soused in graf.get(aktualni, ()):
            if soused not in vzdalenosti:
                vzdalenosti[soused] = vzdalenosti[aktualni] + 1
                fronta.append(soused)
    return vzdalenosti
