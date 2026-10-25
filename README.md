# Harem Game 2.0 — Dark Dominion

Textová tahová RPG v češtině o správě dominia, průzkumu propojeného světa,
frakcích, postavách, vztazích, ekonomice a soubojích. Verze 2.0 propojuje
dosavadní herní systémy s offline simulací, ve které města, NPC a frakce
pokračují ve svých činnostech i mezi hráčovými rozhodnutími.

**Tvůrce: #LordRusty23**

> Hra pracuje s temnými a dospělými fikčními tématy a je určena dospělému
> publiku. Herní systémy nenahrazují skutečné vztahy, služby ani historické
> informace.

## Spuštění

Potřebuješ Python 3.8 nebo novější. Projekt je připraven hlavně pro Windows;
volitelnou knihovnu `colorama` spouštěč zkusí doinstalovat, pokud chybí.

**Windows:** spusť `spustit.bat`, případně v PowerShellu nebo terminálu:

```powershell
python launcher.py
```

**Přímé spuštění:**

```bash
python main.py
```

Závislosti nejsou povinné pro základní textové rozhraní. Hra běží lokálně,
nevyžaduje síťovou službu ani připojení k online AI.

## Jak hra funguje

Hráč vede vlastní dominium, získává zdroje, rozvíjí pevnost, vyjednává
s frakcemi a rozhoduje o událostech ve Starém městě i Východním Brodě.
Herní den posouvá simulaci světa, městské ukazatele, cíle frakcí, pohyb NPC,
provoz personálu, armádní rozkazy a některé ekonomické systémy. Hráč může
svět ovlivňovat přímými volbami, úkoly, mapovými akcemi i hospodařením.

Hlavní menu vypisuje aktuálně dostupné volby a podporuje více rozložení.
Číselné zkratky se převádějí na interní volby kvůli kompatibilitě se staršími
savy. Řiď se proto názvy zobrazenými ve své hře; nabídka obsahuje mimo jiné:

- interakce a profily postav, harém a vztahy;
- mapu, lokace, NPC, questy a příběhovou kampaň;
- diplomacii, správu frakcí a živý svět;
- pevnost, budovy, ekonomiku, personál a armádu;
- souboje, arénu, alchymii, crafting a výzkum;
- manželství, rodinu, kroniku, kalendář a nastavení.

V hlavním menu se zobrazuje také podpis **Tvůrce: #LordRusty23**.

## Živý svět 2.0

### Města a mapa

Mapa obsahuje 45 propojených lokací ve dvou městech:

- **Staré město** — pevnost, tržiště, přístav, akademie, hostinec a další
  městské, společenské, přírodní a nebezpečné oblasti.
- **Východní Brod** — Východní přístav, tržiště, radnice, kasárna a zahrady;
  navazuje na říční a obchodní cestu ze Starého města.

Hráč objevuje lokace cestováním a průzkumem. Každá lokace má sousedy,
atmosféru, nebezpečí a případné místní akce či odměny. Odhalené oblasti na
mapě získávají barvu podle frakce s nejsilnějším vlivem; legenda rozlišuje
frakční kontrolu a aktuální polohu hráče.

### Frakce a místní simulace

Deset frakcí sleduje vlastní cíl. Jejich denní činnost může měnit bezpečí,
prosperitu či stabilitu měst, postupně ovlivňovat kontrolu lokací a vytvářet
rozhodovací situace pro hráče. Městské hodnoty se drží v rozsahu 0–100 a jejich
vzájemné působení znamená, že dlouhodobě nebezpečné či nestabilní město může
ztrácet prosperitu.

Pět dvojic frakcí má navíc uložené vztahy. Rivalita může způsobit pokles
bezpečí a stability, spojenectví naopak stabilitu posiluje. V nabídce živého
světa lze vztahy ovlivnit zprostředkováním smíru nebo podporou soupeření.

### NPC a jejich příběhy

Městské postavy se přesouvají po propojené mapě a podle své role vyhledávají
oblasti, kde mohou prospět. Jejich činnost přispívá k místnímu stavu měst a
jejich poloha se ukládá. Hráč může otevřít jejich třídílné dlouhodobé příběhy,
pomoci jim za zlato nebo podpořit jejich vlastní rozhodnutí. Dokončení příběhu
ovlivní vztah, město a příslušnou frakci.

### Události, návaznosti a karavany

Městské situace se pravidelně objevují v omezené frontě. Hráč může zvolit
placenou pomoc, bezplatné řešení nebo nezasahovat. Nevyřešené či odmítnuté
situace mají důsledky pro městské ukazatele a zaznamenávají se do historie.
Některá rozhodnutí naplánují pokračování o několik dní později, například
oživení tržiště, bezpečnější čtvrť nebo potíže se zásobami.

Karavany cestují po existujících hranách mapy. Jejich bezpečný příjezd může
přinést hráči zlato, městu prosperitu a obchodníkům vliv; špatné podmínky
zásilku odkloní. Přehled živého světa ukazuje současné karavany, vztahy
frakcí, nadcházející návazné situace a poslední změny.

