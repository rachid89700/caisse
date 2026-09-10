"""
Couche Persistance SQLite pour la Caisse Enregistreuse.
Gère les produits, l'historique des ventes, les tickets et le Z de caisse.
"""

import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from .domain import Product, Ticket, TicketItem, PaymentMethod, CompanyInfo
except ImportError:
    from domain import Product, Ticket, TicketItem, PaymentMethod, CompanyInfo


DEFAULT_PRODUCTS = [
    # Boulangerie / Viennoiserie
    {"name": "Croissant pur beurre", "price": 1.30, "category": "Viennoiseries", "tva": 10.0, "color": "#f59e0b"},
    {"name": "Pain au chocolat", "price": 1.40, "category": "Viennoiseries", "tva": 10.0, "color": "#d97706"},
    {"name": "Baguette Tradition", "price": 1.35, "category": "Boulangerie", "tva": 5.5, "color": "#b45309"},
    {"name": "Pain de campagne", "price": 2.80, "category": "Boulangerie", "tva": 5.5, "color": "#92400e"},

    # Boissons Chaudes & Fraîches
    {"name": "Café Expresso", "price": 1.80, "category": "Boissons", "tva": 10.0, "color": "#3b82f6"},
    {"name": "Grand Café / Allongé", "price": 2.20, "category": "Boissons", "tva": 10.0, "color": "#2563eb"},
    {"name": "Cappuccino", "price": 3.20, "category": "Boissons", "tva": 10.0, "color": "#1d4ed8"},
    {"name": "Thé / Infusion Bio", "price": 2.80, "category": "Boissons", "tva": 10.0, "color": "#0284c7"},
    {"name": "Eau Minérale 50cl", "price": 1.50, "category": "Boissons", "tva": 5.5, "color": "#0ea5e9"},
    {"name": "Soda / Canette 33cl", "price": 2.50, "category": "Boissons", "tva": 10.0, "color": "#06b6d4"},

    # Snacking / Déjeuner
    {"name": "Sandwich Jambon-Beurre", "price": 4.80, "category": "Snacking", "tva": 10.0, "color": "#10b981"},
    {"name": "Sandwich Poulet Crudités", "price": 5.40, "category": "Snacking", "tva": 10.0, "color": "#059669"},
    {"name": "Formule Déjeuner (Plat+Boisson+Dessert)", "price": 8.90, "category": "Snacking", "tva": 10.0, "color": "#047857"},
    {"name": "Quiche Lorraine", "price": 4.50, "category": "Snacking", "tva": 10.0, "color": "#15803d"},

    # Desserts & Gourmandises
    {"name": "Cookie Chocolat", "price": 2.20, "category": "Desserts", "tva": 10.0, "color": "#8b5cf6"},
    {"name": "Muffin Myrtille", "price": 2.60, "category": "Desserts", "tva": 10.0, "color": "#7c3aed"},
    {"name": "Tartelette aux Pommes", "price": 3.40, "category": "Desserts", "tva": 10.0, "color": "#6d28d9"},
]


