"""Lokální příběhy, starosti a obchodní specializace frakcí."""

FRAKCNI_PROFILY = {
    "policie": {
        "starost": "Hlídky jsou přetížené a obyvatelé hlásí nebezpečné cesty.",
        "zbozi": ("obilí", "železné nástroje", "výstroj"),
        "kapitoly": (
            ("Noční hlídka", "Stráž žádá o světla na cestu mezi tržištěm a hranicí."),
            ("Ztracený rozkaz", "Kapitán hledá svědky, kteří pomohou obnovit důvěru v hlídky."),
            ("Bezpečí pro všechny", "Místní rada chce pořádek, který nebude stát na strachu."),
        ),
    },
    "podsveti": {
        "starost": "Pašerácké trasy se střetávají a přístavní dělníci se bojí odvety.",
        "zbozi": ("vzácné koření", "pašované zboží", "stavební kámen"),
        "kapitoly": (
            ("Zásilka bez původu", "Přístavní kontakt nabízí zboží, ale žádá bezpečný průchod."),
            ("Cena příměří", "Dva dokové gangy se přou o sklad a hrozí uzavřením mola."),
            ("Pravidla podsvětí", "Pašeráci rozhodují, zda jejich síť ochrání město, nebo jen sebe."),
        ),
    },
    "cirkev": {
        "starost": "Chrám je rozdělený mezi veřejnou pomoc a hon na domnělé viníky.",
        "zbozi": ("léčivé byliny", "svíce", "krystaly"),
        "kapitoly": (
            ("Záznam z archivu", "Kurýrka přináší starý dokument, který může očistit neprávem obviněné."),
            ("Svědectví bez nátlaku", "Svědkové chtějí, aby je někdo vyslechl bez hrozeb a příkazů."),
            ("Otevřená brána", "Chrám se rozhoduje, zda otevře svou ošetřovnu každému měšťanovi."),
        ),
    },
    "obchodnici": {
        "starost": "Karavany ztrácejí čas na rozbitém mostě a ceny zásob rostou.",
        "zbozi": ("dřevo", "obilí", "železo"),
        "kapitoly": (
            ("Karavana u brodu", "Kupecká vyjednavačka potřebuje dohodnout bezpečné místo k překládce."),
            ("Most a mýto", "Obchodníci nabízejí opravu mostu výměnou za předvídatelné clo."),
            ("Trasa pro dvě města", "Kupci chtějí propojit Staré město s Východním Brodem férovou smlouvou."),
        ),
    },
    "kult_krve": {
        "starost": "Zvláštní světla nad observatoří děsí horníky i obyvatele okolí.",
        "zbozi": ("krystaly", "vzácné houby", "železná ruda"),
        "kapitoly": (
            ("Světlo nad věží", "Vědma hledá vysvětlení světel, která se objevují nad starou věží."),
            ("Kámen z lomu", "Horníci našli rudě zbarvený krystal a žádají bezpečné vyšetření."),
            ("Rituál, nebo výzkum", "Kult musí zvolit mezi tajným obřadem a otevřeným bádáním."),
        ),
    },
    "syndikat_stinu": {
        "starost": "Neověřené zprávy vyvolávají nedůvěru mezi cechy a městskou radou.",
        "zbozi": ("mapy", "zapečetěné zprávy", "stavební dřevo"),
        "kapitoly": (
            ("Dopis pod lucernou", "Informátor našel zprávu, jejíž pravost může potvrdit jen druhý zdroj."),
            ("Síť důvěry", "Špehové chtějí chránit své kontakty před vydíráním a falešnými obviněními."),
            ("Zpráva pro radu", "Syndikát rozhoduje, zda předá městu důkaz o chystaném nebezpečí."),
        ),
    },
    "cech_kurtizan": {
        "starost": "Umělkyně a hostitelé žádají bezpečné prostory a jasná pravidla akcí.",
        "zbozi": ("parfémy", "hedvábí", "květiny"),
        "kapitoly": (
            ("Večer pro mecenáše", "Umělkyně připravuje dobrovolné vystoupení a hledá vhodné místo."),
            ("Smlouva s cechem", "Hostitelé chtějí jasně stanovené odměny a bezpečnostní pravidla."),
            ("Dům otevřených dveří", "Cech se rozhoduje, jak podpořit nové umělce bez dluhových závazků."),
        ),
    },
    "narkomani": {
        "starost": "Lidé v Dýmové čtvrti potřebují bezpečnou pomoc a dostupné léčení.",
        "zbozi": ("čistá voda", "léčivé byliny", "potraviny"),
        "kapitoly": (
            ("Ošetřovna v háji", "Dobrovolníci hledají čisté obvazy a místo pro první pomoc."),
            ("Bezpečná cesta", "Léčitelka nabízí doprovod lidem, kteří se bojí vyhledat pomoc."),
            ("Nový začátek", "Místní skupina chce obnovit zahradní skleník jako veřejné zázemí."),
        ),
    },
    "cyberpunkaci": {
        "starost": "Komunikační uzly v akademické čtvrti se přehřívají a výpadky ohrožují tržiště.",
        "zbozi": ("železo", "krystaly", "alchymistické součástky"),
        "kapitoly": (
            ("Tichý uzel", "Technici hledají součástku, která obnoví spojení mezi dílnami."),
            ("Cena za data", "Městský archiv žádá audit, než odkoupí další citlivé záznamy."),
            ("Síť pro město", "Hackeři rozhodují, zda otevřou opravenou síť i veřejným službám."),
        ),
    },
    "nymfomanky": {
        "starost": "Organizátorky slavnosti chtějí zajistit dobrovolnou účast a klidný průběh.",
        "zbozi": ("květiny", "nápoje", "látky na výzdobu"),
        "kapitoly": (
            ("Pozvánka do zahrady", "Organizátorka plánuje slavnost, na kterou se každý přihlašuje svobodně."),
            ("Dohoda o pravidlech", "Účastníci společně připravují pravidla soukromí a bezpečného návratu."),
            ("Slavnost pod hvězdami", "Zahrada rozhoduje, zda výtěžek věnuje místní ošetřovně."),
        ),
    },
    "gembleri": {
        "starost": "Hráči se zadlužují a kasino potřebuje pravidla pro limity a pomoc.",
        "zbozi": ("kostky", "žetony", "obilí"),
        "kapitoly": (
            ("Dluh u kostek", "Hráčská skupina hledá způsob, jak zastavit nebezpečné půjčky."),
            ("Turnaj s limity", "Organizátoři navrhují férový turnaj s předem známými sázkami."),
            ("Pokladna pomoci", "Gamblerů rozhodují, zda část výtěžku půjde na podporu zadlužených."),
        ),
    },
}

