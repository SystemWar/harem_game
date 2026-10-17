# game/interakce.py
import random
from data.interakce import INTERAKCE
from data.charaktery import CHARAKTERY, nazev_charakteru
from utils.vypis import hlavicka, clear, tisk_ok, tisk_chyba, tisk_info, vytiskni_volbu
from models.otrokyne import Otrokyně
from models.hrac import Hrac

NAZVY_STATISTIK = {
    "duvera": "důvěra",
    "loajalita": "loajalita",
    "touha": "touha",
    "submisivita": "submisivita",
    "poslusnost": "poslušnost",
    "strach": "strach",
    "hp": "zdraví",
    "vlhkost": "smyslnost",
    "broken": "zlomení",
    "mindbreak": "psychika",
    "humiliation": "ponížení",
    "scarred": "jizvy",
    "pain_addiction": "odolnost vůči bolesti",
    "owned_mark": "znamení",
    "zavislost": "závislost",
}

KATEGORIE_PODLE_TYPU = {
    "odmena": "Péče a rozhovor",
    "trest": "Výcvik a disciplína",
    "neutralni": "Zkoušky a rituály",
}
PORADI_KATEGORII = (
    "Péče a rozhovor",
    "Společný čas",
    "Blízkost",
    "Výcvik a disciplína",
    "Zkoušky a rituály",
)


def _kategorie(akce):
    return akce.get("kategorie") or KATEGORIE_PODLE_TYPU.get(
        akce.get("typ"), "Ostatní"
    )


def _popis_akce(akce):
    efekty = ", ".join(
        f"{NAZVY_STATISTIK.get(stat, stat)} {hodnota:+g}"
        for stat, hodnota in akce.get("efekty", {}).items()
    )
    cena = (
        f"Energie {akce.get('cena_energie', 0)}"
        f" | Temná energie {akce.get('cena_temnoty', 0)}"
    )
    podminky = []
    if akce.get("intimni"):
        podminky.append(f"důvěra {akce.get('min_duvera', 0)}+")
        podminky.append("dospělá postava, její souhlas")
    riziko = akce.get("riziko", 0)
    if riziko:
        podminky.append(f"riziko {riziko:.0%}")
    if akce.get("popis"):
        print(f"   {akce['popis']}")
    print(f"   Účinky: {efekty or 'bez přímé změny statistik'}")
    print(f"   Cena: {cena}")
    if podminky:
        print(f"   Podmínky: {', '.join(podminky)}")


def proved_interakci(otrok: Otrokyně, hrac: Hrac, akce_id: str):
    akce = next((a for a in INTERAKCE if a["id"] == akce_id), None)
    if not akce:
        tisk_chyba("Neznámá akce.")
        return False

    if getattr(otrok, "na_najmu", False):
        tisk_chyba("Interakce s ní počkají, dokud neskončí její pracovní závazek.")
        return False

    if hrac.sex_energy < akce.get("cena_energie", 0):
        tisk_chyba("Nedostatek sexuální energie.")
        return False
    if hrac.dark_energy < akce.get("cena_temnoty", 0):
        tisk_chyba("Nedostatek temné energie.")
        return False

    if akce.get("intimni"):
        if getattr(otrok, "vek", 0) < 18:
            tisk_chyba("Intimní interakce jsou dostupné pouze dospělým postavám.")
            return False
        min_duvera = akce.get("min_duvera", 0)
        if getattr(otrok, "duvera", 0) < min_duvera:
            tisk_info(
                f"{otrok.jmeno} zatím nemá dost důvěry pro tuto blízkost "
                f"(potřebuje {min_duvera}/100)."
            )
            otrok.zaznamenej_volbu(
                "intimita_odmítnuto", akce["nazev"], getattr(hrac, "den", 0)
            )
            return False
        souhlas = input(
            f"Zeptat se {otrok.jmeno}, zda s tím souhlasí? (a/n): "
        ).strip().lower()
        if souhlas not in ("a", "ano"):
            otrok.zaznamenej_volbu(
                "intimita_odmítnuto", f"Odmítla: {akce['nazev']}",
                getattr(hrac, "den", 0),
            )
            tisk_info(f"{otrok.jmeno} odmítla. Její rozhodnutí respektuješ.")
            return False

    hrac.sex_energy -= akce.get("cena_energie", 0)
    hrac.dark_energy -= akce.get("cena_temnoty", 0)

    charakter_data = CHARAKTERY.get(otrok.charakter, CHARAKTERY["subka"])
    mod = charakter_data.get("modifikatory", {})

    for stat, hodnota in akce["efekty"].items():
        mod_hodnota = int(hodnota * mod.get(stat, 1.0))
        otrok.zvysit_stat(stat, mod_hodnota)

    if akce.get("typ") == "trest":
        otrok.zvysit_stat("submisivita", int(3 * charakter_data.get("reakce_na_trest", 1.0)))
        otrok.zvysit_stat("strach", int(2 * charakter_data.get("reakce_na_trest", 1.0)))
    elif akce.get("typ") == "odmena":
        otrok.zvysit_stat("loajalita", int(2 * charakter_data.get("reakce_na_odmenu", 1.0)))
        otrok.zvysit_stat("duvera", int(2 * charakter_data.get("reakce_na_odmenu", 1.0)))

    if otrok.charakter in ["vzdorna", "odvazna"]:
        if random.random() < charakter_data.get("utek_sance", 0.1):
            tisk_chyba(f"{otrok.jmeno} se pokusila o útěk!")
            return False

    if "vliv_inkvizice" in akce:
        hrac.vliv_inkvizice = min(100, hrac.vliv_inkvizice + akce["vliv_inkvizice"])

    if random.random() < akce.get("riziko", 0):
        otrok.zvysit_stat("hp", -random.randint(1, 10))
        tisk_chyba("Stala se nepříjemná událost!")

    otrok.aktualizuj_fazi()
    otrok.zaznamenej_volbu(
        "interakce", akce["nazev"], getattr(hrac, "den", 0)
    )
    tisk_ok(f"Provedeno: {akce['nazev']} (charakter: {nazev_charakteru(getattr(otrok, 'charakter', 'subka'))})")
    try:
        from game.ai_dialog import vypis_dialog, typ_z_akce
        nast = getattr(hrac, "_nastaveni_ref", None)
        vypis_dialog(otrok, hrac, typ_z_akce(akce), nastaveni=nast)
    except Exception:
        pass
    return True

