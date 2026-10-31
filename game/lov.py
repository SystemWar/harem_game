"""Pátrání po dospělých dobrovolnicích a záchranné výpravy."""
import random
from models.otrokyne import Otrokyně
from data.jmena import vyber_nove_jmeno
from data.charaktery import nazev_charakteru, vyber_charakter
from utils.vypis import clear, nacti_volbu, tisk_ok, tisk_chyba, tisk_info
from config import RED, GREEN, CYAN, MAGENTA, GOLD, NC
from game.alchymie import SUROVINY

LOV_OBLASTI = [
    {
        "nazev": "Vesnice",
        "popis": "Místní dobrovolnice hledají bezpečné zázemí a nové příležitosti.",
        "sance": 0.7,
        "kvalita": (1, 3),
        "cena_energie": 10,
        "emodži": "🏡",
        "specialni_sance": 0.1
    },
    {
        "nazev": "Přístav",
        "popis": "Přístavní komunita propojuje cestovatelky s místními spojenci.",
        "sance": 0.55,
        "kvalita": (2, 5),
        "cena_energie": 20,
        "emodži": "⚓",
        "specialni_sance": 0.2
    },
    {
        "nazev": "Karavana",
        "popis": "Karavana veze zprávy o dospělých ženách hledajících nový domov.",
        "sance": 0.45,
        "kvalita": (3, 6),
        "cena_energie": 30,
        "emodži": "🐪",
        "specialni_sance": 0.25
    },
    {
        "nazev": "Šlechtické sídlo",
        "popis": "Ve šlechtickém sídle se hledají dobrovolnice pro společenské role.",
        "sance": 0.3,
        "kvalita": (5, 8),
        "cena_energie": 50,
        "emodži": "🏰",
        "specialni_sance": 0.4
    },
    {
        "nazev": "Banditský tábor",
        "popis": "Nebezpečný tábor může ukrývat lidi, kteří potřebují pomoc s odchodem.",
        "sance": 0.25,
        "kvalita": (2, 6),
        "cena_energie": 40,
        "emodži": "🏕️",
        "specialni_sance": 0.35
    },
    {
        "nazev": "Tržiště práce",
        "popis": "Dospělé uchazečky se samy hlásí na placené role v dominiu.",
        "sance": 0.65,
        "kvalita": (3, 7),
        "cena_energie": 35,
        "emodži": "🏪",
        "specialni_sance": 0.15
    },
    {
        "nazev": "Chrám temnoty",
        "popis": "Chrám hledá dospělé dobrovolnice pro bezpečný výzkum a zázemí.",
        "sance": 0.4,
        "kvalita": (4, 9),
        "cena_energie": 60,
        "emodži": "⛩️",
        "specialni_sance": 0.5
    },
    {
        "nazev": "Pohraniční osada",
        "popis": "Obyvatelky osady hledají ochranu před nájezdy a férovou práci.",
        "sance": 0.6,
        "kvalita": (2, 5),
        "cena_energie": 18,
        "emodži": "🛡️",
        "specialni_sance": 0.18,
    },
    {
        "nazev": "Tekno Party",
        "popis": "Hudebnice a pořadatelky se mohou dobrovolně přidat k tvé družině.",
        "sance": 0.65,
        "kvalita": (2, 6),
        "cena_energie": 20,
        "emodži": "🎛️",
        "specialni_sance": 0.22,
    },
]

TECHNIKY_LOVU = {
    "1": ("Průzkum a navázání kontaktu", 0.15, 0),
    "2": ("Vyjednat férovou nabídku (10 zl.)", 0.2, 10),
    "3": ("Zajistit doprovod oddílu (vyžaduje 2 vojáky)", 0.02, 0),
}

SPECIALNI_UDALOSTI_LOV = [
    {
        "nazev": "Poklad",
        "popis": "Našel jsi truhlu se zlaťáky.",
        "efekt": lambda h: setattr(h, 'gold', h.gold + random.randint(20, 80))
    },
    {
        "nazev": "Surovina",
        "popis": "Našel jsi vzácnou surovinu.",
        "efekt": lambda h, alchymie: alchymie.pridat_surovinu(random.choice(list(SUROVINY.keys())), 1) if alchymie else None
    },
    {
        "nazev": "Přepadení",
        "popis": "Byli jste přepadeni!",
        "efekt": lambda h: (setattr(h, 'hp', max(1, h.hp - random.randint(5, 20))), setattr(h, 'gold', max(0, h.gold - random.randint(10, 40))))
    },
    {
        "nazev": "Inkvizice",
        "popis": "Inkvizice vás zahlédla.",
        "efekt": lambda h: setattr(h, 'vliv_inkvizice', min(100, h.vliv_inkvizice + random.randint(2, 8)))
    },
]

