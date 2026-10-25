import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from game.manzelstvi import nastav_pozici_manzelky, vychovat_dite
from game.save_load import Hra
from models.marriage import Marriage
from models.otrokyne import Otrokyně


class ManzelstviTesty(unittest.TestCase):
    def _pridej_manzelku(self, hra, jmeno, pozice="choť"):
        postava = Otrokyně(jmeno, vek=25)
        postava.je_manzelkou = True
        postava.partnerka = True
        hra.harem.pridat(postava)
        hra.marriage_system[jmeno] = Marriage(
            partner_jmeno=jmeno,
            den_zasnubin=1,
            den_svatby=12,
            stav="vdana",
            pozice=pozice,
        )
        return hra.marriage_system[jmeno]

    def test_dvorska_funkce_zustava_jedinecna(self):
        hra = Hra()
        prvni = self._pridej_manzelku(hra, "Mira", "radkyne")
        druha = self._pridej_manzelku(hra, "Nela")

        with patch("builtins.input", side_effect=["2", "3"]), \
             redirect_stdout(io.StringIO()):
            self.assertTrue(nastav_pozici_manzelky(hra))

        self.assertEqual(druha.pozice, "radkyne")
        self.assertEqual(prvni.pozice, "choť")

    def test_nula_nevybere_posledni_manzelku_ani_obor_ditete(self):
        hra = Hra()
        marriage = self._pridej_manzelku(hra, "Mira")
        dite = marriage.prida_dite("Ari")
        puvodni_typ = dite["typ"]
        zlato_pred = hra.hrac.gold

        with patch("builtins.input", return_value="0"), \
             redirect_stdout(io.StringIO()):
            self.assertFalse(nastav_pozici_manzelky(hra))
        with patch("builtins.input", side_effect=["1", "0"]), \
             redirect_stdout(io.StringIO()):
            self.assertFalse(vychovat_dite(hra))

        self.assertEqual(hra.hrac.gold, zlato_pred)
        self.assertEqual(dite["typ"], puvodni_typ)

    def test_deti_starnou_po_herním_roce_a_pozice_maji_prijem(self):
        hra = Hra()
        marriage = self._pridej_manzelku(hra, "Mira", "spravkyne_panstvi")
        dite = marriage.prida_dite("Ari")
        dite["vek_dni"] = 364

        pred = hra.harem.pasivni_prijem()
        marriage.starne_deti()
        prijem_spravkyne = hra.harem.pasivni_prijem()

        self.assertEqual(dite["vek"], 1)
        self.assertEqual(dite["vek_dni"], 0)
        self.assertEqual(prijem_spravkyne, pred)
        hra.nevestinec.otevreno = True
        marriage.pozice = "mecenaska"
        self.assertEqual(hra.harem.pasivni_prijem(), pred + 2)


if __name__ == "__main__":
    unittest.main()
