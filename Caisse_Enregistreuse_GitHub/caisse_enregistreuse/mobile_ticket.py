"""
Générateur de ticket de caisse dématérialisé pour smartphone (Loi AGEC).
Affiché lorsque le client flashe le QR Code avec son smartphone.
100% autonome, zéro dépendance externe, CSS responsive intégré.
"""

from typing import Dict, Any


def render_mobile_ticket(ticket: Dict[str, Any]) -> str:
    """
    Génère la page HTML complète du ticket électronique pour mobile.
    """
    co = ticket.get("company", {})
    items = ticket.get("items", [])
    tva_breakdown = ticket.get("tva_breakdown", {})
    tva_rows = list(tva_breakdown.values()) if isinstance(tva_breakdown, dict) else []

    is_duplicata = ticket.get("is_duplicata", False)
    ticket_title = "DUPLICATA DE TICKET DE CAISSE" if is_duplicata else "TICKET DE CAISSE DÉMATÉRIALISÉ"

    items_html = "".join(f"""
      <div class="item-row">
        <div class="item-desc">
          <div class="item-title">{i.get('name', 'Article')}</div>
          <div class="item-sub">{i.get('quantity', 1)} x {float(i.get('unit_price', 0.0)):.2f} € &bull; TVA {float(i.get('tva_rate', 10.0)):.1f}%</div>
        </div>
        <div class="item-price">{float(i.get('total_ttc', 0.0)):.2f} €</div>
      </div>
    """ for i in items)

    tva_html = "".join(f"""
      <tr>
        <td>{float(r.get('rate', 0.0)):.1f}%</td>
        <td>{float(r.get('base_ht', 0.0)):.2f} €</td>
        <td>{float(r.get('montant_tva', 0.0)):.2f} €</td>
        <td style="font-weight: 700;">{float(r.get('total_ttc', 0.0)):.2f} €</td>
      </tr>
    """ for r in tva_rows)

    change_block = ""
    if ticket.get("change_returned") is not None and float(ticket.get("change_returned", 0)) > 0:
        change_block = f"""
        <div class="meta-row">
          <span>Montant reçu</span>
          <span>{float(ticket.get('amount_received', 0.0)):.2f} €</span>
        </div>
        <div class="meta-row" style="color: #059669; font-weight: 700;">
          <span>Monnaie rendue</span>
          <span>{float(ticket.get('change_returned', 0.0)):.2f} €</span>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Ticket {ticket.get('ticket_number', '')} - {co.get('name', 'Ticket de caisse')}</title>
  <style>
    :root {{
      --primary: #2563eb;
      --primary-dark: #1d4ed8;
      --bg: #f1f5f9;
      --card-bg: #ffffff;
      --text: #0f172a;
      --text-muted: #64748b;
      --border: #e2e8f0;
      --success: #16a34a;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      display: flex;
      justify-content: center;
      padding: 16px 12px 32px 12px;
      min-height: 100vh;
    }}
    .ticket-container {{
      width: 100%;
      max-width: 440px;
      background: var(--card-bg);
      border-radius: 16px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      border: 1px solid var(--border);
    }}
    .header-band {{
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
      color: white;
      padding: 20px 18px;
      text-align: center;
    }}
    .brand-icon {{ font-size: 2rem; margin-bottom: 4px; }}
    .company-name {{ font-size: 1.15rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }}
    .company-sub {{ font-size: 0.78rem; color: #94a3b8; margin-top: 3px; line-height: 1.35; }}
    
    .status-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      margin-top: 10px;
      background: rgba(34, 197, 94, 0.18);
      color: #4ade80;
      font-size: 0.75rem;
      font-weight: 700;
      padding: 4px 12px;
      border-radius: 9999px;
      letter-spacing: 0.3px;
    }}
    .status-badge.duplicata {{
      background: rgba(239, 68, 68, 0.2);
      color: #fca5a5;
    }}

    .ticket-body {{ padding: 18px; display: flex; flex-direction: column; gap: 14px; }}
    
    .meta-box {{
      background: #f8fafc;
      border: 1px solid #edf2f7;
      border-radius: 10px;
      padding: 12px;
      font-size: 0.82rem;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .meta-row {{ display: flex; justify-content: space-between; align-items: center; }}
    .meta-label {{ color: var(--text-muted); }}
    .meta-value {{ font-weight: 700; color: var(--text); }}
    
    .divider {{ border: none; border-top: 1px dashed var(--border); margin: 6px 0; }}
    
    .section-title {{ font-size: 0.85rem; font-weight: 800; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.5px; margin-bottom: 6px; }}
    
    .items-list {{ display: flex; flex-direction: column; gap: 10px; }}
    .item-row {{ display: flex; justify-content: space-between; align-items: baseline; }}
    .item-title {{ font-size: 0.95rem; font-weight: 700; }}
    .item-sub {{ font-size: 0.75rem; color: var(--text-muted); margin-top: 2px; }}
    .item-price {{ font-size: 1rem; font-weight: 800; white-space: nowrap; margin-left: 8px; }}

    .total-card {{
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      border-radius: 12px;
      padding: 16px;
      margin-top: 6px;
    }}
    .total-title {{ font-size: 0.85rem; font-weight: 700; color: #166534; text-transform: uppercase; }}
    .total-amount {{ font-size: 2.2rem; font-weight: 900; color: #15803d; margin: 4px 0 8px 0; }}
    .subtotals {{ display: flex; justify-content: space-between; font-size: 0.82rem; color: #166534; }}

    .tva-table {{ width: 100%; border-collapse: collapse; font-size: 0.76rem; margin-top: 4px; }}
    .tva-table th {{ text-align: right; border-bottom: 1px solid var(--border); padding: 4px; color: var(--text-muted); }}
    .tva-table th:first-child {{ text-align: left; }}
    .tva-table td {{ text-align: right; padding: 5px 4px; border-bottom: 1px solid #f1f5f9; }}
    .tva-table td:first-child {{ text-align: left; font-weight: 700; }}

    .seal-box {{
      background: #fafafa;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 10px;
      font-size: 0.70rem;
      color: #64748b;
      word-break: break-all;
      text-align: center;
      line-height: 1.35;
    }}
    .seal-hash {{ font-family: monospace; font-size: 0.65rem; color: #0f172a; margin-top: 3px; display: block; }}

    .actions-bar {{
      padding: 14px 18px 20px 18px;
      background: white;
      border-top: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    .btn-action {{
      width: 100%;
      padding: 14px;
      border-radius: 10px;
      border: none;
      font-size: 0.95rem;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: background 0.15s;
    }}
    .btn-print {{ background: var(--primary); color: white; }}
    .btn-print:hover {{ background: var(--primary-dark); }}

    @media print {{
      body {{ background: white; padding: 0; }}
      .actions-bar {{ display: none !important; }}
      .ticket-container {{ box-shadow: none; border: none; max-width: 100%; }}
    }}
  </style>
</head>
<body>

  <div class="ticket-container">
    <div class="header-band">
      <div class="brand-icon">🏪</div>
      <h1 class="company-name">{co.get('name', 'ÉTABLISSEMENT')}</h1>
      <div class="company-sub">{co.get('legal_form', '')}</div>
      <div class="company-sub">{co.get('address', '')}</div>
      <div class="company-sub">Tél : {co.get('phone', '')}</div>
      <div class="company-sub">SIRET : {co.get('siret', '')} | {co.get('rcs', '')}</div>
      <div class="company-sub">Code NAF : {co.get('code_naf', '')} | N° TVA : {co.get('tva_intra', '')}</div>
      
      <div style="font-size: 0.75rem; color: #cbd5e1; margin-top: 8px; font-weight: 600;">
        🌱 E-Ticket Dématérialisé &bull; Loi Anti-Gaspillage AGEC
      </div>
      
      <div class="status-badge {'duplicata' if is_duplicata else ''}">
        {'⚠️ ' + ticket_title if is_duplicata else '✅ Justificatif d\'Achat Numérique Conforme'}
      </div>
    </div>

    <div class="ticket-body">
      <div class="meta-box">
        <div class="meta-row">
          <span class="meta-label">Ticket N°</span>
          <span class="meta-value" style="font-family: monospace;">{ticket.get('ticket_number', '')}</span>
        </div>
        <div class="meta-row">
          <span class="meta-label">Date & Heure</span>
          <span class="meta-value">{ticket.get('created_at', '')}</span>
        </div>
        <div class="meta-row">
          <span class="meta-label">Caisse</span>
          <span class="meta-value">{co.get('pos_id', 'CAISSE-01')}</span>
        </div>
        <div class="meta-row">
          <span class="meta-label">Mode de règlement</span>
          <span class="meta-value" style="color: var(--primary);">{ticket.get('payment_method', 'Comptant')}</span>
        </div>
        {change_block}
      </div>

      <div>
        <div class="section-title">Articles ({len(items)})</div>
        <div class="items-list">
          {items_html}
        </div>
      </div>

      <div class="total-card">
        <div class="total-title">Total Règlement TTC</div>
        <div class="total-amount">{float(ticket.get('total_ttc', 0.0)):.2f} €</div>
        <div class="subtotals">
          <span>Dont Total HT : <strong>{float(ticket.get('total_ht', 0.0)):.2f} €</strong></span>
          <span>TVA : <strong>{float(ticket.get('total_tva', 0.0)):.2f} €</strong></span>
        </div>
      </div>

      <div>
        <div class="section-title">VENTILATION DE LA TVA (CGI ART. 286)</div>
        <table class="tva-table">
          <thead>
            <tr>
              <th>Taux</th>
              <th>Base HT</th>
              <th>Montant TVA</th>
              <th>Total TTC</th>
            </tr>
          </thead>
          <tbody>
            {tva_html}
          </tbody>
        </table>
      </div>

      <div class="seal-box">
        🔒 <strong>Scellement Fiscal NF 525 (Art. 88 LF 2015-1785)</strong><br>
        Système d'encaissement certifié conforme CGI art. 286, I-3° bis.<br>
        Ce ticket électronique vaut justificatif d'achat opposable.<br>
        <span class="seal-hash">Empreinte : {ticket.get('signature', '')}</span>
      </div>
    </div>

    <div class="actions-bar">
      <button class="btn-action btn-print" onclick="window.print()">
        📥 Enregistrer en PDF / Imprimer
      </button>
    </div>
  </div>

</body>
</html>
"""
