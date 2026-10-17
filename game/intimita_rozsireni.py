# game/intimita_rozsireni.py
"""Rozšířený systém intimních a erotických chvil v harému."""

from config import MAGENTA, NC, BOLD
from utils.vypis import clear, hlavicka, tisk_ok, tisk_chyba, tisk_info, vytiskni_volbu
from data.charaktery import CHARAKTERY, normalizuj_charakter

INTIMNI_AKTIVITY = {
    "lazne": {
        "nazev": "Společná lázeň s vonnými oleji",
        "cena_sex": 6,
        "cena_gold": 15,
        "min_duvera": 25,
        "popis": "Horká voda, mramorový bazén, omývání těla a uvolňující masáž ramen.",
        "efekt": {"touha": 12, "duvera": 8, "loajalita": 5, "hp": 15},
        "text_odmitnuti": "ještě se necítí dost uvolněná na to, aby s tebou sdílela lázeň.",
        "text_prijmuti": (
            "vstoupila s tebou do teplé vody. Pod tvými doteky její napětí polevilo "
            "a nechala tě vmasírovat vonný jasmínový olej do její pokožky."
        ),
    },
    "masaz": {
        "nazev": "Smyslná soukromá masáž v komnatách",
        "cena_sex": 8,
        "cena_gold": 0,
        "min_duvera": 35,
        "popis": "Tiché přítmí komnat, hedvábná prostěradla a doteky po celém těle.",
        "efekt": {"touha": 16, "duvera": 10, "submisivita": 6, "loajalita": 6},
        "text_odmitnuti": "se obává, že by masáž překročila její současné osobní hranice.",
        "text_prijmuti": (
            "se položila na hedvábné polštáře. Když tvé ruce klouzaly po jejích zádech a bocích, "
            "její dech ztěžkl a tiché povzdechy prozradily probouzející se vášeň."
        ),
    },
    "vino": {
        "nazev": "Večer při víně a svíčkách",
        "cena_sex": 5,
        "cena_gold": 25,
        "min_duvera": 20,
        "popis": "Sladké jižní víno, upřímný rozhovor z očí do očí a postupné sbližování.",
        "efekt": {"duvera": 12, "loajalita": 8, "touha": 8},
        "text_odmitnuti": "raději dnes zůstane ve svých komnatách o samotě.",
        "text_prijmuti": (
            "s tebou popíjela rubínové víno u praskajícího krbu. Při pohledu do tvých očí "
            "se jí tváře zbarvily do ruda a její ruka vyhledala tu tvou."
        ),
    },
    "noc_vasne": {
        "nazev": "Vášnivá noc plná odevzdání",
        "cena_sex": 14,
        "cena_gold": 0,
        "min_duvera": 55,
        "popis": "Hluboké spojení, intenzivní fyzická blízkost a úplná extáze bez zábran.",
        "efekt": {"touha": 25, "duvera": 15, "loajalita": 12, "submisivita": 10},
        "text_odmitnuti": "ještě k tobě necítí dost hlubokou důvěru pro takové intimní odevzdání.",
        "text_prijmuti": (
            "se ti v náručí plně odevzdala. Noc plná vášně, tichých výkřiků a tělesné extáze "
            "vás propojila víc než cokoliv předtím."
        ),
    },
    "tanec": {
        "nazev": "Soukromý svůdný tanec",
        "cena_sex": 7,
        "cena_gold": 20,
        "min_duvera": 30,
        "popis": "Tlumené svíce, hedvábné závoje a pomalý tanec jen pro tebe.",
        "efekt": {"touha": 18, "duvera": 7, "loajalita": 4},
        "text_odmitnuti": "dnes nemá náladu tančit před někým jiným než sama pro sebe.",
        "text_prijmuti": (
            "se začala pomalu pohybovat v rytmu tiché hudby. Závoje jí klouzaly po kůži, "
            "její pohled se tvého nepustil a vzduch v komnatě zhoustl napětím."
        ),
    },
    "svicky": {
        "nazev": "Koupel při svíčkách a polibky",
        "cena_sex": 9,
        "cena_gold": 10,
        "min_duvera": 45,
        "popis": "Voda zalitá světlem svíček, dlouhé polibky a něžné doteky.",
        "efekt": {"touha": 20, "duvera": 12, "loajalita": 8, "hp": 10},
        "text_odmitnuti": "by si pro takovou blízkost přála nejdřív více času a důvěry.",
        "text_prijmuti": (
            "se k tobě v teplé vodě přitiskla. Svíčky vrhaly zlaté odlesky na její ramena, "
            "a mezi polibky se tiše rozesmála, než se světlo zdálo ztlumit samo."
        ),
    },
    "ranni_probuzeni": {
        "nazev": "Líné ráno v posteli",
        "cena_sex": 10,
        "cena_gold": 0,
        "min_duvera": 60,
        "popis": "Pomalé probouzení, objetí pod přikrývkami a ráno, které se nechce končit.",
        "efekt": {"touha": 18, "duvera": 14, "loajalita": 10, "submisivita": 4},
        "text_odmitnuti": "si to zatím nedovede představit; potřebuje s tebou sdílet víc společných chvil.",
        "text_prijmuti": (
            "se ráno přitulila blíž a zašeptala, ať ještě nikam nechodíš. Mezi hedvábím "
            "a jejími doteky ztratil čas význam a závěsy zůstaly zatažené až do poledne."
        ),
    },
}