class Database:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or "caisse.db").resolve()
        self._init_tables()
        self._seed_default_products()
        self._seed_default_company()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    category TEXT NOT NULL,
                    tva_rate REAL NOT NULL DEFAULT 10.0,
                    color TEXT NOT NULL DEFAULT '#3b82f6',
                    active INTEGER NOT NULL DEFAULT 1
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_number TEXT UNIQUE NOT NULL,
                    total_ttc REAL NOT NULL,
                    total_ht REAL NOT NULL,
                    total_tva REAL NOT NULL,
                    payment_method TEXT NOT NULL,
                    amount_received REAL NOT NULL,
                    change_returned REAL NOT NULL,
                    signature TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            try:
                cursor.execute("ALTER TABLE tickets ADD COLUMN signature TEXT")
            except Exception:
                pass
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ticket_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER NOT NULL,
                    product_id INTEGER,
                    name TEXT NOT NULL,
                    unit_price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    total_ttc REAL NOT NULL,
                    tva_rate REAL NOT NULL,
                    FOREIGN KEY (ticket_id) REFERENCES tickets(id)
                )
            """)

            # Tables de conformité NF 525 et réglementaire
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS company_settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    name TEXT NOT NULL,
                    legal_form TEXT NOT NULL,
                    address TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    siret TEXT NOT NULL,
                    rcs TEXT NOT NULL,
                    code_naf TEXT NOT NULL,
                    tva_intra TEXT NOT NULL,
                    pos_id TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS z_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    z_number TEXT UNIQUE NOT NULL,
                    period_date TEXT NOT NULL,
                    tickets_count INTEGER NOT NULL,
                    total_sales_ttc REAL NOT NULL,
                    total_sales_ht REAL NOT NULL,
                    total_tva REAL NOT NULL,
                    grand_total_ttc REAL NOT NULL,
                    tva_breakdown TEXT NOT NULL,
                    payments_breakdown TEXT NOT NULL,
                    signature TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS technical_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    signature TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            # Triggers d'inaltérabilité stricte NF 525 (interdiction absolue de modification/suppression de tickets validés)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_prevent_ticket_update
                BEFORE UPDATE ON tickets
                BEGIN
                    SELECT RAISE(ABORT, 'NF525 : Inaltérabilité stricte - Modification de ticket validé interdite.');
                END;
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_prevent_ticket_delete
                BEFORE DELETE ON tickets
                BEGIN
                    SELECT RAISE(ABORT, 'NF525 : Inaltérabilité stricte - Suppression de ticket validé interdite.');
                END;
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_prevent_ticket_items_update
                BEFORE UPDATE ON ticket_items
                BEGIN
                    SELECT RAISE(ABORT, 'NF525 : Inaltérabilité stricte - Modification de ligne de ticket validé interdite.');
                END;
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_prevent_ticket_items_delete
                BEFORE DELETE ON ticket_items
                BEGIN
                    SELECT RAISE(ABORT, 'NF525 : Inaltérabilité stricte - Suppression de ligne de ticket validé interdite.');
                END;
            """)
            conn.commit()

    def _seed_default_company(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as cnt FROM company_settings WHERE id = 1")
            if cursor.fetchone()["cnt"] == 0:
                default_co = CompanyInfo()
                cursor.execute("""
                    INSERT INTO company_settings (id, name, legal_form, address, phone, siret, rcs, code_naf, tva_intra, pos_id)
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    default_co.name, default_co.legal_form, default_co.address, default_co.phone,
                    default_co.siret, default_co.rcs, default_co.code_naf, default_co.tva_intra, default_co.pos_id
                ))
                conn.commit()

    def _seed_default_products(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as cnt FROM products")
            if cursor.fetchone()["cnt"] == 0:
                for item in DEFAULT_PRODUCTS:
                    cursor.execute("""
                        INSERT INTO products (name, price, category, tva_rate, color)
                        VALUES (?, ?, ?, ?, ?)
                    """, (item["name"], item["price"], item["category"], item["tva"], item["color"]))
                conn.commit()

    def get_all_products(self) -> List[Product]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price, category, tva_rate, color FROM products WHERE active = 1 ORDER BY category, name")
            return [
                Product(
                    id=row["id"],
                    name=row["name"],
                    price=row["price"],
                    category=row["category"],
                    tva_rate=row["tva_rate"],
                    color=row["color"]
                ) for row in cursor.fetchall()
            ]

    def add_product(self, name: str, price: float, category: str, tva_rate: float = 10.0, color: str = "#3b82f6") -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (name, price, category, tva_rate, color)
                VALUES (?, ?, ?, ?, ?)
            """, (name, price, category, tva_rate, color))
            conn.commit()
            return cursor.lastrowid

    def delete_product(self, product_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET active = 0 WHERE id = ?", (product_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_categories_summary(self) -> List[Dict[str, Any]]:
        """Retourne la liste des catégories existantes avec le décompte des produits actifs."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM products
                WHERE active = 1
                GROUP BY category
                ORDER BY category
            """)
            return [{"category": row["category"], "name": row["category"], "count": row["count"]} for row in cursor.fetchall()]

    def rename_category(self, old_name: str, new_name: str) -> int:
        """Renomme une catégorie existante pour tous les produits associés."""
        old_name = (old_name or "").strip()
        new_name = (new_name or "").strip()
        if not new_name:
            raise ValueError("Le nouveau nom de catégorie ne peut pas être vide.")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products
                SET category = ?
                WHERE category = ? AND active = 1
            """, (new_name, old_name))
            conn.commit()
            return cursor.rowcount

    def delete_category(self, category_name: str, reassign_to: Optional[str] = "Divers") -> int:
        """
        Supprime une catégorie :
        - Soit en réassignant ses produits à une autre catégorie (par défaut 'Divers').
        - Soit en désactivant (supprimant) tous les produits de cette catégorie si reassign_to est vide/None.
        """
        category_name = (category_name or "").strip()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if reassign_to:
                target = reassign_to.strip() or "Divers"
                cursor.execute("""
                    UPDATE products
                    SET category = ?
                    WHERE category = ? AND active = 1
                """, (target, category_name))
            else:
                cursor.execute("""
                    UPDATE products
                    SET active = 0
                    WHERE category = ? AND active = 1
                """, (category_name,))
            conn.commit()
            return cursor.rowcount

    def save_ticket(self, ticket: Ticket) -> str:
        """Enregistre le ticket et ses lignes dans la base."""
        now = datetime.now()
        timestamp_str = now.strftime("%Y%m%d%H%M%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Génère un numéro de ticket séquentiel unique
            cursor.execute("SELECT COUNT(*) as count FROM tickets WHERE date(created_at) = date('now')")
            today_count = cursor.fetchone()["count"] + 1
            ticket_number = f"TCK-{now.strftime('%Y%m%d')}-{today_count:04d}"
            ticket.ticket_number = ticket_number

            # Chaînage cryptographique NF 525 (Signature SHA-256 scellant le ticket avec le précédent)
            cursor.execute("SELECT signature FROM tickets ORDER BY id DESC LIMIT 1")
            prev_row = cursor.fetchone()
            prev_sig = prev_row["signature"] if (prev_row and prev_row["signature"]) else "GENESIS_ROOT_CAISSE"
            chain_payload = f"{ticket_number}|{ticket.total_ttc}|{ticket.total_ht}|{ticket.total_tva}|{now.isoformat()}|{prev_sig}"
            signature = hashlib.sha256(chain_payload.encode("utf-8")).hexdigest()
            ticket.signature = signature

            cursor.execute("""
                INSERT INTO tickets (ticket_number, total_ttc, total_ht, total_tva, payment_method, amount_received, change_returned, signature, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket_number,
                ticket.total_ttc,
                ticket.total_ht,
                ticket.total_tva,
                ticket.payment_method.value if hasattr(ticket.payment_method, "value") else str(ticket.payment_method),
                ticket.amount_received,
                ticket.change_returned,
                signature,
                now.isoformat()
            ))
            ticket_id = cursor.lastrowid
            ticket.id = ticket_id

            for item in ticket.items:
                cursor.execute("""
                    INSERT INTO ticket_items (ticket_id, product_id, name, unit_price, quantity, total_ttc, tva_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    ticket_id,
                    item.product_id,
                    item.name,
                    item.unit_price,
                    item.quantity,
                    item.total_ttc,
                    item.tva_rate
                ))
            conn.commit()
            return ticket_number

    def get_company_info(self) -> CompanyInfo:
        """Retourne les mentions légales de l'entreprise émettrice."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, legal_form, address, phone, siret, rcs, code_naf, tva_intra, pos_id FROM company_settings WHERE id = 1")
            row = cursor.fetchone()
            if row:
                return CompanyInfo(
                    name=row["name"],
                    legal_form=row["legal_form"],
                    address=row["address"],
                    phone=row["phone"],
                    siret=row["siret"],
                    rcs=row["rcs"],
                    code_naf=row["code_naf"],
                    tva_intra=row["tva_intra"],
                    pos_id=row["pos_id"]
                )
            return CompanyInfo()

    def update_company_info(self, info: CompanyInfo) -> None:
        """Met à jour les informations légales de l'entreprise."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE company_settings
                SET name = ?, legal_form = ?, address = ?, phone = ?, siret = ?, rcs = ?, code_naf = ?, tva_intra = ?, pos_id = ?
                WHERE id = 1
            """, (info.name, info.legal_form, info.address, info.phone, info.siret, info.rcs, info.code_naf, info.tva_intra, info.pos_id))
            conn.commit()

    def get_daily_summary(self, target_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Calcule le Z de Caisse (clôture journalière) avec ventilation de TVA par taux et compteur perpétuel (NF 525).
        """
        date_filter = target_date or datetime.now().strftime("%Y-%m-%d")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as tickets_count,
                    COALESCE(SUM(total_ttc), 0.0) as total_sales,
                    COALESCE(SUM(total_ht), 0.0) as total_ht,
                    COALESCE(SUM(total_tva), 0.0) as total_tva
                FROM tickets
                WHERE date(created_at) = date(?)
            """, (date_filter,))
            global_row = cursor.fetchone()

            cursor.execute("""
                SELECT 
                    payment_method,
                    COUNT(*) as count,
                    COALESCE(SUM(total_ttc), 0.0) as sum_ttc
                FROM tickets
                WHERE date(created_at) = date(?)
                GROUP BY payment_method
            """, (date_filter,))
            payment_breakdown = [
                {"method": r["payment_method"], "count": r["count"], "total": round(r["sum_ttc"], 2)}
                for r in cursor.fetchall()
            ]

            # Ventilation de la TVA par taux légal (5.5%, 10%, 20%)
            cursor.execute("""
                SELECT ti.tva_rate, ti.total_ttc
                FROM ticket_items ti
                JOIN tickets t ON ti.ticket_id = t.id
                WHERE date(t.created_at) = date(?)
            """, (date_filter,))
            tva_summary = {}
            for row in cursor.fetchall():
                rate = float(row["tva_rate"])
                ttc = float(row["total_ttc"])
                rate_k = f"{rate:.1f}"
                if rate_k not in tva_summary:
                    tva_summary[rate_k] = {"rate": rate, "base_ht": 0.0, "montant_tva": 0.0, "total_ttc": 0.0}
                ht = round(ttc / (1.0 + rate / 100.0), 2)
                tva = round(ttc - ht, 2)
                tva_summary[rate_k]["base_ht"] = round(tva_summary[rate_k]["base_ht"] + ht, 2)
                tva_summary[rate_k]["montant_tva"] = round(tva_summary[rate_k]["montant_tva"] + tva, 2)
                tva_summary[rate_k]["total_ttc"] = round(tva_summary[rate_k]["total_ttc"] + ttc, 2)
            tva_breakdown = dict(sorted(tva_summary.items(), key=lambda x: float(x[0])))

            # Grand Total perpétuel (compteur perpétuel d'encaissement cumulé NF 525)
            cursor.execute("SELECT COALESCE(SUM(total_ttc), 0.0) as grand_total FROM tickets")
            grand_total = round(cursor.fetchone()["grand_total"], 2)

            # Top 5 articles vendus
            cursor.execute("""
                SELECT ti.name, SUM(ti.quantity) as qty, SUM(ti.total_ttc) as total
                FROM ticket_items ti
                JOIN tickets t ON ti.ticket_id = t.id
                WHERE date(t.created_at) = date(?)
                GROUP BY ti.name
                ORDER BY qty DESC
                LIMIT 5
            """, (date_filter,))
            top_items = [
                {"name": r["name"], "quantity": r["qty"], "total": round(r["total"], 2)}
                for r in cursor.fetchall()
            ]

            # Statut de clôture formelle Z
            cursor.execute("SELECT z_number, signature, created_at FROM z_reports WHERE period_date = date(?)", (date_filter,))
            z_existing = cursor.fetchone()

            tickets_cnt = global_row["tickets_count"]
            total_sales = round(global_row["total_sales"], 2)
            avg_basket = round(total_sales / tickets_cnt, 2) if tickets_cnt > 0 else 0.0

            return {
                "date": date_filter,
                "tickets_count": tickets_cnt,
                "total_sales_ttc": total_sales,
                "total_sales_ht": round(global_row["total_ht"], 2),
                "total_tva": round(global_row["total_tva"], 2),
                "grand_total_ttc": grand_total,
                "tva_breakdown": tva_breakdown,
                "average_basket": avg_basket,
                "payments": payment_breakdown,
                "top_items": top_items,
                "is_closed": bool(z_existing),
                "z_number": z_existing["z_number"] if z_existing else None,
                "signature": z_existing["signature"] if z_existing else None,
                "company": self.get_company_info().to_dict()
            }

    def close_daily_z(self, target_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Effectue la clôture journalière irréversible (Rapport Z) avec scellement SHA-256 (NF 525).
        """
        date_filter = target_date or datetime.now().strftime("%Y-%m-%d")
        summary = self.get_daily_summary(date_filter)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM z_reports WHERE period_date = date(?)", (date_filter,))
            existing = cursor.fetchone()
            if existing:
                return {
                    "status": "ALREADY_CLOSED",
                    "message": f"La journée {date_filter} a déjà été clôturée par le Rapport {existing['z_number']}.",
                    "z_number": existing["z_number"],
                    "signature": existing["signature"],
                    "date": date_filter,
                    "summary": summary
                }

            cursor.execute("SELECT COUNT(*) as cnt FROM z_reports")
            z_seq = cursor.fetchone()["cnt"] + 1
            z_number = f"Z-{date_filter.replace('-', '')}-{z_seq:04d}"

            cursor.execute("SELECT signature FROM z_reports ORDER BY id DESC LIMIT 1")
            prev_row = cursor.fetchone()
            prev_sig = prev_row["signature"] if (prev_row and prev_row["signature"]) else "GENESIS_Z_ROOT_CAISSE"

            chain_payload = f"{z_number}|{date_filter}|{summary['tickets_count']}|{summary['total_sales_ttc']}|{summary['grand_total_ttc']}|{prev_sig}"
            signature = hashlib.sha256(chain_payload.encode("utf-8")).hexdigest()
            now_iso = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO z_reports (z_number, period_date, tickets_count, total_sales_ttc, total_sales_ht, total_tva, grand_total_ttc, tva_breakdown, payments_breakdown, signature, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                z_number,
                date_filter,
                summary["tickets_count"],
                summary["total_sales_ttc"],
                summary["total_sales_ht"],
                summary["total_tva"],
                summary["grand_total_ttc"],
                json.dumps(summary["tva_breakdown"]),
                json.dumps(summary["payments"]),
                signature,
                now_iso
            ))
            conn.commit()

        self.log_technical_event("CLOSURE_Z", f"Clôture journalière {z_number} scellée pour le {date_filter}")
        summary["is_closed"] = True
        summary["z_number"] = z_number
        summary["signature"] = signature
        return {
            "status": "SUCCESS",
            "message": f"Clôture journalière {z_number} scellée avec succès.",
            "z_number": z_number,
            "signature": signature,
            "date": date_filter,
            "summary": summary
        }

    def log_technical_event(self, event_type: str, description: str) -> None:
        """Consigne un événement dans le Journal des Événements Techniques (JET - NF 525)."""
        now = datetime.now().isoformat()
        payload = f"{now}|{event_type}|{description}"
        sig = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO technical_events (event_type, description, signature, created_at)
                    VALUES (?, ?, ?, ?)
                """, (event_type, description, sig, now))
                conn.commit()
        except Exception:
            pass

    def export_fiscal_archive(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Exporte l'archive fiscale complète (tickets, lignes, clôtures Z, journal JET)
        scellée par un hachage SHA-256 global pour l'administration fiscale (LPF art. L. 102 B).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query_t = "SELECT * FROM tickets WHERE 1=1"
            params = []
            if start_date:
                query_t += " AND date(created_at) >= date(?)"
                params.append(start_date)
            if end_date:
                query_t += " AND date(created_at) <= date(?)"
                params.append(end_date)
            query_t += " ORDER BY id ASC"
            cursor.execute(query_t, params)
            tickets = [dict(r) for r in cursor.fetchall()]

            for t in tickets:
                cursor.execute("SELECT * FROM ticket_items WHERE ticket_id = ?", (t["id"],))
                t["items"] = [dict(i) for i in cursor.fetchall()]

            cursor.execute("SELECT * FROM z_reports ORDER BY id ASC")
            z_reports = [dict(r) for r in cursor.fetchall()]

            cursor.execute("SELECT * FROM technical_events ORDER BY id ASC")
            events = [dict(r) for r in cursor.fetchall()]

            company = self.get_company_info().to_dict()

            archive_payload = {
                "generated_at": datetime.now().isoformat(),
                "standards": "NF 525 / Art. 88 Loi de Finances n° 2015-1785 / CGI art. 286",
                "company": company,
                "tickets_count": len(tickets),
                "tickets": tickets,
                "z_reports": z_reports,
                "technical_events": events
            }

            serialized = json.dumps(archive_payload, sort_keys=True, ensure_ascii=False)
            archive_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
            archive_payload["archive_seal_sha256"] = archive_hash
            return archive_payload

    def get_sales_history(self, limit: int = 100, date_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Retourne l'historique des tickets de caisse avec statistiques de synthèse (total, panier moyen, nombre de tickets).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM tickets WHERE 1=1"
            params = []
            if date_filter:
                clean_filter = date_filter.strip()
                if len(clean_filter) == 7:  # Format mois AAAA-MM
                    query += " AND strftime('%Y-%m', created_at) = ?"
                    params.append(clean_filter)
                else:
                    query += " AND date(created_at) = date(?)"
                    params.append(clean_filter)
            query += " ORDER BY id DESC"
            if limit is not None and limit > 0:
                query += " LIMIT ?"
                params.append(limit)

            cursor.execute(query, params)
            tickets = [dict(r) for r in cursor.fetchall()]

            total_sales = 0.0
            total_ht = 0.0
            total_tva = 0.0

            for t in tickets:
                cursor.execute("SELECT * FROM ticket_items WHERE ticket_id = ? ORDER BY id ASC", (t["id"],))
                items = [dict(i) for i in cursor.fetchall()]
                t["items"] = items
                t["items_count"] = sum(i["quantity"] for i in items)
                total_sales += float(t["total_ttc"])
                total_ht += float(t.get("total_ht", 0.0))
                total_tva += float(t.get("total_tva", 0.0))

            count = len(tickets)
            avg_basket = round(total_sales / count, 2) if count > 0 else 0.0

            return {
                "tickets": tickets,
                "count": count,
                "total_sales_ttc": round(total_sales, 2),
                "total_sales_ht": round(total_ht, 2),
                "total_tva": round(total_tva, 2),
                "average_basket": avg_basket,
                "date_filter": date_filter
            }

    def get_ticket_details(self, ticket_number: str) -> Optional[Dict[str, Any]]:
        """
        Retourne l'ensemble des données d'un ticket spécifique pour consultation ou réimpression (duplicata).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tickets WHERE ticket_number = ?", (ticket_number,))
            row = cursor.fetchone()
            if not row:
                return None
            ticket_data = dict(row)

            cursor.execute("SELECT * FROM ticket_items WHERE ticket_id = ? ORDER BY id ASC", (ticket_data["id"],))
            items = [dict(i) for i in cursor.fetchall()]

            # Recalcul de la ventilation de TVA
            tva_summary = {}
            for i in items:
                rate = float(i.get("tva_rate", 10.0))
                ttc = float(i["total_ttc"])
                rate_k = f"{rate:.1f}"
                if rate_k not in tva_summary:
                    tva_summary[rate_k] = {"rate": rate, "base_ht": 0.0, "montant_tva": 0.0, "total_ttc": 0.0}
                ht = round(ttc / (1.0 + rate / 100.0), 2)
                tva = round(ttc - ht, 2)
                tva_summary[rate_k]["base_ht"] = round(tva_summary[rate_k]["base_ht"] + ht, 2)
                tva_summary[rate_k]["montant_tva"] = round(tva_summary[rate_k]["montant_tva"] + tva, 2)
                tva_summary[rate_k]["total_ttc"] = round(tva_summary[rate_k]["total_ttc"] + ttc, 2)

            tva_breakdown = dict(sorted(tva_summary.items(), key=lambda x: float(x[0])))
            company = self.get_company_info().to_dict()

            return {
                "status": "SUCCESS",
                "ticket_number": ticket_data["ticket_number"],
                "created_at": ticket_data["created_at"],
                "company": company,
                "total_ttc": ticket_data["total_ttc"],
                "total_ht": ticket_data["total_ht"],
                "total_tva": ticket_data["total_tva"],
                "tva_breakdown": tva_breakdown,
                "payment_method": ticket_data["payment_method"],
                "amount_received": ticket_data["amount_received"],
                "change_returned": ticket_data["change_returned"],
                "signature": ticket_data["signature"],
                "is_duplicata": True,
                "items": [
                    {
                        "name": i["name"],
                        "quantity": i["quantity"],
                        "unit_price": i["unit_price"],
                        "tva_rate": i.get("tva_rate", 10.0),
                        "total_ht": round(i["total_ttc"] / (1.0 + float(i.get("tva_rate", 10.0)) / 100.0), 2),
                        "total_tva": round(i["total_ttc"] - (i["total_ttc"] / (1.0 + float(i.get("tva_rate", 10.0)) / 100.0)), 2),
                        "total_ttc": i["total_ttc"],
                        "total": i["total_ttc"]
                    }
                    for i in items
                ]
            }
