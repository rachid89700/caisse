import threading
import time
import urllib.request
import json
import sys
from pathlib import Path

# Add root directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from caisse_enregistreuse.app import run_server

# Lancement du serveur en thread d'arrière-plan sur le port 8089 pour le test
server_thread = threading.Thread(target=lambda: run_server(port=8089, open_browser=False), daemon=True)
server_thread.start()
time.sleep(1)

# Vérification du endpoint health
with urllib.request.urlopen("http://127.0.0.1:8089/health") as response:
    health_data = json.loads(response.read().decode("utf-8"))
    assert health_data["status"] == "OK"
    print("✓ Healthcheck HTTP : OK")

# Vérification du catalogue
with urllib.request.urlopen("http://127.0.0.1:8089/api/catalog") as response:
    catalog = json.loads(response.read().decode("utf-8"))
    assert len(catalog) > 5
    print(f"✓ API Catalogue : {len(catalog)} articles chargés")

# Simulation d'un ajout au panier
req = urllib.request.Request(
    "http://127.0.0.1:8089/api/ticket/add",
    data=json.dumps({"product_id": catalog[0]["id"], "quantity": 2}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as response:
    ticket_state = json.loads(response.read().decode("utf-8"))
    assert ticket_state["total_count"] == 2
    print(f"✓ Ajout au ticket : Total {ticket_state['total_ttc']} € pour 2 articles")

# Simulation d'un encaissement CB
req_checkout = urllib.request.Request(
    "http://127.0.0.1:8089/api/checkout",
    data=json.dumps({"method": "Carte Bancaire"}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req_checkout) as response:
    receipt = json.loads(response.read().decode("utf-8"))
    assert receipt["status"] == "SUCCESS"
    assert "TCK-" in receipt["ticket_number"]
    print(f"✓ Encaissement réussi : Ticket {receipt['ticket_number']} généré")

# Vérification du Z de caisse
with urllib.request.urlopen("http://127.0.0.1:8089/api/z_report") as response:
    z_data = json.loads(response.read().decode("utf-8"))
    assert z_data["tickets_count"] >= 1
    print(f"✓ Rapport Z validé : {z_data['tickets_count']} ticket(s) enregistré(s), Total : {z_data['total_sales_ttc']} €")

print("\n🎉 TOUS LES FLUX DU SERVEUR DE CAISSE SONT VALIDÉS À 100% !")