def lov_otrokyn(hra):
    hrac = hra.hrac
    clear()
    print(f"{GOLD}{'='*50}{NC}")
    print(f"{MAGENTA}🧭 PÁTRÁNÍ A DOBROVOLNÝ NÁBOR{NC}")
    print(f"{GOLD}{'='*50}{NC}\n")

    if hrac.sex_energy < 10:
        tisk_chyba("Nemáš dostatek energie na lov (min. 10).")
        input("Enter...")
        return None

    print("Vyber oblast lovu:\n")
    for i, oblast in enumerate(LOV_OBLASTI, 1):
        print(f"{i}) {oblast['emodži']} {oblast['nazev']} - {oblast['popis']}")
        print(f"   Šance: {int(oblast['sance']*100)}% | Kvalita: {oblast['kvalita'][0]}-{oblast['kvalita'][1]} | Energie: {oblast['cena_energie']} | Zvláštní událost: {int(oblast['specialni_sance']*100)}%\n")

    try:
        volba = nacti_volbu(
            {"0", *(str(index) for index in range(1, len(LOV_OBLASTI) + 1))},
            chybova_zprava="Neplatná volba. Zadej číslo oblasti nebo 0 pro návrat.",
        )
    except EOFError:
        return None
    if volba == "0":
        return None

    idx = int(volba) - 1
    oblast = LOV_OBLASTI[idx]
    if hrac.sex_energy < oblast["cena_energie"]:
        tisk_chyba(f"Nedostatek energie. Potřebuješ {oblast['cena_energie']}.")
        input("Enter...")
        return None

    print(f"\nZvol techniku pro oblast {oblast['emodži']} {oblast['nazev']}:")
    for ident, (nazev, _, _) in TECHNIKY_LOVU.items():
        print(f"{ident}) {nazev}")
    try:
        technika = nacti_volbu(
            {"0", *TECHNIKY_LOVU},
            chybova_zprava="Neplatná technika. Vyber 1–3 nebo 0 pro návrat.",
        )
    except EOFError:
        return None
    if technika == "0":
        return None
    bonus, cena = TECHNIKY_LOVU[technika][1:]
    if technika == "3" and hra.mafie.vojaci < 2:
        tisk_chyba("Doprovod vyžaduje alespoň dva vojáky.")
        return None
    if hrac.gold < cena:
        tisk_chyba("Na férovou nabídku nemáš dost zlata.")
        return None

    hrac.sex_energy -= oblast["cena_energie"]
    hrac.gold -= cena
    if technika == "3":
        bonus *= min(10, hra.mafie.vojaci)
    print(
        f"\nVydáváš se do oblasti {oblast['emodži']} {oblast['nazev']} "
        f"technikou: {TECHNIKY_LOVU[technika][0]}..."
    )

    if random.random() < oblast["specialni_sance"]:
        udalost = random.choice(SPECIALNI_UDALOSTI_LOV)
        print(f"\n⭐ {udalost['popis']}")
        if udalost["nazev"] == "Surovina":
            udalost["efekt"](hrac, hra.alchymie)
        else:
            udalost["efekt"](hrac)
        input("Enter...")

    sance = min(0.9, oblast["sance"] + bonus)
    if random.random() < sance:
        kvalita = random.randint(*oblast["kvalita"])
        jmeno = vyber_nove_jmeno(hra.harem.otrokyne)
        charakter = vyber_charakter()
        otrok = Otrokyně(
            jmeno=jmeno,
            srdce=min(100, random.randint(40, 90) + kvalita * 5),
            poslusnost=min(100, random.randint(10, 70) + kvalita * 4),
            submisivita=min(100, random.randint(10, 75) + kvalita * 5),
            loajalita=min(100, random.randint(5, 60) + kvalita * 3),
            touha=min(100, random.randint(15, 80) + kvalita * 4),
            broken=0,
            hp=random.randint(70, 100),
            charakter=charakter,
            vek=random.randint(20, 35),
        )
        hrac.gold += random.randint(10, 50)
        print(
            f"\n✅ {tisk_ok(f'{jmeno}, dospělá dobrovolnice, přijala nabídku a přidá se k dominiu.')}"
        )
        print(f"   Charakter: {nazev_charakteru(charakter)}")
        print(f"   Vlastnosti: důvěra {otrok.duvera}, loajalita {otrok.loajalita}")
        return otrok
    else:
        print(f"\n❌ {tisk_chyba('Pátrání nikoho nezastihlo. Zkus jinou oblast nebo techniku.')}")
        return None