def zobraz_interakce(otrok, hrac, nastaveni=None):
    from game.tresty_odmeny import menu_trestu, menu_odmen
    from game.drogy import menu_drog
    if nastaveni is not None:
        hrac._nastaveni_ref = nastaveni
    while True:
        clear()
        hlavicka(f'Interakce s {otrok.jmeno}')
        print(
            f"HP: {otrok.hp} | Důvěra: {otrok.duvera} | "
            f"Loajalita: {otrok.loajalita} | Touha: {otrok.touha}"
        )
        print(f"Energie: {hrac.sex_energy} | Temná energie: {hrac.dark_energy}")
        if getattr(otrok, "na_najmu", False):
            print("\nTato postava má pracovní závazek; osobní interakce zatím nejsou dostupné.")
        dostupne = [
            akce for akce in INTERAKCE
            if not getattr(otrok, "na_najmu", False)
            and (
                not akce.get("intimni")
                or getattr(otrok, "vek", 0) >= 18
            )
        ]
        skupiny = {}
        for akce in dostupne:
            skupiny.setdefault(_kategorie(akce), []).append(akce)
        skupiny = dict(sorted(
            skupiny.items(),
            key=lambda item: (
                PORADI_KATEGORII.index(item[0])
                if item[0] in PORADI_KATEGORII
                else len(PORADI_KATEGORII)
            ),
        ))
        nazvy_skupin = list(skupiny)
        if not getattr(otrok, "na_najmu", False):
            print("\nKategorie interakcí:")
            for index, nazev in enumerate(nazvy_skupin, 1):
                print(f"{index}) {nazev} ({len(skupiny[nazev]}) možností)")
        vytiskni_volbu('97', 'Bojová společnice (doprovod do arény a dungeonů)')
        vytiskni_volbu('98', 'Drogy')
        vytiskni_volbu('99', 'Tresty/odměny')
        vytiskni_volbu('0', 'Zpět')
        try:
            volba = input("> ").strip()
        except EOFError:
            return
        if volba == "0":
            break
        elif volba == "97":
            hra = getattr(hrac, "_hra_ref", None)
            pevnost = getattr(hra, "pevnost", None) if hra else None
            if pevnost:
                if getattr(pevnost, "bojova_partnerka", "") == otrok.jmeno:
                    pevnost.bojova_partnerka = ""
                    tisk_ok(f"{otrok.jmeno} již není tvou aktivní bojovou společnicí.")
                else:
                    pevnost.bojova_partnerka = otrok.jmeno
                    otrok.zvysit_stat("loajalita", 3)
                    tisk_ok(f"★ {otrok.jmeno} byla zvolena jako tvá bojová společnice!")
            else:
                tisk_info(f"{otrok.jmeno} je připravena bojovat po tvém boku (zvolena v aréně).")
            input("Enter...")
        elif volba == "98":
            menu_drog(otrok, hrac)
        elif volba == "99":
            while True:
                clear()
                hlavicka(f'Tresty / Odměny pro {otrok.jmeno}')
                vytiskni_volbu('1', 'Tresty')
                vytiskni_volbu('2', 'Odměny')
                vytiskni_volbu('0', 'Zpět')
                volba2 = input("> ")
                if volba2 == "1":
                    menu_trestu(otrok, hrac)
                elif volba2 == "2":
                    menu_odmen(otrok, hrac)
                elif volba2 == "0":
                    break
        else:
            try:
                idx = int(volba) - 1
                if not 0 <= idx < len(nazvy_skupin):
                    tisk_chyba("Špatná volba.")
                    input("Enter...")
                    continue
                kategorie = nazvy_skupin[idx]
                akce_v_kategorii = skupiny[kategorie]
                while True:
                    clear()
                    hlavicka(f"{kategorie}: {otrok.jmeno}")
                    for index, akce in enumerate(akce_v_kategorii, 1):
                        print(f"{index}) {akce['nazev']}")
                        _popis_akce(akce)
                    vytiskni_volbu("0", "Zpět do kategorií")
                    try:
                        vyber_akce = input("> ").strip()
                    except EOFError:
                        return
                    if vyber_akce == "0":
                        break
                    try:
                        index_akce = int(vyber_akce) - 1
                    except ValueError:
                        tisk_chyba("Zadej číslo akce.")
                        input("Enter...")
                        continue
                    if not 0 <= index_akce < len(akce_v_kategorii):
                        tisk_chyba("Špatná volba.")
                        input("Enter...")
                        continue
                    proved_interakci(otrok, hrac, akce_v_kategorii[index_akce]["id"])
                    input("Enter...")
            except ValueError:
                tisk_chyba("Zadej číslo.")
                input("Enter...")

