"""Uložitelný stav městského kasina."""

from dataclasses import asdict, dataclass, field


@dataclass
class KasinoSystem:
    otevreno: bool = False
    uroven: int = 0
    celkem_vsazeno: int = 0
    cisty_zisk: int = 0
    vyhry: int = 0
    prohry: int = 0
    remizy: int = 0
    posledni_den_prijmu: int = 0
    historie: list = field(default_factory=list)

    def __post_init__(self):
        self.otevreno = bool(self.otevreno)
        self.uroven = max(0, min(5, _cele_cislo(self.uroven)))
        if self.uroven == 0:
            self.otevreno = False
        self.celkem_vsazeno = max(0, _cele_cislo(self.celkem_vsazeno))
        self.cisty_zisk = _cele_cislo(self.cisty_zisk)
        self.vyhry = max(0, _cele_cislo(self.vyhry))
        self.prohry = max(0, _cele_cislo(self.prohry))
        self.remizy = max(0, _cele_cislo(self.remizy))
        self.posledni_den_prijmu = max(
            0, _cele_cislo(self.posledni_den_prijmu)
        )
        if not isinstance(self.historie, list):
            self.historie = []
        self.historie = [
            zaznam for zaznam in self.historie
            if isinstance(zaznam, dict)
            and isinstance(zaznam.get("hra"), str)
            and isinstance(zaznam.get("vysledek"), str)
        ][-20:]

    @property
    def limit_sazky(self):
        return self.uroven * 100

    def denni_prijem(self, den):
        den = max(0, _cele_cislo(den))
        if (
            not self.otevreno
            or den <= self.posledni_den_prijmu
        ):
            return 0
        self.posledni_den_prijmu = den
        return self.uroven * 10

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            return cls()
        allowed = cls.__dataclass_fields__
        return cls(**{
            key: value for key, value in data.items()
            if key in allowed
        })


def _cele_cislo(hodnota):
    if isinstance(hodnota, bool):
        return 0
    try:
        return int(hodnota)
    except (TypeError, ValueError):
        return 0