ZACHRANNE_LOKACE = {
    "les": "Mlžném lese",
    "paserska_zatoka": "Pašerácké zátoce",
    "severni_hradby": "Severních hradbách",
    "dymova_ctvrt": "Dýmové čtvrti",
    "tekno_party": "okolí Tekno Party",
}


def proved_zachranne_patranie(hra, lokace_id, technika, rng=None):
    """Vyhledá lidi v nouzi a doprovodí je do bezpečí; nikoho nepřijímá do harému."""
    if lokace_id not in ZACHRANNE_LOKACE or technika not in TECHNIKY_LOVU:
        return False
    den = max(0, int(hra.hrac.den))
    if not hra.svet.lokacni_odmena_dostupna(lokace_id, "patrani_zachrana", den):
        tisk_info("Záchranné pátrání v této oblasti už dnes proběhlo.")
        return False

    bonus, cena = TECHNIKY_LOVU[technika][1:]
    if technika == "1":
        if hra.hrac.sex_energy < 5 and hra.hrac.dark_energy < 5:
            tisk_chyba("Průzkum vyžaduje 5 bodů sexuální nebo temné energie.")
            return False
        if hra.hrac.sex_energy >= 5:
            hra.hrac.sex_energy -= 5
        else:
            hra.hrac.dark_energy -= 5
    elif technika == "2":
        if hra.hrac.gold < 15:
            tisk_chyba("Na domluvu s místními kontakty potřebuješ 15 zlata.")
            return False
        hra.hrac.gold -= 15
    else:
        vojaci = max(0, int(hra.mafie.vojaci))
        if vojaci < 2:
            tisk_chyba("Doprovod vyžaduje alespoň dva vojáky.")
            return False
        bonus *= min(10, vojaci)

    hra.svet.zaznamenej_lokacni_odmenu(lokace_id, "patrani_zachrana", den)
    generator = rng or random
    sance = min(0.9, 0.55 + bonus + hra.hrac.skilly.get("vyjednavani", 0) * 0.01)
    if generator.random() >= sance:
        tisk_info("Pátrání dnes nikoho nenašlo; místní kontakty zůstávají otevřené.")
        return False

    hra.hrac.gold += 25
    hra.hrac.reputace_mesta = min(100, hra.hrac.reputace_mesta + 2)
    mesto_id = "vychodni_brod" if lokace_id == "severni_hradby" else "stare_mesto"
    hra.zivy_svet.mesta[mesto_id].uprav(bezpeci=2, stabilita=1)
    for frakce_id in ("systemaci", "narkomani"):
        frakce = hra.frakce.frakce.get(frakce_id)
        if frakce:
            frakce.zmenit(2)
    tisk_ok(
        f"V oblasti {ZACHRANNE_LOKACE[lokace_id]} se podařilo najít lidi "
        "v nouzi a bezpečně je doprovodit. Reputace +2, odměna +25 zl."
    )
    return True


def menu_zachranneho_patrani(hra, lokace_id):
    if lokace_id not in ZACHRANNE_LOKACE:
        return False
    print(f"\nPátrání v oblasti: {ZACHRANNE_LOKACE[lokace_id]}")
    for ident, (nazev, _, _) in TECHNIKY_LOVU.items():
        print(f"{ident}) {nazev}")
    print("0) Zpět")
    try:
        volba = input("> ").strip()
    except EOFError:
        return False
    if volba == "0":
        return False
    if volba not in TECHNIKY_LOVU:
        tisk_chyba("Neplatná technika pátrání.")
        return False
    return proved_zachranne_patranie(hra, lokace_id, volba)
