import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from data.drogy import DROGY
from game.drogovy_provoz import (
    PRODEJNI_CENA,
    RECEPTY,
    investuj_do_zarizeni,
    prodej_zasob,
    vypestuj_konopi,
    vyrob_drogu,
)
from game.save_load import Hra


class DrogovyProvozTesty(unittest.TestCase):
    def test_nova_volba_menu_otevira_provoz(self):
        from game.menu_hlavni import normalizuj_volbu
        from main import _obnov_hru_runtime, _obsluz_volbu_hlavniho_menu

        hra = Hra()
        with patch(
            "game.drogovy_provoz.menu_drogoveho_provozu"
        ) as menu:
            _obsluz_volbu_hlavniho_menu(
                hra, normalizuj_volbu("39"), _obnov_hru_runtime(hra)
            )
        menu.assert_called_once_with(hra)

    def test_investice_sklizen_a_vyzkum(self):
        hra = Hra()
        hra.hrac.gold = 1_000
        zasoby_pred = hra.pevnost.zasoby
        body_pred = hra.vyzkum.body

        with redirect_stdout(io.StringIO()):
            self.assertEqual(investuj_do_zarizeni(hra, "pestirna"), 350)
            self.assertEqual(vypestuj_konopi(hra), 3)

        stav = hra.drogovy_provoz
        self.assertEqual(hra.pevnost.zasoby, zasoby_pred - 8)
        self.assertEqual(stav["sklad"]["konopny_kvet"], 3)
        self.assertEqual(stav["sklad"]["byliny"], 1)
        self.assertEqual(hra.vyzkum.body, body_pred + 1)

    def test_laboratorni_vyroba_spotrebuje_zasoby_a_prida_body(self):
        hra = Hra()
        hra.hrac.gold = 1_000
        hra.pevnost.krystaly = 4
        with redirect_stdout(io.StringIO()):
            investuj_do_zarizeni(hra, "laborator")
            investuj_do_zarizeni(hra, "pestirna")
            vypestuj_konopi(hra)
            self.assertTrue(vyrob_drogu(hra, "serafinsky_prach"))

        stav = hra.drogovy_provoz
        self.assertEqual(stav["sklad"]["byliny"], 0)
        self.assertEqual(stav["sklad"]["serafinsky_prach"], 1)
        self.assertEqual(hra.pevnost.krystaly, 3)
        self.assertEqual(hra.vyzkum.body, 3)
        self.assertEqual(set(RECEPTY), set(DROGY))

    def test_prodej_zasob_vydela_zlato_a_nepovoli_prodat_prazdny_sklad(self):
        hra = Hra()
        hra.hrac.gold = 0
        stav = hra.drogovy_provoz
        stav.setdefault("sklizeno", 0)
        stav.setdefault("vyrobeno", 0)
        stav.setdefault("zisk", 0)
        stav["sklad"] = {"konopny_kvet": 2}
        with redirect_stdout(io.StringIO()):
            self.assertEqual(prodej_zasob(hra, "konopny_kvet", 2), 36)
            self.assertFalse(prodej_zasob(hra, "konopny_kvet", 1))

        self.assertEqual(hra.hrac.gold, 36)
        self.assertEqual(stav["sklad"]["konopny_kvet"], 0)
        self.assertEqual(stav["zisk"], 36)
        self.assertGreater(PRODEJNI_CENA["temny_elixir"], 0)

    def test_stav_provozu_a_vyzkum_se_zachovaji_v_ulozene_hre(self):
        hra = Hra()
        hra.hrac.gold = 1_000
        hra.pevnost.krystaly = 4
        with redirect_stdout(io.StringIO()):
            investuj_do_zarizeni(hra, "laborator")
            investuj_do_zarizeni(hra, "pestirna")
            vypestuj_konopi(hra)
            vyrob_drogu(hra, "modry_lotos")

        obnovena = Hra.from_dict(hra.to_dict())
        self.assertEqual(
            obnovena.drogovy_provoz,
            hra.drogovy_provoz,
        )
        self.assertEqual(obnovena.vyzkum.body, hra.vyzkum.body)


if __name__ == "__main__":
    unittest.main()
