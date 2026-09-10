"""
Couche Service d'Application pour la Caisse Enregistreuse.
Orchestre le panier en cours, la validation de paiement, le rendu de monnaie et le Z de caisse.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
try:
    from .domain import Product, Ticket, TicketItem, PaymentMethod, DomainValidationError, CompanyInfo
    from .database import Database
except ImportError:
    from domain import Product, Ticket, TicketItem, PaymentMethod, DomainValidationError, CompanyInfo
    from database import Database


class CashRegisterService:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()
        self.current_ticket = Ticket()

    def get_catalog(self) -> List[Dict[str, Any]]:
        """Retourne les produits actifs groupés par catégorie."""
        products = self.db.get_all_products()
        return [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "category": p.category,
                "tva_rate": p.tva_rate,
                "color": p.color
            }
            for p in products
        ]

    def get_categories(self) -> List[str]:
        catalog = self.get_catalog()
        cats = sorted(list({p["category"] for p in catalog}))
        return ["Tout"] + cats

    def add_to_ticket(self, product_id: int, quantity: int = 1) -> Dict[str, Any]:
        """Ajoute un produit au ticket en cours."""
        products = self.db.get_all_products()
        prod = next((p for p in products if p.id == product_id), None)
        if not prod:
            raise DomainValidationError(f"Produit ID {product_id} introuvable.")
        self.current_ticket.add_item(prod, quantity=quantity)
        return self.get_ticket_state()

    def remove_from_ticket(self, product_id: int) -> Dict[str, Any]:
        """Décrémente ou retire un produit du ticket."""
        self.current_ticket.remove_item(product_id)
        return self.get_ticket_state()

    def delete_ticket_line(self, product_id: int) -> Dict[str, Any]:
        """Supprime complètement une ligne du ticket."""
        self.current_ticket.delete_line(product_id)
        return self.get_ticket_state()

    def clear_ticket(self) -> Dict[str, Any]:
        """Réinitialise le ticket en cours."""
        self.current_ticket = Ticket()
        return self.get_ticket_state()

    def get_ticket_state(self) -> Dict[str, Any]:
        """Retourne l'état complet du ticket actuel avec ventilation TVA."""
        items = [
            {
                "product_id": item.product_id,
                "name": item.name,
                "unit_price": item.unit_price,
                "quantity": item.quantity,
                "tva_rate": item.tva_rate,
                "total_ttc": item.total_ttc,
                "total_ht": item.total_ht,
                "total_tva": item.total_tva
            }
            for item in self.current_ticket.items
        ]
        return {
            "items": items,
            "total_count": sum(i.quantity for i in self.current_ticket.items),
            "total_ttc": self.current_ticket.total_ttc,
            "total_ht": self.current_ticket.total_ht,
            "total_tva": self.current_ticket.total_tva,
            "tva_breakdown": self.current_ticket.get_tva_breakdown()
        }

    def checkout(self, method_str: str, amount_received: Optional[float] = None) -> Dict[str, Any]:
        """
        Valide la vente, enregistre en base de données et prépare un nouveau ticket.
        Retourne le récapitulatif complet de la transaction conforme aux mentions légales obligatoires.
        """
        if not self.current_ticket.items:
            raise DomainValidationError("Le ticket est vide. Ajoutez au moins un article.")

        # Résolution du mode de paiement
        try:
            method = PaymentMethod(method_str)
        except ValueError:
            method = PaymentMethod.CARTE_BANCAIRE

        change = self.current_ticket.process_payment(method=method, amount_received=amount_received)
        ticket_number = self.db.save_ticket(self.current_ticket)

        company = self.db.get_company_info().to_dict()
        tva_breakdown = self.current_ticket.get_tva_breakdown()
        created_at_str = self.current_ticket.created_at.strftime("%d/%m/%Y %H:%M:%S") if hasattr(self.current_ticket, "created_at") and self.current_ticket.created_at else datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        receipt_summary = {
            "status": "SUCCESS",
            "ticket_number": ticket_number,
            "created_at": created_at_str,
            "company": company,
            "total_ttc": self.current_ticket.total_ttc,
            "total_ht": self.current_ticket.total_ht,
            "total_tva": self.current_ticket.total_tva,
            "tva_breakdown": tva_breakdown,
            "payment_method": method.value,
            "amount_received": self.current_ticket.amount_received,
            "change_returned": change,
            "signature": self.current_ticket.signature,
            "items": [
                {
                    "name": i.name,
                    "quantity": i.quantity,
                    "unit_price": i.unit_price,
                    "tva_rate": i.tva_rate,
                    "total_ht": i.total_ht,
                    "total_tva": i.total_tva,
                    "total_ttc": i.total_ttc,
                    "total": i.total_ttc  # Rétrocompatibilité
                }
                for i in self.current_ticket.items
            ]
        }

        # Nouveau ticket prêt pour la vente suivante
        self.current_ticket = Ticket()
        return receipt_summary

    def add_custom_product(self, name: str, price: float, category: str, tva_rate: float = 10.0, color: str = "#3b82f6") -> int:
        return self.db.add_product(name=name, price=price, category=category, tva_rate=tva_rate, color=color)

    def delete_product(self, product_id: int) -> bool:
        return self.db.delete_product(product_id)

    def get_z_report(self, target_date: Optional[str] = None) -> Dict[str, Any]:
        """Génère le Z de caisse (rapport de clôture de journée avec ventilation TVA)."""
        return self.db.get_daily_summary(target_date)

    def close_daily_z(self, target_date: Optional[str] = None) -> Dict[str, Any]:
        """Clôture formelle et irréversible de la journée (NF 525)."""
        return self.db.close_daily_z(target_date)

    def get_company_info(self) -> Dict[str, Any]:
        """Retourne les données d'identification fiscale de l'entreprise."""
        return self.db.get_company_info().to_dict()

    def update_company_info(self, **kwargs) -> Dict[str, Any]:
        """Met à jour les informations légales de l'entreprise."""
        info = self.db.get_company_info()
        for k, v in kwargs.items():
            if hasattr(info, k) and v is not None:
                setattr(info, k, str(v).strip())
        self.db.update_company_info(info)
        return {"status": "SUCCESS", "company": info.to_dict()}

    def export_fiscal_archive(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """Exporte l'archive fiscale intègre pour l'administration fiscale (LPF art. L. 102 B)."""
        return self.db.export_fiscal_archive(start_date, end_date)

    def get_categories_summary(self) -> List[Dict[str, Any]]:
        return self.db.get_categories_summary()

    def rename_category(self, old_name: str, new_name: str) -> Dict[str, Any]:
        count = self.db.rename_category(old_name, new_name)
        return {"status": "SUCCESS", "old_name": old_name, "new_name": new_name, "updated_count": count}

    def delete_category(self, category_name: str, reassign_to: Optional[str] = "Divers") -> Dict[str, Any]:
        count = self.db.delete_category(category_name, reassign_to=reassign_to)
        return {"status": "SUCCESS", "category": category_name, "reassigned_to": reassign_to, "affected_count": count}

    def get_sales_history(self, limit: int = 100, date_filter: Optional[str] = None) -> Dict[str, Any]:
        """Retourne l'historique des ventes et transactions récentes."""
        return self.db.get_sales_history(limit=limit, date_filter=date_filter)

    def get_ticket_details(self, ticket_number: str) -> Optional[Dict[str, Any]]:
        """Retourne les données d'un ticket pour consultation ou réimpression."""
        return self.db.get_ticket_details(ticket_number)
