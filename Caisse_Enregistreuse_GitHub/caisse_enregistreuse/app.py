"""
Serveur HTTP et Point d'Entrée Principal pour la Caisse Enregistreuse.
Fournit l'API REST et sert l'interface web tactile.
Fonctionne à 100% avec les bibliothèques standard de Python (zéro dépendance externe).
"""

import argparse
import io
import json
import os
import socket
import sys
import urllib.parse
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional

# Configuration console Windows UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from .service import CashRegisterService
    from .web_ui import HTML_PAGE
    from .mobile_ticket import render_mobile_ticket
except ImportError:
    from service import CashRegisterService
    from web_ui import HTML_PAGE
    from mobile_ticket import render_mobile_ticket

# Instance globale du service
service = CashRegisterService()


def get_local_ip() -> str:
    """Détecte l'adresse IP locale de la machine sur le réseau LAN/Wi-Fi."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


class CashRegisterHTTPHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: dict, status: int = 200) -> None:
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def _send_html(self, html: str, status: int = 200) -> None:
        payload = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _parse_json_body(self) -> dict:
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len > 0:
            body = self.rfile.read(content_len).decode("utf-8")
            try:
                return json.loads(body)
            except Exception:
                return {}
        return {}

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        url_path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        if url_path in ("/", "/index.html"):
            self._send_html(HTML_PAGE)
        elif url_path.startswith("/ticket/"):
            ticket_number = url_path.replace("/ticket/", "").strip()
            details = service.get_ticket_details(ticket_number)
            if details:
                self._send_html(render_mobile_ticket(details))
            else:
                self._send_html("<!DOCTYPE html><html><body style='font-family:sans-serif;text-align:center;padding:40px;'><h1>Ticket introuvable</h1><p>Ce ticket n'existe pas ou est erroné.</p></body></html>", status=404)
        elif url_path == "/api/system/info":
            self._send_json({
                "status": "SUCCESS",
                "local_ip": get_local_ip()
            })
        elif url_path == "/manifest.json":
            manifest = {
                "name": "Ma Caisse Enregistreuse Facile",
                "short_name": "Caisse",
                "start_url": "/",
                "display": "standalone",
                "background_color": "#1e293b",
                "theme_color": "#1e293b",
                "icons": [
                    {
                        "src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏪</text></svg>",
                        "sizes": "192x192 512x512",
                        "type": "image/svg+xml"
                    }
                ]
            }
            self._send_json(manifest)
        elif url_path == "/api/qr":
            ticket_num = query.get("ticket", [None])[0]
            text = query.get("text", [None])[0]
            if not text and ticket_num:
                host_header = self.headers.get("Host")
                proto_header = self.headers.get("X-Forwarded-Proto") or ("https" if self.headers.get("X-Forwarded-Ssl") == "on" else "http")
                if host_header and not host_header.startswith("127.0.0.1") and not host_header.startswith("localhost"):
                    text = f"{proto_header}://{host_header}/ticket/{ticket_num}"
                else:
                    ip = get_local_ip()
                    port = self.server.server_address[1]
                    text = f"http://{ip}:{port}/ticket/{ticket_num}"
            if not text:
                host_header = self.headers.get("Host")
                proto_header = self.headers.get("X-Forwarded-Proto") or ("https" if self.headers.get("X-Forwarded-Ssl") == "on" else "http")
                if host_header and not host_header.startswith("127.0.0.1") and not host_header.startswith("localhost"):
                    text = f"{proto_header}://{host_header}/"
                else:
                    text = f"http://{get_local_ip()}:{self.server.server_address[1]}/"

            try:
                import qrcode
                qr = qrcode.QRCode(
                    version=None,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=8,
                    border=3,
                )
                qr.add_data(text)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                payload = buf.getvalue()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(payload)))
                self.send_header("Cache-Control", "public, max-age=86400")
                self.end_headers()
                self.wfile.write(payload)
            except Exception as e:
                self._send_json({"status": "ERROR", "message": str(e)}, status=500)
        elif url_path == "/api/catalog":
            self._send_json(service.get_catalog())
        elif url_path == "/api/ticket":
            self._send_json(service.get_ticket_state())
        elif url_path == "/api/z_report":
            target_date = query.get("date", [None])[0]
            self._send_json(service.get_z_report(target_date))
        elif url_path == "/api/history":
            date_filter = query.get("date", [None])[0]
            limit_str = query.get("limit", ["100"])[0]
            try:
                limit = int(limit_str)
            except ValueError:
                limit = 100
            self._send_json(service.get_sales_history(limit=limit, date_filter=date_filter))
        elif url_path == "/api/ticket/detail":
            ticket_number = query.get("number", [""])[0]
            details = service.get_ticket_details(ticket_number)
            if details:
                self._send_json(details)
            else:
                self._send_json({"status": "ERROR", "message": "Ticket introuvable"}, status=404)
        elif url_path == "/api/company":
            self._send_json(service.get_company_info())
        elif url_path == "/api/fiscal_archive":
            self._send_json(service.export_fiscal_archive())
        elif url_path == "/api/categories":
            self._send_json(service.get_categories_summary())
        elif url_path == "/health":
            self._send_json({"status": "OK", "app": "caisse_enregistreuse"})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        url_path = self.path.split("?")[0]
        data = self._parse_json_body()

        if url_path == "/api/ticket/add":
            prod_id = int(data.get("product_id", 0))
            qty = int(data.get("quantity", 1))
            res = service.add_to_ticket(prod_id, qty)
            self._send_json(res)

        elif url_path == "/api/ticket/remove":
            prod_id = int(data.get("product_id", 0))
            res = service.remove_from_ticket(prod_id)
            self._send_json(res)

        elif url_path == "/api/ticket/delete_line":
            prod_id = int(data.get("product_id", 0))
            res = service.delete_ticket_line(prod_id)
            self._send_json(res)

        elif url_path == "/api/ticket/clear":
            res = service.clear_ticket()
            self._send_json(res)

        elif url_path == "/api/checkout":
            method = data.get("method", "Carte Bancaire")
            received = data.get("amount_received")
            if received is not None:
                received = float(received)
            res = service.checkout(method_str=method, amount_received=received)
            self._send_json(res)

        elif url_path == "/api/z_report/close":
            target_date = data.get("date")
            res = service.close_daily_z(target_date)
            self._send_json(res)

        elif url_path == "/api/company":
            res = service.update_company_info(**data)
            self._send_json(res)

        elif url_path == "/api/products/add":
            name = str(data.get("name", "Nouveau Produit"))
            price = float(data.get("price", 1.0))
            cat = str(data.get("category", "Divers"))
            tva = float(data.get("tva_rate", 10.0))
            new_id = service.add_custom_product(name=name, price=price, category=cat, tva_rate=tva)
            self._send_json({"status": "SUCCESS", "id": new_id})

        elif url_path == "/api/categories/rename":
            old_name = str(data.get("old_name", "")).strip()
            new_name = str(data.get("new_name", "")).strip()
            if not new_name:
                self._send_json({"status": "ERROR", "message": "Nouveau nom requis"}, status=400)
            else:
                res = service.rename_category(old_name, new_name)
                self._send_json(res)

        elif url_path == "/api/categories/delete":
            cat = str(data.get("category", "")).strip()
            reassign_to = data.get("reassign_to", "Divers")
            res = service.delete_category(cat, reassign_to=reassign_to)
            self._send_json(res)

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Réduit le bruit de la console pour une expérience utilisateur propre
        pass


def run_server(port: Optional[int] = None, open_browser: Optional[bool] = None):
    if port is None:
        port = int(os.environ.get("PORT", 8080))

    is_cloud = "PORT" in os.environ or "RENDER" in os.environ or "DYNO" in os.environ or os.environ.get("HEADLESS") == "1"
    if open_browser is None:
        open_browser = not is_cloud

    server_address = ("0.0.0.0", port)
    try:
        httpd = HTTPServer(server_address, CashRegisterHTTPHandler)
    except OSError:
        # Si le port est déjà occupé, tente le port suivant
        port = port + 1
        server_address = ("0.0.0.0", port)
        httpd = HTTPServer(server_address, CashRegisterHTTPHandler)

    local_ip = get_local_ip()
    url = f"http://127.0.0.1:{port}"
    net_url = f"http://{local_ip}:{port}"
    print("\n" + "=" * 70)
    print("🏪 MA CAISSE ENREGISTREUSE FACILE EST PRÊTE !")
    print(f"👉 Accès local : {url}")
    print(f"👉 Accès réseau local (Smartphones / QR Code) : {net_url}")
    print("👉 Pour quitter : appuyez sur Ctrl + C dans ce terminal")
    print("=" * 70 + "\n")

    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nFermeture propre de la caisse. À bientôt !")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lancement de la Caisse Enregistreuse")
    parser.add_argument("--port", type=int, default=8080, help="Port HTTP (défaut: 8080)")
    parser.add_argument("--no-browser", action="store_true", help="Ne pas ouvrir automatiquement le navigateur")
    args = parser.parse_args()

    run_server(port=args.port, open_browser=not args.no_browser)