def zobraz_hromadne_interakce(otrokyne, hrac):
    """Provede stejnou bezpečnou interakci na všech vybraných postavách."""
    cilove_postavy = [
        otrok for otrok in otrokyne
        if not getattr(otrok, "na_najmu", False) and getattr(otrok, "hp", 0) > 0
    ]
    if not cilove_postavy:
        tisk_chyba("Nemáš žádné aktivní postavy.")
        return

    while True:
        clear()
        hlavicka('Hromadná interakce se všemi otrokyněmi')
        print(f"Počet způsobilých postav: {len(cilove_postavy)}")
        vynechano = len(otrokyne) - len(cilove_postavy)
        if vynechano:
            print(f"Postavy na nájmu nebo mimo provoz budou vynechány: {vynechano}.")
        dostupne = [akce for akce in INTERAKCE if not akce.get("intimni")]
        for i, akce in enumerate(dostupne, 1):
            print(
                f"{i}) {akce['nazev']} "
                f"(E:{akce.get('cena_energie', 0)} "
                f"T:{akce.get('cena_temnoty', 0)} za osobu)"
            )
        vytiskni_volbu('0', 'Zpět')
        volba = input("> ").strip()
        if volba == "0":
            return
        try:
            index = int(volba) - 1
        except ValueError:
            tisk_chyba("Zadej číslo.")
            input("Enter...")
            continue
        if not 0 <= index < len(dostupne):
            tisk_chyba("Špatná volba.")
            input("Enter...")
            continue

        akce = dostupne[index]
        cena_energie = akce.get("cena_energie", 0) * len(cilove_postavy)
        cena_temnoty = akce.get("cena_temnoty", 0) * len(cilove_postavy)
        if hrac.sex_energy < cena_energie or hrac.dark_energy < cena_temnoty:
            tisk_chyba(
                f"Nemáš dost energie pro všechny. Potřebuješ "
                f"E:{cena_energie}, T:{cena_temnoty}."
            )
            input("Enter...")
            continue

        provedeno = sum(
            1 for otrok in cilove_postavy
            if proved_interakci(otrok, hrac, akce["id"])
        )
        if provedeno:
            tisk_ok(
                f"Interakce „{akce['nazev']}“ proběhla u {provedeno} "
                f"z {len(cilove_postavy)} postav."
            )
        else:
            tisk_info("Interakce se tentokrát nepodařila.")
        input("Enter...")
        return
