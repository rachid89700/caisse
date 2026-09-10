"""
Couche Domaine pour la Caisse Enregistreuse.
Entités pures, règles de gestion métier, calculs de TVA et rendu de monnaie.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class PaymentMethod(str, Enum):
    ESPECES = "Espèces"
    CARTE_BANCAIRE = "Carte Bancaire"
    TICKET_RESTO = "Ticket Restaurant"
    AUTRE = "Autre"


class DomainValidationError(Exception):
    """Exception levée en cas d'incohérence métier."""
    pass


@dataclass
class CompanyInfo:
    """Informations légales obligatoires de l'entreprise émettrice du ticket (CGI art. 286, Code de commerce R. 123-237)."""
    name: str = "BOULANGERIE PATISSERIE DU COMMERCE"
    legal_form: str = "SARL au capital de 15 000 €"
    address: str = "12 Rue de la République, 75001 Paris"
    phone: str = "01 42 68 00 00"
    siret: str = "834 567 890 00018"
    rcs: str = "RCS Paris B 834 567 890"
    code_naf: str = "1071C"
    tva_intra: str = "FR 45 834567890"
    pos_id: str = "CAISSE-01"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "legal_form": self.legal_form,
            "address": self.address,
            "phone": self.phone,
            "siret": self.siret,
            "rcs": self.rcs,
            "code_naf": self.code_naf,
            "tva_intra": self.tva_intra,
            "pos_id": self.pos_id,
        }


@dataclass
class Product:
    id: int
    name: str
    price: float
    category: str
    tva_rate: float = 10.0  # Pourcentage (ex: 10% ou 20%)
    color: str = "#3b82f6"

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise DomainValidationError("Le nom du produit ne peut pas être vide.")
        if self.price < 0:
            raise DomainValidationError("Le prix du produit ne peut pas être négatif.")
        if self.tva_rate < 0:
            raise DomainValidationError("Le taux de TVA ne peut pas être négatif.")


@dataclass
class TicketItem:
    product_id: int
    name: str
    unit_price: float
    quantity: int = 1
    tva_rate: float = 10.0

    def __post_init__(self):
        if self.quantity <= 0:
            raise DomainValidationError("La quantité doit être supérieure à zéro.")
        if self.unit_price < 0:
            raise DomainValidationError("Le prix unitaire ne peut pas être négatif.")

    @property
    def total_ttc(self) -> float:
        return round(self.unit_price * self.quantity, 2)

    @property
    def total_ht(self) -> float:
        rate = 1.0 + (self.tva_rate / 100.0)
        return round(self.total_ttc / rate, 2)

    @property
    def total_tva(self) -> float:
        return round(self.total_ttc - self.total_ht, 2)


@dataclass
class Ticket:
    id: Optional[int] = None
    ticket_number: str = ""
    items: List[TicketItem] = field(default_factory=list)
    payment_method: PaymentMethod = PaymentMethod.CARTE_BANCAIRE
    amount_received: float = 0.0
    change_returned: float = 0.0
    signature: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def add_item(self, product: Product, quantity: int = 1) -> None:
        """Ajoute un produit au ticket ou incrémente sa quantité s'il existe déjà."""
        for item in self.items:
            if item.product_id == product.id:
                item.quantity += quantity
                return
        self.items.append(TicketItem(
            product_id=product.id,
            name=product.name,
            unit_price=product.price,
            quantity=quantity,
            tva_rate=product.tva_rate
        ))

    def remove_item(self, product_id: int) -> None:
        """Supprime une ligne ou décrémente la quantité."""
        for item in self.items:
            if item.product_id == product_id:
                if item.quantity > 1:
                    item.quantity -= 1
                else:
                    self.items.remove(item)
                return

    def delete_line(self, product_id: int) -> None:
        """Supprime complètement une ligne du ticket."""
        self.items = [i for i in self.items if i.product_id != product_id]

    @property
    def total_ttc(self) -> float:
        return round(sum(i.total_ttc for i in self.items), 2)

    @property
    def total_ht(self) -> float:
        return round(sum(i.total_ht for i in self.items), 2)

    @property
    def total_tva(self) -> float:
        return round(sum(i.total_tva for i in self.items), 2)

    def get_tva_breakdown(self) -> dict:
        """
        Calcule la ventilation légale de la TVA par taux (CGI art. 286 et annexe II art. 242 nonies A).
        Pour chaque taux applicable, retourne :
        - rate: Taux de TVA en pourcentage (ex: 5.5, 10.0, 20.0)
        - base_ht: Base d'imposition hors taxes
        - montant_tva: Montant de la TVA
        - total_ttc: Total TTC correspondant
        """
        breakdown = {}
        for item in self.items:
            key = f"{item.tva_rate:.1f}"
            if key not in breakdown:
                breakdown[key] = {
                    "rate": float(item.tva_rate),
                    "base_ht": 0.0,
                    "montant_tva": 0.0,
                    "total_ttc": 0.0,
                }
            breakdown[key]["base_ht"] = round(breakdown[key]["base_ht"] + item.total_ht, 2)
            breakdown[key]["montant_tva"] = round(breakdown[key]["montant_tva"] + item.total_tva, 2)
            breakdown[key]["total_ttc"] = round(breakdown[key]["total_ttc"] + item.total_ttc, 2)
        return dict(sorted(breakdown.items(), key=lambda x: float(x[0])))

    def process_payment(self, method: PaymentMethod, amount_received: Optional[float] = None) -> float:
        """
        Valide le paiement et calcule la monnaie à rendre si paiement en espèces.
        Retourne le montant de la monnaie rendue.
        """
        if not self.items:
            raise DomainValidationError("Impossible de régler un ticket vide.")

        self.payment_method = method
        total = self.total_ttc

        if method == PaymentMethod.ESPECES:
            received = amount_received if amount_received is not None else total
            if received < total:
                raise DomainValidationError(
                    f"Montant reçu ({received:.2f} €) insuffisant pour couvrir le total ({total:.2f} €)."
                )
            self.amount_received = received
            self.change_returned = round(received - total, 2)
        else:
            self.amount_received = total
            self.change_returned = 0.0

        return self.change_returned
