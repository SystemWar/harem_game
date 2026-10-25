"""Uložitelný stav města pro autonomní simulaci živého světa."""

from dataclasses import asdict, dataclass


@dataclass
class StavMesta:
    ident: str
    nazev: str
    prosperita: int = 50
    bezpeci: int = 50
    stabilita: int = 50

    def __post_init__(self):
        for atribut in ("prosperita", "bezpeci", "stabilita"):
            setattr(self, atribut, _rozsah(getattr(self, atribut, 50)))

    def uprav(self, **zmeny):
        for atribut, zmena in zmeny.items():
            if atribut in ("prosperita", "bezpeci", "stabilita"):
                aktualni = getattr(self, atribut)
                setattr(self, atribut, _rozsah(aktualni + _cislo(zmena)))

    def posun_den(self):
        if self.bezpeci < 25:
            self.stabilita -= 1
        elif self.bezpeci >= 70 and self.prosperita >= 55:
            self.stabilita += 1
        if self.stabilita < 25:
            self.prosperita -= 1
        elif self.stabilita >= 70 and self.bezpeci >= 55:
            self.prosperita += 1
        self.__post_init__()

    def uprav_akci(self, akce, velikost=1):
        """Promítne běžnou činnost místního NPC do stavu jeho města."""
        if akce in ("prosperita", "bezpeci", "stabilita"):
            self.uprav(**{akce: velikost})

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data, fallback):
        if not isinstance(data, dict):
            data = {}
        return cls(
            ident=fallback["ident"],
            nazev=fallback["nazev"],
            prosperita=data.get("prosperita", fallback["prosperita"]),
            bezpeci=data.get("bezpeci", fallback["bezpeci"]),
            stabilita=data.get("stabilita", fallback["stabilita"]),
        )


def _cislo(hodnota):
    try:
        if isinstance(hodnota, bool):
            return 0
        return int(hodnota)
    except (TypeError, ValueError):
        return 0


def _rozsah(hodnota):
    return max(0, min(100, _cislo(hodnota)))