POVAHOVE_REAKCE = {
    "kurtizana": "Se sebejistým úsměvem sama určila tempo večera a ty ses jen poddal.",
    "nymfomanka": "Její dychtivost tě nechala bez dechu a každý dotek vracela s úrokem.",
    "umelkyne": "Po všem si tiše pobrukovala melodii, kterou večer inspiroval.",
    "diplomatka": "Mezi polibky vtipně vyjednávala, kdo smí rozhodnout o příští noci.",
    "amazonka": "Zpočátku se tě snažila přemoci, ale nakonec se nechala vést s hrdým smíchem.",
    "carodejka": "Nad postelí se vznášela světýlka, která vyčarovala sama od vzrušení.",
}


def nabidnout_intimni_chvili(hra, otrok):
    """Interaktivní menu pro výběr intimní aktivity s dívkou."""
    clear()
    hlavicka(f"Smyslné chvíle & Intimita: {otrok.jmeno}")
    print(
        f"Důvěra: {otrok.duvera}/100 | Touha: {otrok.touha}/100 | "
        f"Vztah: {otrok.romance_stav} ({otrok.romance_body}/100)"
    )
    print(f"Tvá sexuální energie: {hra.hrac.sex_energy} ⚡ | Zlato: {hra.hrac.gold} 🪙\n")

    if otrok.vek < 18:
        tisk_chyba("Intimní chvíle jsou vyhrazeny výhradně dospělým postavám.")
        input("Enter...")
        return False
    if otrok.na_najmu:
        tisk_chyba("Postava má aktivní pracovní závazek mimo panství.")
        input("Enter...")
        return False

    aktivity_seznam = list(INTIMNI_AKTIVITY.items())
    for idx, (klic, info) in enumerate(aktivity_seznam, 1):
        cena_str = f"{info['cena_sex']} ⚡ energie"
        if info["cena_gold"] > 0:
            cena_str += f", {info['cena_gold']} 🪙"
        print(f"  {BOLD}{idx}){NC} {BOLD}{info['nazev']}{NC} [{cena_str}]")
        print(f"      {info['popis']}")
        print(f"      Požadavek důvěry: min. {info['min_duvera']}")
    vytiskni_volbu("0", "Zpět")

    try:
        volba = input("> ").strip()
    except EOFError:
        return False

    if volba == "0" or not volba:
        return False

    try:
        idx_akt = int(volba) - 1
        if not (0 <= idx_akt < len(aktivity_seznam)):
            tisk_chyba("Neplatná volba.")
            input("Enter...")
            return False
    except ValueError:
        tisk_chyba("Zadej číslo.")
        input("Enter...")
        return False

    _, info = aktivity_seznam[idx_akt]

    # Ověření zdrojů
    if hra.hrac.sex_energy < info["cena_sex"]:
        tisk_chyba(f"Nemáš dost sexuální energie (potřebuješ {info['cena_sex']} ⚡).")
        input("Enter...")
        return False
    if hra.hrac.gold < info["cena_gold"]:
        tisk_chyba(f"Nemáš dost zlata (potřebuješ {info['cena_gold']} 🪙).")
        input("Enter...")
        return False

    # Ověření důvěry a souhlasu
    char_id = normalizuj_charakter(otrok.charakter)
    char_data = CHARAKTERY.get(char_id, {})
    reakce_mod = float(char_data.get("reakce_na_odmenu", 1.0))

    prah_duvery = info["min_duvera"]
    # Toužící a nymfomanka mají nižší práh pro vášeň
    if char_id in ("touha", "nymfomanka"):
        prah_duvery = max(10, prah_duvery - 15)
    elif char_id in ("vzdorna", "chladna"):
        prah_duvery += 10

    if otrok.duvera < prah_duvery:
        tisk_info(f"✦ {otrok.jmeno} {info['text_odmitnuti']}")
        otrok.zaznamenej_volbu("intimita_odmítnuto", info["nazev"], hra.hrac.den)
        input("Enter...")
        return False

    souhlas = input(
        f"Zeptat se {otrok.jmeno}, zda chce {info['nazev'].lower()}? (a/n): "
    ).strip().lower()
    if souhlas not in ("a", "ano"):
        otrok.zaznamenej_volbu(
            "intimita_odmítnuto", f"Odmítla: {info['nazev']}", hra.hrac.den
        )
        tisk_info(f"{otrok.jmeno} odmítla. Její rozhodnutí respektuješ.")
        input("Enter...")
        return False

    # Provedení
    hra.hrac.sex_energy -= info["cena_sex"]
    hra.hrac.gold -= info["cena_gold"]
    otrok.souhlas_romance = True

    # Aplikace efektů
    for stat, val in info["efekt"].items():
        skutecna_val = max(1, int(val * reakce_mod))
        otrok.zvysit_stat(stat, skutecna_val)

    otrok.romance_body = min(100, otrok.romance_body + int(8 * reakce_mod))
    if otrok.romance_body >= 75:
        otrok.romance_stav = "oddané partnerství"
    elif otrok.romance_body >= 40:
        otrok.romance_stav = "blízký vztah"

    otrok.zaznamenej_volbu("intimita", info["nazev"], hra.hrac.den)

    # Bonus pro hráče
    if hasattr(hra.hrac, "pridej_xp"):
        hra.hrac.pridej_xp(15)

    clear()
    hlavicka("Smyslné spojení")
    print(f"\n{MAGENTA}♥ {otrok.jmeno} {info['text_prijmuti']}{NC}\n")
    reakce = POVAHOVE_REAKCE.get(char_id)
    if reakce:
        print(f"{MAGENTA}{reakce}{NC}\n")
    tisk_ok(
        f"Vztah s {otrok.jmeno} se prohloubil! "
        f"Romance: {otrok.romance_body}/100 ({otrok.romance_stav}), "
        f"Touha: {otrok.touha}/100, Důvěra: {otrok.duvera}/100."
    )
    input("Enter...")
    return True
