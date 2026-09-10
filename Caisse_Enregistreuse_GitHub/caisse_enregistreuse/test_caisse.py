"""
Tests Unitaires et d'Intégration pour la Caisse Enregistreuse.
Valide les calculs de TVA, de totaux, de rendu de monnaie, de persistance SQLite et le rapport Z.
"""

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from caisse_enregistreuse.domain import Product, Ticket, TicketItem, PaymentMethod, DomainValidationError, CompanyInfo
from caisse_enregistreuse.database import Database
from caisse_enregistreuse.service import CashRegisterService


class TestCaisseDomain(unittest.TestCase):
    def test_product_validation(self):
        p = Product(id=1, name="Baguette", price=1.20, category="Boulangerie", tva_rate=5.5)
        self.assertEqual(p.name, "Baguette")
        self.assertEqual(p.price, 1.20)

        with self.assertRaises(DomainValidationError):
            Product(id=2, name="", price=1.0, category="Boulangerie")

        with self.assertRaises(DomainValidationError):
            Product(id=3, name="Invalide", price=-2.0, category="Boulangerie")

    def test_ticket_calculations_and_tva(self):
        ticket = Ticket()
        p1 = Product(id=1, name="Café", price=2.00, category="Boissons", tva_rate=10.0)
        p2 = Product(id=2, name="Croissant", price=1.50, category="Viennoiseries", tva_rate=10.0)

        ticket.add_item(p1, quantity=2)  # 4.00 €
        ticket.add_item(p2, quantity=1)  # 1.50 €

        self.assertEqual(ticket.total_ttc, 5.50)
        self.assertEqual(ticket.total_ht, 5.00)
        self.assertEqual(ticket.total_tva, 0.50)

    def test_ticket_remove_and_delete(self):
        ticket = Ticket()
        p = Product(id=1, name="Eau", price=1.00, category="Boissons")
        ticket.add_item(p, quantity=3)
        self.assertEqual(ticket.items[0].quantity, 3)

        ticket.remove_item(1)
        self.assertEqual(ticket.items[0].quantity, 2)

        ticket.delete_line(1)
        self.assertEqual(len(ticket.items), 0)

    def test_cash_payment_and_change_return(self):
        ticket = Ticket()
        p = Product(id=1, name="Menu", price=8.50, category="Plats")
        ticket.add_item(p, quantity=1)

        # Reçu 10 € pour 8.50 € => monnaie 1.50 €
        change = ticket.process_payment(PaymentMethod.ESPECES, amount_received=10.00)
        self.assertEqual(change, 1.50)
        self.assertEqual(ticket.change_returned, 1.50)
        self.assertEqual(ticket.amount_received, 10.00)

    def test_insufficient_cash_raises_error(self):
        ticket = Ticket()
        p = Product(id=1, name="Menu", price=10.00, category="Plats")
        ticket.add_item(p, quantity=1)

        with self.assertRaises(DomainValidationError):
            ticket.process_payment(PaymentMethod.ESPECES, amount_received=5.00)


class TestCaisseServiceAndDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_caisse.db"
        self.db = Database(db_path=str(self.db_path))
        self.service = CashRegisterService(db=self.db)

    def tearDown(self):
        if self.db_path.exists():
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    def test_catalog_seeded_and_categories(self):
        catalog = self.service.get_catalog()
        self.assertGreater(len(catalog), 5)
        categories = self.service.get_categories()
        self.assertIn("Tout", categories)
        self.assertIn("Boissons", categories)

    def test_full_sale_and_z_report(self):
        # 1. Ajout au ticket
        catalog = self.service.get_catalog()
        item1 = catalog[0]
        item2 = catalog[1]

        self.service.add_to_ticket(item1["id"], quantity=2)
        self.service.add_to_ticket(item2["id"], quantity=1)

        state = self.service.get_ticket_state()
        expected_total = round((item1["price"] * 2) + item2["price"], 2)
        self.assertEqual(state["total_ttc"], expected_total)

        # 2. Encaissement Carte Bancaire
        receipt = self.service.checkout(method_str="Carte Bancaire")
        self.assertEqual(receipt["status"], "SUCCESS")
        self.assertIn("TCK-", receipt["ticket_number"])

        # 3. Vérification du Z de caisse
        z_report = self.service.get_z_report()
        self.assertEqual(z_report["tickets_count"], 1)
        self.assertEqual(z_report["total_sales_ttc"], expected_total)
        self.assertEqual(len(z_report["payments"]), 1)
        self.assertEqual(z_report["payments"][0]["method"], "Carte Bancaire")

    def test_custom_product_creation(self):
        new_id = self.service.add_custom_product(
            name="Smoothie Mangue",
            price=4.50,
            category="Boissons Fraîches",
            tva_rate=10.0
        )
        self.assertGreater(new_id, 0)
        catalog = self.service.get_catalog()
        found = any(p["name"] == "Smoothie Mangue" for p in catalog)
        self.assertTrue(found)

    def test_categories_summary(self):
        summary = self.service.get_categories_summary()
        self.assertTrue(any(c["category"] == "Boissons" for c in summary))
        for c in summary:
            self.assertGreater(c["count"], 0)

    def test_rename_category(self):
        res = self.service.rename_category("Snacking", "Restauration Rapide")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertGreater(res["updated_count"], 0)

        catalog = self.service.get_catalog()
        self.assertTrue(any(p["category"] == "Restauration Rapide" for p in catalog))
        self.assertFalse(any(p["category"] == "Snacking" for p in catalog))

        summary = self.service.get_categories_summary()
        self.assertTrue(any(c["category"] == "Restauration Rapide" for c in summary))
        self.assertFalse(any(c["category"] == "Snacking" for c in summary))

    def test_delete_category_with_reassignment(self):
        result = self.service.delete_category("Boissons", reassign_to="Divers")
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["reassigned_to"], "Divers")
        self.assertGreater(result["affected_count"], 0)

        catalog = self.service.get_catalog()
        self.assertFalse(any(p["category"] == "Boissons" for p in catalog))
        self.assertTrue(any(p["category"] == "Divers" for p in catalog))

    def test_delete_category_deactivate(self):
        # Create unique category with product
        self.service.add_custom_product(name="Produit Unique", price=10.0, category="TestCat")
        result = self.service.delete_category("TestCat", reassign_to=None)
        self.assertEqual(result["status"], "SUCCESS")
        self.assertGreater(result["affected_count"], 0)

        catalog = self.service.get_catalog()
        self.assertFalse(any(p["name"] == "Produit Unique" for p in catalog))
        self.assertFalse(any(p["category"] == "TestCat" for p in catalog))

    def test_ticket_signature_chaining(self):
        catalog = self.service.get_catalog()
        self.service.add_to_ticket(catalog[0]["id"], 1)
        receipt1 = self.service.checkout("Carte Bancaire")
        sig1 = receipt1.get("signature")
        self.assertIsNotNone(sig1)
        self.assertEqual(len(sig1), 64)  # SHA-256 hex string

        self.service.add_to_ticket(catalog[1]["id"], 1)
        receipt2 = self.service.checkout("Espèces", amount_received=10.0)
        sig2 = receipt2.get("signature")
        self.assertIsNotNone(sig2)
        self.assertNotEqual(sig1, sig2)

    def test_tva_breakdown_multi_rates(self):
        """Vérifie la conformité de la ventilation de la TVA par taux (CGI art. 286)."""
        ticket = Ticket()
        p1 = Product(id=1, name="Baguette", price=1.35, category="Boulangerie", tva_rate=5.5)
        p2 = Product(id=2, name="Sandwich", price=5.00, category="Snacking", tva_rate=10.0)

        ticket.add_item(p1, quantity=2)  # 2.70 € TTC
        ticket.add_item(p2, quantity=1)  # 5.00 € TTC

        breakdown = ticket.get_tva_breakdown()
        self.assertIn("5.5", breakdown)
        self.assertIn("10.0", breakdown)

        self.assertEqual(breakdown["5.5"]["rate"], 5.5)
        self.assertEqual(breakdown["5.5"]["total_ttc"], 2.70)
        self.assertAlmostEqual(breakdown["5.5"]["base_ht"] + breakdown["5.5"]["montant_tva"], 2.70, places=2)

        self.assertEqual(breakdown["10.0"]["rate"], 10.0)
        self.assertEqual(breakdown["10.0"]["total_ttc"], 5.00)
        self.assertAlmostEqual(breakdown["10.0"]["base_ht"] + breakdown["10.0"]["montant_tva"], 5.00, places=2)

        total_ht_sum = round(sum(b["base_ht"] for b in breakdown.values()), 2)
        total_tva_sum = round(sum(b["montant_tva"] for b in breakdown.values()), 2)
        self.assertEqual(total_ht_sum, ticket.total_ht)
        self.assertEqual(total_tva_sum, ticket.total_tva)

    def test_nf525_sqlite_inalterability_triggers(self):
        """Vérifie que les triggers SQLite interdisent physiquement toute modification ou suppression."""
        catalog = self.service.get_catalog()
        self.service.add_to_ticket(catalog[0]["id"], 1)
        receipt = self.service.checkout("Carte Bancaire")
        tck_num = receipt["ticket_number"]

        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            # 1. Tentative d'UPDATE sur tickets -> doit échouer
            with self.assertRaises(sqlite3.IntegrityError):
                cursor.execute("UPDATE tickets SET total_ttc = 0.0 WHERE ticket_number = ?", (tck_num,))

            # 2. Tentative de DELETE sur tickets -> doit échouer
            with self.assertRaises(sqlite3.IntegrityError):
                cursor.execute("DELETE FROM tickets WHERE ticket_number = ?", (tck_num,))

            # 3. Tentative de DELETE sur ticket_items -> doit échouer
            with self.assertRaises(sqlite3.IntegrityError):
                cursor.execute("DELETE FROM ticket_items")

    def test_company_info_and_receipt_data(self):
        """Vérifie la présence des mentions légales obligatoires de l'entreprise sur le ticket."""
        catalog = self.service.get_catalog()
        self.service.add_to_ticket(catalog[0]["id"], 1)
        receipt = self.service.checkout("Carte Bancaire")

        self.assertIn("company", receipt)
        co = receipt["company"]
        self.assertIn("siret", co)
        self.assertIn("rcs", co)
        self.assertIn("tva_intra", co)
        self.assertIn("legal_form", co)
        self.assertIn("tva_breakdown", receipt)
        self.assertIn("created_at", receipt)

    def test_daily_z_closure_and_sealing(self):
        """Vérifie la clôture formelle Z, le scellement cryptographique et le Grand Total perpétuel."""
        catalog = self.service.get_catalog()
        self.service.add_to_ticket(catalog[0]["id"], 2)
        self.service.checkout("Carte Bancaire")

        z_res = self.service.close_daily_z()
        self.assertEqual(z_res["status"], "SUCCESS")
        self.assertIn("Z-", z_res["z_number"])
        self.assertIsNotNone(z_res["signature"])
        self.assertGreater(z_res["summary"]["grand_total_ttc"], 0)

        # Nouvelle tentative de clôture le même jour -> ALREADY_CLOSED
        z_reclose = self.service.close_daily_z()
        self.assertEqual(z_reclose["status"], "ALREADY_CLOSED")

    def test_fiscal_archive_export(self):
        """Vérifie la génération d'une archive fiscale scellée par hachage SHA-256."""
        archive = self.service.export_fiscal_archive()
        self.assertIn("archive_seal_sha256", archive)
        self.assertEqual(len(archive["archive_seal_sha256"]), 64)
        self.assertIn("tickets", archive)
        self.assertIn("z_reports", archive)
        self.assertIn("company", archive)

    def test_manual_update_company_info(self):
        """Vérifie la saisie manuelle et la mise à jour répétée de la dénomination sociale et mentions légales."""
        # 1. Première saisie manuelle de dénomination
        up1 = self.service.update_company_info(
            name="LE FOURNIL DES SAVEURS",
            legal_form="SASU au capital de 10 000 €",
            siret="11122233300044",
            rcs="RCS Lyon B 111 222 333"
        )
        self.assertEqual(up1["status"], "SUCCESS")
        self.assertEqual(self.service.get_company_info()["name"], "LE FOURNIL DES SAVEURS")
        self.assertEqual(self.service.get_company_info()["siret"], "11122233300044")

        # Vérification sur le ticket de caisse généré
        cat = self.service.get_catalog()
        self.service.add_to_ticket(cat[0]["id"], 1)
        r1 = self.service.checkout("Espèces", amount_received=10.0)
        self.assertEqual(r1["company"]["name"], "LE FOURNIL DES SAVEURS")
        self.assertEqual(r1["company"]["siret"], "11122233300044")

        # 2. Deuxième saisie manuelle : possibilité de changer de dénomination à tout moment
        up2 = self.service.update_company_info(
            name="BOULANGERIE DES HALLES",
            siret="99988877700012"
        )
        self.assertEqual(up2["status"], "SUCCESS")
        self.assertEqual(self.service.get_company_info()["name"], "BOULANGERIE DES HALLES")

        # Le ticket suivant reflète immédiatement la nouvelle dénomination
        self.service.add_to_ticket(cat[0]["id"], 2)
        r2 = self.service.checkout("Carte Bancaire")
        self.assertEqual(r2["company"]["name"], "BOULANGERIE DES HALLES")
        self.assertEqual(r2["company"]["siret"], "99988877700012")

    def test_sales_history_and_ticket_reprint(self):
        """Vérifie la consultation de l'historique des ventes et l'accès au duplicata d'un ticket."""
        catalog = self.service.get_catalog()
        self.service.add_to_ticket(catalog[0]["id"], 1)
        r1 = self.service.checkout("Carte Bancaire")

        self.service.add_to_ticket(catalog[1]["id"], 2)
        r2 = self.service.checkout("Espèces", amount_received=20.0)

        # 1. Vérification de l'historique
        history = self.service.get_sales_history(limit=50)
        self.assertGreaterEqual(history["count"], 2)
        self.assertGreater(history["total_sales_ttc"], 0)
        self.assertGreater(history["average_basket"], 0)

        # Les tickets sont ordonnés du plus récent au plus ancien
        tck_numbers = [t["ticket_number"] for t in history["tickets"]]
        self.assertIn(r1["ticket_number"], tck_numbers)
        self.assertIn(r2["ticket_number"], tck_numbers)
        self.assertEqual(history["tickets"][0]["ticket_number"], r2["ticket_number"])

        # 2. Vérification des détails d'un ticket pour réimpression / duplicata
        details = self.service.get_ticket_details(r1["ticket_number"])
        self.assertIsNotNone(details)
        self.assertEqual(details["status"], "SUCCESS")
        self.assertEqual(details["ticket_number"], r1["ticket_number"])
        self.assertTrue(details["is_duplicata"])
        self.assertIn("tva_breakdown", details)
        self.assertIn("company", details)
        self.assertGreaterEqual(len(details["items"]), 1)

        # 3. Ticket inexistant
        self.assertIsNone(self.service.get_ticket_details("TCK-NONEXISTENT"))

    def test_mobile_ticket_html_rendering(self):
        """Vérifie la génération du HTML responsive du e-ticket smartphone (Loi AGEC)."""
        from caisse_enregistreuse.mobile_ticket import render_mobile_ticket

        cat = self.service.get_catalog()
        self.service.add_to_ticket(cat[0]["id"], 2)
        sale = self.service.checkout("Carte Bancaire")

        details = self.service.get_ticket_details(sale["ticket_number"])
        self.assertIsNotNone(details)

        html = render_mobile_ticket(details)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn(sale["ticket_number"], html)
        self.assertIn("E-Ticket", html)
        self.assertIn("Loi Anti-Gaspillage AGEC", html)
        self.assertIn(sale["company"]["name"], html)
        self.assertIn("VENTILATION DE LA TVA (CGI ART. 286)", html)
        self.assertIn("Scellement Fiscal NF 525", html)
        self.assertIn(f"{sale['total_ttc']:.2f} €", html)


if __name__ == "__main__":
    unittest.main()