Simulace je lokální herní logika, nikoli generativní online AI. Její vývoj
vychází z uloženého stavu, pravidel systému a herního dne; veškerá rozhodnutí
hráče zůstávají pod jeho kontrolou.

## Personál a armádní rozkazy

V menu personálu lze najmout průzkumníka, herolda, správce zásob, polního
lékaře nebo válečného velitele. Pracovník má specializaci, denní mzdu, město
působení, zkušenosti a poslední zaznamenanou akci. Mise přinášejí například
objevené lokace, reputaci, příjem, léčení, bezpečí či morálku armády.

Každému pracovníkovi lze nastavit cílové město a styl mise:

- **Vyváženě** — základní účinky a mzda.
- **Úsporně** — denní mzda je nižší.
- **Podpora města** — vyšší mzda a dodatečná stabilita cílového města.
- **Intenzivně** — vyšší mzda a dodatečná prosperita cílového města.

Armáda může hlídkovat, cvičit, patrolovat území nebo podniknout riskantní
tažení. Žold a výsledek závisí na nastavení, počtech vojáků a kapitánů, morálce
a síle oddílů. Starší pracovníci v uložených hrách dostanou výchozí vyvážený
styl mise.

## Dominion, ekonomika a frakce

Pevnost je základna pro budovy, zásoby a rozvoj. Budovy zvyšují produkci nebo
odemykají funkce; tržiště může provozovat obchodní smlouvy, jejichž výsledek
závisí na dostupných surovinách. Městská ekonomika je ovlivněna bezpečím,
prosperitou, stabilitou, karavanami a činností frakcí.

Systém mafie a území spravuje kontrolu čtvrtí, podniky, příjmy, vojáky,
kapitány, morálku a konflikty s organizacemi. Diplomacie mění reputaci frakcí.
Výzkum odemyká technologické bonusy a crafting zpracovává dostupné předměty
a suroviny. Alchymie vyrábí lektvary podle odemčených receptů a zásob
ingrediencí.

## Postavy, vztahy a rodina

Postavy mají vlastní profily, vlastnosti, zdraví, energii, příběhy a historii
rozhodnutí. Hráč může rozvíjet důvěru, loajalitu a vztahy, plnit osobní i
mapové úkoly a přidělovat postavám různé role. Systém manželství a rodiny
zahrnuje zasnoubení, svatbu a rodinný život; harém, vztahy a významné volby
mají samostatné přehledy.

## Dobrodružství, úkoly a souboje

Mapa, běžné questy, NPC linky a kampaň nabízejí cíle s různými podmínkami
a odměnami. Deník úkolů ukazuje aktivní postup, kalendář zaznamenává události
a kronika uchovává důležité volby. Souboje jsou tahové; aréna přidává
protivníky, postup a odměny. Postava může využívat dovednosti, vybavení,
předměty a dostupnou bojovou podporu.

## Ukládání

Hra nabízí pět save slotů a autosave při přechodu na nový den. Uložené hry
jsou ve formátu JSON; zápis je atomický a starší podporované save se při
načítání migrují. Nové systémy živého světa, NPC, měst, vztahů, karavan,
událostí i rozkazů personálu se ukládají. Starším save se při načtení doplní
bezpečné výchozí hodnoty. Formát budoucí verze, kterou tato hra nezná, se
odmítne místo tichého poškození dat.

Ve Windows se uživatelská data ukládají do adresáře aplikace v `%APPDATA%`.
Konkrétní cestu určuje `config.py`; hlavní soubor používá historický název
`harem_dark_v18_save.json`. Save soubory jsou osobní herní data — před ručními
úpravami si vytvoř kopii.

## Nastavení a přístupnost

Nastavení umožňuje upravit vizuální téma, barvy terminálu, rozložení menu,
obtížnost a vývojářský režim. Vývojářské volby jsou standardně vypnuté.
Barevné vykreslení je doplňkové; běžné číselné volby zůstávají ovladatelné
textem. Vzhled emoji závisí na fontu a terminálu.

## Testování a struktura projektu

Testy spustíš z kořenové složky:

```bash
python -m unittest discover -s tests -q
python -m compileall -q data game models utils tests
```

Hlavní části repozitáře:

| Složka / soubor | Obsah |
|---|---|
| `data/` | Definice měst, mapy, frakcí, postav, předmětů a dalších herních dat |
| `game/` | Pravidla, menu, simulace, questy, souboje, ekonomika a ukládání |
| `models/` | Datové modely hráče, postav, měst, frakcí, armády a dalších systémů |
| `utils/` | Pomocné funkce, rozhodovací logika a výpisy |
| `tests/` | Regresní a systémové testy |
| `main.py` | Vstupní bod hry |
| `launcher.py` | Kontrola prostředí a spuštění |

## Poznámka pro recenzenty

Tento README je popis funkcí projektu, nikoli soubor uživatelských recenzí.
Hodnocení hráčů zde nejsou doplňována ani vydávána za skutečná. Hra je
terminálové RPG v češtině; aktuální stav implementace a případné změny ověř
přímo v repozitáři a v testech.

## Tvůrce a repozitář

**Tvůrce: #LordRusty23**

Zdrojový kód: [WarDroid23/harem_game](https://github.com/WarDroid23/harem_game)