MESTSKE_STAROSTI = {
    "stare_mesto": {
        "prosperita": "Obchodníci žádají opravit sklady a zkrátit zdržení karavan.",
        "bezpeci": "Obyvatelé chtějí hlídky v uličkách i na cestě k přístavu.",
        "stabilita": "Rada potřebuje dohodu mezi cechy, stráží a chrámem.",
    },
    "vychodni_brod": {
        "prosperita": "Říční trh postrádá pravidelné dodávky a opravené molo.",
        "bezpeci": "Pohraniční osady žádají doprovod přes most a zásoby pro hlídky.",
        "stabilita": "Městská rada hledá společný plán pro zahrady, kasárna a kupce.",
    },
}

TRZNI_ZBOZI = {
    "zasoby": {"nazev": "Potraviny", "jednotka": "zásob", "cena": 3},
    "drevo": {"nazev": "Stavební dřevo", "jednotka": "dřeva", "cena": 4},
    "kamen": {"nazev": "Kámen", "jednotka": "kamene", "cena": 5},
    "zelezo": {"nazev": "Železo", "jednotka": "železa", "cena": 9},
    "krystaly": {"nazev": "Krystaly", "jednotka": "krystalů", "cena": 14},
}

VYCHOZI_SKLADY = {
    "stare_mesto": {
        "zasoby": 18, "drevo": 24, "kamen": 20, "zelezo": 9, "krystaly": 5,
    },
    "vychodni_brod": {
        "zasoby": 30, "drevo": 10, "kamen": 12, "zelezo": 15, "krystaly": 3,
    },
}
