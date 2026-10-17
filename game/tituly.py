"""Hodnosti pána harému. Skládají se z arény, pevnosti a reputace města."""

TITULY = (
    {
        "id": "neznamy",
        "poradi": 0,
        "nazev": "Neznámý pán",
        "arena": 0,
        "pevnost": 1,
        "reputace": -999,
        "dan": 0.0,
        "vztah": 0,
    },
    {
        "id": "strazce_dvora",
        "poradi": 1,
        "nazev": "Strážce dvora",
        "arena": 1,
        "pevnost": 1,
        "reputace": 0,
        "dan": 0.05,
        "vztah": 1,
    },
    {
        "id": "pan_cerne_areny",
        "poradi": 2,
        "nazev": "Pán Černé arény",
        "arena": 3,
        "pevnost": 2,
        "reputace": 8,
        "dan": 0.10,
        "vztah": 2,
    },
    {
        "id": "pan_stinu",
        "poradi": 3,
        "nazev": "Pán stínů",
        "arena": 5,
        "pevnost": 3,
        "reputace": 15,
        "dan": 0.18,
        "vztah": 3,
    },
)


def _stav(hra):
    return (
        getattr(getattr(hra, "pevnost", None), "arena_rank", 0),
        getattr(getattr(hra, "pevnost", None), "uroven", 1),
        getattr(getattr(hra, "hrac", None), "reputace_mesta", 0),
    )


def hodnost(hra):
    """Nejvyšší titul, jehož prahy hráč právě splňuje."""
    arena, pevnost, reputace = _stav(hra)
    aktualni = TITULY[0]
    for titul in TITULY:
        if (
            arena >= titul["arena"]
            and pevnost >= titul["pevnost"]
            and reputace >= titul["reputace"]
        ):
            aktualni = titul
    return aktualni


def dalsi_titul(hra):
    poradi = hodnost(hra)["poradi"] + 1
    return next((titul for titul in TITULY if titul["poradi"] == poradi), None)


def uprav_dan(zaklad, hra):
    """Vrátí daň po bonusu hodnosti. Neznámý pán nic nemění."""
    return int(zaklad * (1 + hodnost(hra)["dan"]))


def sance_vyzvy(hra):
    """Čím vyšší hodnost, tím míň se někdo odváží útočit nebo vyzývat."""
    return max(1, 4 - hodnost(hra)["poradi"])


def zaznamenej_povyseni(hra):
    """Při postupu jednorázově zlepší vztahy s NPC. Opakované volání nic nepřidá.

    Uložený titul je nejvyšší dosažená hodnost. Pokles a návrat bonus znovu nedá.
    """
    titul = hodnost(hra)
    posledni = getattr(hra.hrac, "titul_mesta", "")
    stary = next((item for item in TITULY if item["nazev"] == posledni), TITULY[0])
    if titul["poradi"] <= stary["poradi"]:
        return None
    hra.hrac.titul_mesta = titul["nazev"]
    delta = titul["vztah"] - stary["vztah"]
    svet = getattr(hra, "svet", None)
    if delta > 0 and svet is not None and hasattr(svet, "zmen_vztah"):
        for npc_id in list(getattr(svet, "vztahy_npc", {})):
            svet.zmen_vztah(npc_id, delta)
    return titul
