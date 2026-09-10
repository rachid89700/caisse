"""
Interface Web Tactile et Réactive pour la Caisse Enregistreuse.
Fournit le HTML, CSS et JavaScript modernes sans aucune dépendance externe.
"""

try:
    from .qrcode_js import QR_CODE_JS
except ImportError:
    from qrcode_js import QR_CODE_JS

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="Ma Caisse">
  <meta name="theme-color" content="#1e293b">
  <link rel="manifest" href="/manifest.json">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🏪</text></svg>">
  <link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🏪</text></svg>">
  <title>🏪 Ma Caisse Enregistreuse Facile</title>
  <style>
    :root {
      --primary: #2563eb;
      --primary-dark: #1d4ed8;
      --success: #10b981;
      --success-dark: #059669;
      --danger: #ef4444;
      --danger-dark: #dc2626;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --border: #e2e8f0;
      --accent: #f59e0b;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    body { background-color: var(--bg); color: var(--text-main); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }

    /* Top Bar */
    header {
      background: #1e293b;
      color: white;
      padding: 12px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .brand { display: flex; align-items: center; gap: 12px; font-size: 1.3rem; font-weight: 700; }
    .header-actions { display: flex; gap: 10px; align-items: center; }
    .btn-header {
      background: rgba(255,255,255,0.15);
      border: 1px solid rgba(255,255,255,0.25);
      color: white;
      padding: 8px 14px;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: background 0.2s;
    }
    .btn-header:hover { background: rgba(255,255,255,0.25); }
    .btn-z { background: #d97706; }
    .btn-z:hover { background: #b45309; }

    /* Main Grid Layout */
    .pos-container {
      display: grid;
      grid-template-columns: 1fr 420px;
      flex: 1;
      overflow: hidden;
    }

    /* Left Panel: Catalog */
    .catalog-panel {
      display: flex;
      flex-direction: column;
      padding: 16px;
      gap: 12px;
      overflow: hidden;
      background: #f1f5f9;
    }
    .search-row { display: flex; gap: 10px; flex-shrink: 0; }
    .search-input {
      flex: 1;
      padding: 12px 16px;
      font-size: 1.05rem;
      border: 2px solid var(--border);
      border-radius: 10px;
      outline: none;
      background: white;
      transition: border-color 0.2s;
    }
    .search-input:focus { border-color: var(--primary); }

    /* Category Tabs */
    .category-tabs {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      padding: 2px 0 4px 0;
      flex-shrink: 0;
    }
    .tab-btn {
      padding: 10px 18px;
      background: white;
      border: 1px solid var(--border);
      border-radius: 10px;
      cursor: pointer;
      font-weight: 600;
      color: var(--text-muted);
      white-space: nowrap;
      transition: all 0.2s;
      flex-shrink: 0;
    }
    .tab-btn.active {
      background: var(--primary);
      color: white;
      border-color: var(--primary);
      box-shadow: 0 2px 4px rgba(37,99,235,0.25);
    }

    /* Product Cards Grid */
    .products-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
      gap: 12px;
      flex: 1;
      overflow-y: auto;
      padding-bottom: 20px;
      align-content: start;
    }
    .product-card {
      background: white;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      cursor: pointer;
      min-height: 110px;
      user-select: none;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      transition: transform 0.1s, box-shadow 0.1s, border-color 0.1s;
      border-left: 6px solid var(--primary);
    }
    .product-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 10px rgba(0,0,0,0.08);
      border-color: var(--primary);
    }
    .product-card:active { transform: scale(0.98); }
    .product-name { font-weight: 600; font-size: 0.95rem; margin-bottom: 8px; line-height: 1.3; }
    .product-price { font-size: 1.3rem; font-weight: 800; color: #0f172a; text-align: right; }

    /* Right Panel: Current Ticket */
    .ticket-panel {
      background: white;
      border-left: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      box-shadow: -2px 0 10px rgba(0,0,0,0.03);
    }
    .ticket-header {
      padding: 16px;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #fafafa;
    }
    .ticket-title { font-size: 1.15rem; font-weight: 700; display: flex; align-items: center; gap: 8px; }
    .btn-clear {
      background: #fee2e2;
      color: var(--danger);
      border: none;
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      font-size: 0.85rem;
    }
    .btn-clear:hover { background: #fecaca; }

    .ticket-items-list {
      flex: 1;
      overflow-y: auto;
      padding: 12px 16px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .ticket-empty {
      color: var(--text-muted);
      text-align: center;
      margin-top: 60px;
      font-size: 1rem;
    }

    .ticket-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #f8fafc;
      padding: 10px 12px;
      border-radius: 8px;
      border: 1px solid #edf2f7;
    }
    .item-info { flex: 1; }
    .item-name { font-weight: 600; font-size: 0.95rem; }
    .item-unit-price { font-size: 0.8rem; color: var(--text-muted); }
    .qty-controls { display: flex; align-items: center; gap: 6px; margin: 0 10px; }
    .btn-qty {
      width: 28px;
      height: 28px;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: white;
      font-size: 1rem;
      font-weight: bold;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .btn-qty:hover { background: #e2e8f0; }
    .qty-number { font-weight: 700; min-width: 24px; text-align: center; }
    .item-total { font-weight: 700; font-size: 1.05rem; min-width: 60px; text-align: right; }
    .btn-del {
      background: none;
      border: none;
      color: #94a3b8;
      cursor: pointer;
      padding: 4px;
      margin-left: 6px;
    }
    .btn-del:hover { color: var(--danger); }

    /* Ticket Totals Section */
    .ticket-summary {
      padding: 16px;
      border-top: 1px solid var(--border);
      background: #fafafa;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .summary-line { display: flex; justify-content: space-between; font-size: 0.9rem; color: var(--text-muted); }
    .total-line {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 8px;
      padding-top: 8px;
      border-top: 2px dashed #cbd5e1;
    }
    .total-label { font-size: 1.25rem; font-weight: 800; color: #0f172a; }
    .total-amount { font-size: 1.9rem; font-weight: 900; color: #16a34a; }

    /* Payment Buttons */
    .payment-section {
      padding: 16px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      background: white;
      border-top: 1px solid var(--border);
    }
    .btn-pay {
      padding: 16px;
      border: none;
      border-radius: 10px;
      font-size: 1.1rem;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
      color: white;
      transition: opacity 0.15s, transform 0.1s;
    }
    .btn-pay:hover { opacity: 0.92; transform: translateY(-1px); }
    .btn-pay:active { transform: scale(0.98); }
    .btn-cb { background: #2563eb; }
    .btn-cash { background: #16a34a; }
    .btn-full-width { grid-column: span 2; background: #64748b; font-size: 0.95rem; padding: 10px; }

    /* Responsive Tablettes & Écrans Tactiles */
    @media (max-width: 960px) {
      .pos-container {
        grid-template-columns: 1fr 350px;
      }
      .brand { font-size: 1.1rem; }
      .btn-header { padding: 6px 10px; font-size: 0.82rem; }
      .products-grid { grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 8px; }
      .product-card { padding: 12px 8px; min-height: 80px; }
      .product-card .price { font-size: 1.05rem; }
    }

    @media (max-width: 720px) {
      .pos-container {
        grid-template-columns: 1fr;
        grid-template-rows: 1fr auto;
        height: calc(100vh - 60px);
      }
      .ticket-panel {
        max-height: 45vh;
        box-shadow: 0 -4px 12px rgba(0,0,0,0.1);
      }
      .header-actions {
        flex-wrap: wrap;
        gap: 4px;
      }
    }

    /* Modals */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.6);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 100;
    }
    .modal-card {
      background: white;
      border-radius: 14px;
      width: 480px;
      max-width: 95vw;
      padding: 24px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.2);
      display: flex;
      flex-direction: column;
      gap: 16px;
      max-height: 90vh;
      overflow-y: auto;
    }
    .modal-header { display: flex; justify-content: space-between; align-items: center; font-size: 1.25rem; font-weight: 700; }
    .close-modal { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #94a3b8; }
    .close-modal:hover { color: #0f172a; }

    /* Cash Calculator in Modal */
    .cash-display {
      background: #f8fafc;
      border: 2px solid var(--border);
      border-radius: 10px;
      padding: 16px;
      text-align: center;
    }
    .cash-due { font-size: 1.1rem; color: var(--text-muted); }
    .cash-total { font-size: 2.2rem; font-weight: 900; color: #0f172a; }
    .cash-bills { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 12px 0; }
    .btn-bill {
      padding: 12px;
      background: #e2e8f0;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      font-size: 1.1rem;
      font-weight: 700;
      cursor: pointer;
    }
    .btn-bill:hover { background: #cbd5e1; }
    .change-banner {
      background: #ecfdf5;
      border: 2px solid #10b981;
      border-radius: 10px;
      padding: 14px;
      text-align: center;
      display: none;
    }
    .change-label { font-size: 0.95rem; font-weight: 600; color: #047857; }
    .change-value { font-size: 2.2rem; font-weight: 900; color: #059669; }

    /* Receipt & Compliance Styles */
    .receipt-box {
      background: #fafafa;
      border: 1px dashed #94a3b8;
      padding: 16px;
      border-radius: 8px;
      font-family: 'Courier New', Courier, monospace;
      font-size: 0.85rem;
      color: #0f172a;
      line-height: 1.35;
    }
    .receipt-header-center { text-align: center; margin-bottom: 8px; }
    .receipt-company-title { font-size: 1.05rem; font-weight: 800; margin: 0; text-transform: uppercase; }
    .receipt-company-sub { font-size: 0.75rem; color: #475569; }
    .receipt-title { font-weight: 800; font-size: 0.9rem; text-align: center; margin: 6px 0 2px 0; letter-spacing: 0.5px; }
    .receipt-meta { font-size: 0.78rem; text-align: center; color: #334155; margin-bottom: 6px; }
    .receipt-dashed-line { border: none; border-top: 1px dashed #94a3b8; margin: 8px 0; }
    .receipt-dotted-line { border: none; border-top: 1px dotted #cbd5e1; margin: 6px 0; }
    .receipt-item-row { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 3px; }
    .receipt-item-sub { font-size: 0.75rem; color: #64748b; }
    .receipt-item-price { font-weight: 700; white-space: nowrap; margin-left: 8px; }
    .receipt-total-row { display: flex; justify-content: space-between; font-weight: 900; font-size: 1.15rem; margin: 6px 0; }
    .receipt-subtotal-row { display: flex; justify-content: space-between; font-size: 0.82rem; color: #334155; margin: 2px 0; }
    .receipt-table-tva { width: 100%; border-collapse: collapse; font-size: 0.75rem; margin: 6px 0; }
    .receipt-table-tva th { text-align: right; border-bottom: 1px solid #cbd5e1; padding: 2px 4px; font-weight: 700; }
    .receipt-table-tva th:first-child { text-align: left; }
    .receipt-table-tva td { text-align: right; padding: 2px 4px; }
    .receipt-table-tva td:first-child { text-align: left; }
    .receipt-legal-block { text-align: center; font-size: 0.70rem; color: #64748b; margin-top: 8px; line-height: 1.25; }
    .receipt-signature-block { margin-top: 6px; padding-top: 6px; border-top: 1px dotted #cbd5e1; text-align: center; font-size: 0.68rem; color: #64748b; word-break: break-all; }

    /* Receipt Print Style */
    @media print {
      body * { visibility: hidden !important; }
      .print-visible, .print-visible * { visibility: visible !important; }
      .print-visible { position: absolute !important; left: 0 !important; top: 0 !important; width: 80mm !important; padding: 6px !important; font-size: 11px !important; }
    }
  </style>
</head>
<body>

  <!-- Top Bar -->
  <header>
    <div class="brand">
      <span>🏪</span>
      <div>
        <div style="font-weight: 800; font-size: 1.1rem; line-height: 1.2;">Ma Caisse Enregistreuse</div>
        <div id="header-company-subtitle" style="font-size: 0.76rem; font-weight: 600; color: #93c5fd; letter-spacing: 0.3px;"></div>
      </div>
    </div>
    <div class="header-actions">
      <button class="btn-header" style="background: #4338ca;" onclick="openHistoryModal()" title="Consulter l'historique des ventes et tickets">📜 Historique</button>
      <button class="btn-header" style="background: #0f766e;" onclick="openCompanyModal()" title="Modifier la dénomination sociale et les mentions légales">🏢 Infos Établissement</button>
      <button class="btn-header" style="background: #475569;" onclick="openCategoryManagerModal()">🏷️ Gérer Catégories</button>
      <button class="btn-header btn-z" onclick="openZReport()">📊 Clôture du Jour (Z)</button>
      <button class="btn-header" onclick="openAddProductModal()">➕ Nouveau Produit</button>
      <span id="live-clock" style="font-size: 0.95rem; font-weight: 600; margin-left: 10px; opacity: 0.85;"></span>
    </div>
  </header>

  <!-- POS Main Layout -->
  <div class="pos-container">
    
    <!-- Left: Catalog -->
    <div class="catalog-panel">
      <div class="search-row">
        <input type="text" id="search-input" class="search-input" placeholder="🔍 Rechercher un produit par nom..." oninput="filterProducts()">
      </div>

      <!-- Category Filter Tabs -->
      <div class="category-tabs" id="category-tabs">
        <!-- Rendered dynamically -->
      </div>

      <!-- Products Grid -->
      <div class="products-grid" id="products-grid">
        <!-- Rendered dynamically -->
      </div>
    </div>

    <!-- Right: Ticket -->
    <div class="ticket-panel">
      <div class="ticket-header">
        <div class="ticket-title">
          <span>🧾</span>
          <span>Ticket en cours (<span id="ticket-badge">0</span>)</span>
        </div>
        <button class="btn-clear" onclick="clearTicket()">🗑️ Vider</button>
      </div>

      <!-- Items List -->
      <div class="ticket-items-list" id="ticket-items">
        <div class="ticket-empty">Aucun article dans le ticket.<br>Touchez un produit à gauche pour l'ajouter.</div>
      </div>

      <!-- Totals Summary -->
      <div class="ticket-summary">
        <div class="summary-line">
          <span>Total HT</span>
          <span id="sum-ht">0.00 €</span>
        </div>
        <div class="summary-line">
          <span>TVA</span>
          <span id="sum-tva">0.00 €</span>
        </div>
        <div class="total-line">
          <span class="total-label">TOTAL TTC</span>
          <span class="total-amount" id="sum-ttc">0.00 €</span>
        </div>
      </div>

      <!-- Fast Payment Actions -->
      <div class="payment-section">
        <button class="btn-pay btn-cb" onclick="payWithCard()">
          <span>💳</span>
          <span>Carte Bancaire</span>
        </button>
        <button class="btn-pay btn-cash" onclick="openCashModal()">
          <span>💵</span>
          <span>Espèces</span>
        </button>
        <button class="btn-pay btn-full-width" onclick="payWithOther()">
          <span>🎟️ Ticket Restaurant / Autre</span>
        </button>
      </div>
    </div>

  </div>

  <!-- Modal Espèces / Rendu de Monnaie -->
  <div class="modal-overlay" id="cash-modal">
    <div class="modal-card">
      <div class="modal-header">
        <span>💵 Règlement en Espèces</span>
        <button class="close-modal" onclick="closeModal('cash-modal')">&times;</button>
      </div>
      <div class="cash-display">
        <div class="cash-due">Total à payer</div>
        <div class="cash-total" id="modal-cash-total">0.00 €</div>
      </div>
      <div>
        <label style="font-weight: 600; font-size: 0.95rem;">Montant reçu du client (€) :</label>
        <input type="number" step="0.01" id="cash-received-input" class="search-input" style="width: 100%; font-size: 1.4rem; font-weight: bold; margin-top: 6px;" oninput="updateChangeCalculation()">
      </div>
      <div class="cash-bills">
        <button class="btn-bill" onclick="addCashBill(5)">5 €</button>
        <button class="btn-bill" onclick="addCashBill(10)">10 €</button>
        <button class="btn-bill" onclick="addCashBill(20)">20 €</button>
        <button class="btn-bill" onclick="addCashBill(50)">50 €</button>
      </div>
      <button class="tab-btn" style="text-align: center;" onclick="setExactCash()">Montant Exact</button>
      <div class="change-banner" id="change-banner">
        <div class="change-label">MONNAIE À RENDRE</div>
        <div class="change-value" id="change-value">0.00 €</div>
      </div>
      <button class="btn-pay btn-cash" style="width: 100%;" id="btn-validate-cash" onclick="submitCashPayment()" disabled>
        ✅ Valider la Vente & Ouvrir Tiroir
      </button>
    </div>
  </div>

  <!-- Modal Ticket Imprimable & E-Ticket QR Code -->
  <div class="modal-overlay" id="receipt-modal">
    <div class="modal-card" style="max-width: 540px; width: 95%;">
      <div class="modal-header">
        <span id="receipt-modal-title">📱 E-Ticket Dématérialisé (QR Code)</span>
        <button class="close-modal" onclick="closeModal('receipt-modal')">&times;</button>
      </div>

      <!-- Sélecteur d'onglets : QR Code vs Ticket Papier -->
      <div style="display: flex; gap: 8px; margin-bottom: 12px;">
        <button id="btn-tab-qr" class="tab-btn active" style="flex: 1; text-align: center;" onclick="switchReceiptTab('qr')">
          📱 E-Ticket QR Code
        </button>
        <button id="btn-tab-paper" class="tab-btn" style="flex: 1; text-align: center;" onclick="switchReceiptTab('paper')">
          🧾 Ticket Papier
        </button>
      </div>

      <!-- Vue 1 : QR Code Smartphone (Loi AGEC) -->
      <div id="receipt-qr-view" style="display: flex; flex-direction: column; align-items: center; text-align: center; gap: 10px; padding: 6px 0;">
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 8px 14px; font-size: 0.85rem; color: #166534; font-weight: 600; width: 100%;">
          🌱 Ticket Dématérialisé &bull; Loi Anti-Gaspillage AGEC
        </div>

        <div style="font-size: 0.92rem; color: #334155; line-height: 1.35;">
          Approchez l'appareil photo de votre smartphone pour ouvrir votre reçu :
        </div>

        <div id="receipt-qr-container" style="background: white; padding: 14px; border-radius: 16px; border: 2px solid #e2e8f0; box-shadow: 0 4px 14px rgba(0,0,0,0.08); margin: 4px 0; display: flex; justify-content: center; align-items: center;">
          <img id="receipt-qr-img" src="" width="220" height="220" style="display: block; border-radius: 6px;" alt="QR Code E-Ticket">
        </div>

        <div style="font-weight: 800; font-size: 1.35rem; color: #15803d;" id="receipt-qr-total">
          0.00 €
        </div>

        <div style="font-size: 0.8rem; color: #64748b;" id="receipt-qr-meta">
          Ticket N° TCK-...
        </div>

        <div style="display: flex; gap: 8px; width: 100%; margin-top: 4px;">
          <a id="receipt-qr-link" href="#" target="_blank" class="tab-btn" style="flex: 1; text-align: center; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 6px; font-weight: 700; color: #2563eb; background: #eff6ff; border-color: #bfdbfe;">
            🔗 Ouvrir sur l'appareil
          </a>
          <button class="tab-btn" style="flex: 1; text-align: center;" onclick="copyReceiptLink()">
            📋 Copier le lien
          </button>
        </div>
      </div>

      <!-- Vue 2 : Ticket thermique traditionnel -->
      <div id="receipt-paper-view" style="display: none;">
        <div id="printable-receipt" style="background: #fafafa; border: 1px dashed #94a3b8; padding: 16px; border-radius: 8px; font-family: monospace; max-height: 480px; overflow-y: auto;">
          <!-- Rempli dynamiquement en JS -->
        </div>
      </div>

      <!-- Boutons d'actions -->
      <div style="display: flex; gap: 10px; margin-top: 14px; padding-top: 10px; border-top: 1px solid #e2e8f0;">
        <button class="btn-header" style="background: #1e293b; flex: 1; justify-content: center;" onclick="printPaperTicket()">🖨️ Imprimer Papier</button>
        <button class="btn-pay btn-cash" style="flex: 1;" id="btn-receipt-next" onclick="closeModal('receipt-modal')">Client Suivant ➡️</button>
      </div>
    </div>
  </div>

  <!-- Modal Rapport Z de Caisse -->
  <div class="modal-overlay" id="z-modal">
    <div class="modal-card">
      <div class="modal-header">
        <span>📊 Clôture de Caisse (Rapport Z)</span>
        <button class="close-modal" onclick="closeModal('z-modal')">&times;</button>
      </div>
      <div id="z-content" style="display: flex; flex-direction: column; gap: 12px;">
        <!-- Filled dynamically -->
      </div>
      <div style="display: flex; gap: 10px;">
        <button class="btn-header" style="background: #1e293b; flex: 1; justify-content: center;" onclick="window.print()">🖨️ Imprimer Rapport Z</button>
        <button class="tab-btn" style="flex: 1;" onclick="closeModal('z-modal')">Fermer</button>
      </div>
    </div>
  </div>

  <!-- Modal Ajout Produit -->
  <div class="modal-overlay" id="product-modal">
    <div class="modal-card">
      <div class="modal-header">
        <span>➕ Ajouter un Nouveau Produit</span>
        <button class="close-modal" onclick="closeModal('product-modal')">&times;</button>
      </div>
      <form onsubmit="submitNewProduct(event)" style="display: flex; flex-direction: column; gap: 12px;">
        <div>
          <label style="font-weight: 600; font-size: 0.9rem;">Nom de l'article :</label>
          <input type="text" id="new-prod-name" class="search-input" style="width: 100%; margin-top: 4px;" required placeholder="Ex: Baguette Céréales">
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
          <div>
            <label style="font-weight: 600; font-size: 0.9rem;">Prix TTC (€) :</label>
            <input type="number" step="0.01" min="0" id="new-prod-price" class="search-input" style="width: 100%; margin-top: 4px;" required placeholder="1.50">
          </div>
          <div>
            <label style="font-weight: 600; font-size: 0.9rem;">Taux TVA (%) :</label>
            <select id="new-prod-tva" class="search-input" style="width: 100%; margin-top: 4px;">
              <option value="5.5">5.5% (Alimentaire de base)</option>
              <option value="10.0" selected>10.0% (Snack / Restauration)</option>
              <option value="20.0">20.0% (Alcool / Standard)</option>
            </select>
          </div>
        </div>
        <div>
          <label style="font-weight: 600; font-size: 0.9rem;">Catégorie :</label>
          <input type="text" id="new-prod-cat" class="search-input" style="width: 100%; margin-top: 4px;" required placeholder="Ex: Boulangerie, Boissons, Plats">
        </div>
        <button type="submit" class="btn-pay btn-cash" style="margin-top: 10px;">Enregistrer le Produit</button>
      </form>
    </div>
  </div>

  <!-- Modal Gestion des Catégories -->
  <div class="modal-overlay" id="category-modal">
    <div class="modal-card" style="width: 540px;">
      <div class="modal-header">
        <span>🏷️ Gestion des Catégories</span>
        <button class="close-modal" onclick="closeModal('category-modal')">&times;</button>
      </div>
      <p style="font-size: 0.9rem; color: var(--text-muted);">
        Modifiez le nom de vos catégories ou supprimez-en. Vos articles seront automatiquement mis à jour.
      </p>

      <div id="categories-manage-list" style="display: flex; flex-direction: column; gap: 8px; max-height: 380px; overflow-y: auto; padding: 4px 0;">
        <!-- Rempli dynamiquement en JS -->
      </div>

      <div style="display: flex; justify-content: flex-end; margin-top: 8px;">
        <button class="btn-pay btn-cash" style="padding: 10px 24px; font-size: 0.95rem;" onclick="closeModal('category-modal')">Fermer</button>
      </div>
    </div>
  </div>

  <!-- Modal Identité Légale / Infos Établissement -->
  <div class="modal-overlay" id="company-modal">
    <div class="modal-card" style="max-width: 640px; width: 95%;">
      <div class="modal-header">
        <span>🏢 Identification Légale de l'Établissement</span>
        <button class="close-modal" onclick="closeModal('company-modal')">&times;</button>
      </div>
      <div style="background: #f0fdfa; border: 1px solid #ccfbf1; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; font-size: 0.85rem; color: #0f766e; line-height: 1.4;">
        ℹ️ <strong>Saisie libre des mentions légales obligatoires (Art. R123-237 Code de commerce & CGI art. 286) :</strong><br>
        Vous pouvez modifier la <strong>dénomination sociale</strong> et ces coordonnées à tout moment. Toute modification est immédiatement enregistrée et appliquée sur vos prochains tickets de caisse et rapports Z.
      </div>

      <form onsubmit="saveCompanyInfo(event)" style="display: flex; flex-direction: column; gap: 12px;">
        <div>
          <label style="font-weight: 700; font-size: 0.92rem; color: #1e293b;">Dénomination Sociale / Nom Commercial * :</label>
          <input type="text" id="co-name" class="search-input" style="width: 100%; margin-top: 4px; font-weight: 700; font-size: 1rem; border-color: #0f766e;" required placeholder="Ex: BOULANGERIE DU COMMERCE">
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
          <div>
            <label style="font-weight: 600; font-size: 0.85rem;">Forme Juridique & Capital :</label>
            <input type="text" id="co-legal-form" class="search-input" style="width: 100%; margin-top: 4px;" placeholder="Ex: SARL au capital de 15 000 € / SASU / Micro-entreprise">
          </div>
          <div>
            <label style="font-weight: 600; font-size: 0.85rem;">Téléphone :</label>
            <input type="text" id="co-phone" class="search-input" style="width: 100%; margin-top: 4px;" placeholder="Ex: 01 42 68 00 00">
          </div>
        </div>

        <div>
          <label style="font-weight: 600; font-size: 0.85rem;">Adresse Postale Complète :</label>
          <input type="text" id="co-address" class="search-input" style="width: 100%; margin-top: 4px;" placeholder="Ex: 12 Rue de la République, 75001 Paris">
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
          <div>
            <label style="font-weight: 600; font-size: 0.85rem;">Numéro SIRET (14 chiffres) :</label>
            <input type="text" id="co-siret" class="search-input" style="width: 100%; margin-top: 4px;" placeholder="Ex: 834 567 890 00018">
          </div>
          <div>
            <label style="font-weight: 600; font-size: 0.85rem;">Registre du Commerce (RCS) :</label>
            <input type="text" id="co-rcs" class="search-input" style="width: 100%; margin-top: 4px;" placeholder="Ex: RCS Paris B 834 567 890">
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
          <div>
            <label style="font-weight: 600; font-size: 0.85rem;">Code NAF / APE :</label>
            <input type="text" id="co-naf" class="search-input" style="width: 100%; margin-top: 4px;" placeholder="Ex: 1071C">
          </div>
          <div>
            <label style="font-weight: 600; font-size: 0.85rem;">N° TVA Intracomm. :</label>
            <input type="text" id="co-tva-intra" class="search-input" style="width: 100%; margin-top: 4px;" placeholder="Ex: FR 45 834567890">
          </div>
          <div>
            <label style="font-weight: 600; font-size: 0.85rem;">Identifiant Caisse :</label>
            <input type="text" id="co-pos-id" class="search-input" style="width: 100%; margin-top: 4px;" placeholder="Ex: CAISSE-01">
          </div>
        </div>

        <div id="company-save-feedback" style="display: none; padding: 10px 14px; border-radius: 6px; font-size: 0.88rem; font-weight: 600; margin-top: 4px;"></div>

        <div style="display: flex; gap: 10px; margin-top: 10px;">
          <button type="submit" class="btn-pay" style="background: #0f766e; flex: 2; padding: 12px; font-size: 0.95rem; justify-content: center;">
            💾 Enregistrer l'Établissement
          </button>
          <button type="button" class="tab-btn" style="flex: 1;" onclick="closeModal('company-modal')">
            Fermer
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- Modal Historique des Ventes & Tickets -->
  <div class="modal-overlay" id="history-modal">
    <div class="modal-card" style="max-width: 840px; width: 96%; max-height: 90vh; display: flex; flex-direction: column;">
      <div class="modal-header">
        <span>📜 Historique des Ventes & Tickets</span>
        <button class="close-modal" onclick="closeModal('history-modal')">&times;</button>
      </div>

      <!-- Filtres et Recherche -->
      <div style="display: flex; gap: 10px; align-items: center; justify-content: space-between; flex-wrap: wrap; margin-bottom: 12px;">
        <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
          <button id="btn-hist-today" class="tab-btn active" onclick="setHistoryFilter('today')">Aujourd'hui</button>
          <button id="btn-hist-all" class="tab-btn" onclick="setHistoryFilter('all')">Tous les tickets</button>
          <div style="display: flex; align-items: center; gap: 6px; background: #f1f5f9; padding: 4px 8px; border-radius: 6px; border: 1px solid #cbd5e1;">
            <span style="font-size: 0.82rem; font-weight: 700; color: #475569;">📅 Choisir une date :</span>
            <input type="date" id="hist-date-picker" style="border: 1px solid #94a3b8; border-radius: 4px; padding: 3px 6px; font-size: 0.82rem;" onchange="setHistoryFilter('date', this.value)">
          </div>
        </div>
        <div style="flex: 1; min-width: 220px; max-width: 320px;">
          <input type="text" id="hist-search-input" class="search-input" placeholder="🔍 Filtrer par N° ticket, article..." style="width: 100%; padding: 6px 12px; font-size: 0.88rem;" oninput="filterHistoryList()">
        </div>
      </div>

      <!-- Bandeau KPI Synthèse -->
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 14px;">
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; text-align: center;">
          <div style="color: #64748b; font-size: 0.78rem; font-weight: 700; text-transform: uppercase;">Total Ventes (TTC)</div>
          <div id="hist-kpi-total" style="font-size: 1.45rem; font-weight: 900; color: #16a34a; margin-top: 2px;">0.00 €</div>
        </div>
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; text-align: center;">
          <div style="color: #64748b; font-size: 0.78rem; font-weight: 700; text-transform: uppercase;">Nombre de Tickets</div>
          <div id="hist-kpi-count" style="font-size: 1.45rem; font-weight: 900; color: #1e293b; margin-top: 2px;">0</div>
        </div>
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; text-align: center;">
          <div style="color: #64748b; font-size: 0.78rem; font-weight: 700; text-transform: uppercase;">Panier Moyen</div>
          <div id="hist-kpi-basket" style="font-size: 1.45rem; font-weight: 900; color: #2563eb; margin-top: 2px;">0.00 €</div>
        </div>
      </div>

      <!-- Liste des Tickets -->
      <div id="history-tickets-list" style="flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; max-height: 420px; padding-right: 4px;">
        <!-- Rempli dynamiquement en JS -->
      </div>

      <div style="display: flex; justify-content: flex-end; margin-top: 12px; padding-top: 10px; border-top: 1px solid #e2e8f0;">
        <button class="tab-btn" style="padding: 8px 20px; font-size: 0.9rem;" onclick="closeModal('history-modal')">Fermer</button>
      </div>
    </div>
  </div>

  <script>
    /* __QRCODE_JS__ */

    // Gestion du QR Code E-Ticket (Loi AGEC) et Réseau Local
    let systemInfo = { local_ip: '127.0.0.1' };
    let currentTicketData = null;
    let currentTicketUrl = '';

    async function loadSystemInfo() {
      try {
        const res = await fetch('/api/system/info');
        systemInfo = await res.json();
      } catch (err) {
        console.error('Erreur chargement infos reseau:', err);
      }
    }

    function switchReceiptTab(tab) {
      const btnQr = document.getElementById('btn-tab-qr');
      const btnPaper = document.getElementById('btn-tab-paper');
      const qrView = document.getElementById('receipt-qr-view');
      const paperView = document.getElementById('receipt-paper-view');
      const modalTitle = document.getElementById('receipt-modal-title');

      if (tab === 'qr') {
        if (btnQr) btnQr.classList.add('active');
        if (btnPaper) btnPaper.classList.remove('active');
        if (qrView) qrView.style.display = 'flex';
        if (paperView) paperView.style.display = 'none';
        if (modalTitle) modalTitle.innerText = '📱 E-Ticket Dématérialisé (QR Code)';
      } else {
        if (btnQr) btnQr.classList.remove('active');
        if (btnPaper) btnPaper.classList.add('active');
        if (qrView) qrView.style.display = 'none';
        if (paperView) paperView.style.display = 'block';
        if (modalTitle) modalTitle.innerText = '🧾 Ticket de Caisse Papier';
      }
    }

    function printPaperTicket() {
      switchReceiptTab('paper');
      setTimeout(() => {
        window.print();
      }, 100);
    }

    async function copyReceiptLink() {
      if (!currentTicketUrl) return;
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(currentTicketUrl);
          alert('Lien du e-ticket copié dans le presse-papier !');
        } else {
          prompt('Copiez le lien direct du e-ticket :', currentTicketUrl);
        }
      } catch (err) {
        prompt('Copiez le lien direct du e-ticket :', currentTicketUrl);
      }
    }

    let catalog = [];
    let currentCategory = 'Tout';
    let currentTotalTTC = 0.0;

    // Horloge
    function updateClock() {
      const now = new Date();
      document.getElementById('live-clock').innerText = now.toLocaleTimeString('fr-FR', {hour: '2-digit', minute: '2-digit'});
    }
    setInterval(updateClock, 1000);
    updateClock();

    // Chargement initial
    async function loadCatalog() {
      const res = await fetch('/api/catalog');
      catalog = await res.json();
      renderCategories();
      renderProducts();
    }

    function renderCategories() {
      const cats = ['Tout', ...new Set(catalog.map(p => p.category))];
      const container = document.getElementById('category-tabs');
      container.innerHTML = '';
      cats.forEach(cat => {
        const btn = document.createElement('button');
        btn.className = 'tab-btn' + (cat === currentCategory ? ' active' : '');
        btn.innerText = cat;
        btn.onclick = () => selectCategory(cat);
        container.appendChild(btn);
      });
      const manageBtn = document.createElement('button');
      manageBtn.className = 'tab-btn';
      manageBtn.style.cssText = 'color: var(--primary); font-weight: bold; border: 1px dashed var(--primary); background: #eff6ff;';
      manageBtn.innerText = '⚙️ Gérer';
      manageBtn.title = 'Modifier ou supprimer des catégories';
      manageBtn.onclick = () => openCategoryManagerModal();
      container.appendChild(manageBtn);
    }

    function selectCategory(cat) {
      currentCategory = cat;
      renderCategories();
      renderProducts();
    }

    function renderProducts() {
      const query = document.getElementById('search-input').value.toLowerCase().trim();
      const filtered = catalog.filter(p => {
        const matchesCat = (currentCategory === 'Tout' || p.category === currentCategory);
        const matchesQuery = p.name.toLowerCase().includes(query);
        return matchesCat && matchesQuery;
      });

      const grid = document.getElementById('products-grid');
      if (filtered.length === 0) {
        grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: #94a3b8; padding: 40px;">Aucun produit trouvé.</div>';
        return;
      }

      grid.innerHTML = filtered.map(p => `
        <div class="product-card" style="border-left-color: ${p.color || '#3b82f6'};" onclick="addToTicket(${p.id})">
          <div class="product-name">${p.name}</div>
          <div class="product-price">${p.price.toFixed(2)} €</div>
        </div>
      `).join('');
    }

    function filterProducts() {
      renderProducts();
    }

    // Gestion du Ticket
    async function addToTicket(productId) {
      const res = await fetch('/api/ticket/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({product_id: productId, quantity: 1})
      });
      const state = await res.json();
      renderTicketState(state);
    }

    async function changeItemQty(productId, delta) {
      const endpoint = delta > 0 ? '/api/ticket/add' : '/api/ticket/remove';
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({product_id: productId, quantity: 1})
      });
      const state = await res.json();
      renderTicketState(state);
    }

    async function deleteTicketLine(productId) {
      const res = await fetch('/api/ticket/delete_line', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({product_id: productId})
      });
      const state = await res.json();
      renderTicketState(state);
    }

    async function clearTicket() {
      const res = await fetch('/api/ticket/clear', {method: 'POST'});
      const state = await res.json();
      renderTicketState(state);
    }

    function renderTicketState(state) {
      currentTotalTTC = state.total_ttc || 0.0;
      document.getElementById('ticket-badge').innerText = state.total_count || 0;
      document.getElementById('sum-ht').innerText = (state.total_ht || 0.0).toFixed(2) + ' €';
      document.getElementById('sum-tva').innerText = (state.total_tva || 0.0).toFixed(2) + ' €';
      document.getElementById('sum-ttc').innerText = currentTotalTTC.toFixed(2) + ' €';

      const container = document.getElementById('ticket-items');
      if (!state.items || state.items.length === 0) {
        container.innerHTML = '<div class="ticket-empty">Aucun article dans le ticket.<br>Touchez un produit pour l&apos;ajouter.</div>';
        return;
      }

      container.innerHTML = state.items.map(item => `
        <div class="ticket-row">
          <div class="item-info">
            <div class="item-name">${item.name}</div>
            <div class="item-unit-price">${item.unit_price.toFixed(2)} € / u</div>
          </div>
          <div class="qty-controls">
            <button class="btn-qty" onclick="changeItemQty(${item.product_id}, -1)">-</button>
            <span class="qty-number">${item.quantity}</span>
            <button class="btn-qty" onclick="changeItemQty(${item.product_id}, 1)">+</button>
          </div>
          <div class="item-total">${item.total_ttc.toFixed(2)} €</div>
          <button class="btn-del" onclick="deleteTicketLine(${item.product_id})" title="Supprimer">✕</button>
        </div>
      `).join('');
    }

    // Modal & Paiements
    function openModal(id) { document.getElementById(id).style.display = 'flex'; }
    function closeModal(id) { document.getElementById(id).style.display = 'none'; }

    async function payWithCard() {
      if (currentTotalTTC <= 0) { alert('Le ticket est vide.'); return; }
      const res = await fetch('/api/checkout', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({method: 'Carte Bancaire'})
      });
      const data = await res.json();
      if (data.status === 'SUCCESS') {
        showReceipt(data);
        clearTicket();
      }
    }

    async function payWithOther() {
      if (currentTotalTTC <= 0) { alert('Le ticket est vide.'); return; }
      const res = await fetch('/api/checkout', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({method: 'Ticket Restaurant'})
      });
      const data = await res.json();
      if (data.status === 'SUCCESS') {
        showReceipt(data);
        clearTicket();
      }
    }

    function openCashModal() {
      if (currentTotalTTC <= 0) { alert('Le ticket est vide.'); return; }
      document.getElementById('modal-cash-total').innerText = currentTotalTTC.toFixed(2) + ' €';
      document.getElementById('cash-received-input').value = '';
      document.getElementById('change-banner').style.display = 'none';
      document.getElementById('btn-validate-cash').disabled = true;
      openModal('cash-modal');
    }

    function addCashBill(amount) {
      const input = document.getElementById('cash-received-input');
      const current = parseFloat(input.value) || 0;
      input.value = (current + amount).toFixed(2);
      updateChangeCalculation();
    }

    function setExactCash() {
      document.getElementById('cash-received-input').value = currentTotalTTC.toFixed(2);
      updateChangeCalculation();
    }

    function updateChangeCalculation() {
      const received = parseFloat(document.getElementById('cash-received-input').value) || 0;
      const change = received - currentTotalTTC;
      const banner = document.getElementById('change-banner');
      const val = document.getElementById('change-value');
      const btn = document.getElementById('btn-validate-cash');

      if (received >= currentTotalTTC && currentTotalTTC > 0) {
        banner.style.display = 'block';
        val.innerText = Math.max(0, change).toFixed(2) + ' €';
        btn.disabled = false;
      } else {
        banner.style.display = 'none';
        btn.disabled = true;
      }
    }

    async function submitCashPayment() {
      const received = parseFloat(document.getElementById('cash-received-input').value) || currentTotalTTC;
      const res = await fetch('/api/checkout', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({method: 'Espèces', amount_received: received})
      });
      const data = await res.json();
      closeModal('cash-modal');
      if (data.status === 'SUCCESS') {
        showReceipt(data);
        clearTicket();
      }
    }

    function showReceipt(data) {
      currentTicketData = data;
      const receiptEl = document.getElementById('printable-receipt');
      receiptEl.classList.add('print-visible');
      const zEl = document.getElementById('z-content');
      if (zEl) zEl.classList.remove('print-visible');

      const co = data.company || currentCompany || {
        name: "BOULANGERIE PATISSERIE DU COMMERCE",
        legal_form: "SARL au capital de 15 000 €",
        address: "12 Rue de la République, 75001 Paris",
        phone: "01 42 68 00 00",
        siret: "834 567 890 00018",
        rcs: "RCS Paris B 834 567 890",
        code_naf: "1071C",
        tva_intra: "FR 45 834567890",
        pos_id: "CAISSE-01"
      };

      // Construction de l'URL pour le QR code (utilise l'adresse IP du réseau local afin que les smartphones sur le Wi-Fi puissent y accéder)
      const host = (systemInfo && systemInfo.local_ip && systemInfo.local_ip !== "127.0.0.1")
        ? (systemInfo.local_ip + ":" + (window.location.port || "8080"))
        : window.location.host;
      const protocol = window.location.protocol;
      currentTicketUrl = protocol + "//" + host + "/ticket/" + encodeURIComponent(data.ticket_number);

      // Mise à jour de la vue QR Code (Loi AGEC)
      const qrEndpoint = '/api/qr?ticket=' + encodeURIComponent(data.ticket_number);
      const qrImg = document.getElementById('receipt-qr-img');
      if (qrImg) {
        qrImg.src = qrEndpoint;
      }
      const qrTotal = document.getElementById('receipt-qr-total');
      if (qrTotal) {
        qrTotal.innerText = data.total_ttc.toFixed(2) + ' €';
      }
      const qrMeta = document.getElementById('receipt-qr-meta');
      if (qrMeta) {
        qrMeta.innerText = 'Ticket N° ' + data.ticket_number + ' • ' + (data.created_at || new Date().toLocaleString('fr-FR'));
      }
      const qrLink = document.getElementById('receipt-qr-link');
      if (qrLink) {
        qrLink.href = currentTicketUrl;
      }

      // Par défaut, afficher l'onglet QR Code (Loi AGEC)
      switchReceiptTab('qr');

      const tvaBreakdown = data.tva_breakdown || {};
      const tvaRows = Object.values(tvaBreakdown);

      receiptEl.innerHTML = `
        <div class="receipt-box">
          <!-- Identification légale obligatoire de l'entreprise -->
          <div class="receipt-header-center">
            <h3 class="receipt-company-title">${co.name}</h3>
            <div class="receipt-company-sub">${co.legal_form}</div>
            <div class="receipt-company-sub">${co.address}</div>
            <div class="receipt-company-sub">Tél : ${co.phone}</div>
            <div class="receipt-company-sub">SIRET : ${co.siret} | ${co.rcs}</div>
            <div class="receipt-company-sub">Code NAF : ${co.code_naf} | N° TVA : ${co.tva_intra}</div>
          </div>

          <hr class="receipt-dashed-line">

          <!-- Titre légal et métadonnées du ticket -->
          <div class="receipt-title">${data.is_duplicata ? 'DUPLICATA DE TICKET DE CAISSE' : 'TICKET DE CAISSE / JUSTIFICATIF DE VENTE'}</div>
          ${data.is_duplicata ? '<div style="text-align: center; color: #dc2626; font-weight: 800; font-size: 0.78rem; letter-spacing: 1px; margin-bottom: 4px;">*** DUPLICATA CERTIFIÉ CONFORME ***</div>' : ''}
          <div class="receipt-meta">
            <div>Ticket N° : <strong>${data.ticket_number}</strong></div>
            <div>Date & Heure : <strong>${data.created_at || new Date().toLocaleString('fr-FR')}</strong></div>
            <div>Caisse : <strong>${co.pos_id}</strong> | Opérateur : <strong>Vendeur 01</strong></div>
          </div>

          <hr class="receipt-dashed-line">

          <!-- Détail des articles -->
          <div style="display: flex; flex-direction: column; gap: 4px;">
            ${(data.items || []).map(i => `
              <div class="receipt-item-row">
                <div style="flex: 1;">
                  <div style="font-weight: 600;">${i.name}</div>
                  <div class="receipt-item-sub">${i.quantity} x ${(i.unit_price || (i.total / i.quantity)).toFixed(2)} € (TVA ${(i.tva_rate != null ? i.tva_rate.toFixed(1) : '10.0')}%)</div>
                </div>
                <div class="receipt-item-price">${(i.total_ttc || i.total).toFixed(2)} €</div>
              </div>
            `).join('')}
          </div>

          <hr class="receipt-dashed-line">

          <!-- Totaux généraux TTC, HT et TVA -->
          <div class="receipt-total-row">
            <span>TOTAL TTC</span>
            <span>${data.total_ttc.toFixed(2)} €</span>
          </div>
          <div class="receipt-subtotal-row">
            <span>Dont Total Hors Taxes (HT) :</span>
            <span>${data.total_ht.toFixed(2)} €</span>
          </div>
          <div class="receipt-subtotal-row">
            <span>Dont Total TVA :</span>
            <span>${data.total_tva.toFixed(2)} €</span>
          </div>

          <!-- Ventilation légale obligatoire de la TVA (CGI art. 286) -->
          <hr class="receipt-dotted-line">
          <div style="font-weight: 700; font-size: 0.78rem; text-align: center; margin: 4px 0 2px 0;">
            VENTILATION DE LA TVA (CGI ART. 286)
          </div>
          <table class="receipt-table-tva">
            <thead>
              <tr>
                <th>Taux</th>
                <th>Base HT</th>
                <th>Montant TVA</th>
                <th>Total TTC</th>
              </tr>
            </thead>
            <tbody>
              ${tvaRows.length > 0 ? tvaRows.map(r => `
                <tr>
                  <td>${r.rate.toFixed(1)}%</td>
                  <td>${r.base_ht.toFixed(2)} €</td>
                  <td>${r.montant_tva.toFixed(2)} €</td>
                  <td>${r.total_ttc.toFixed(2)} €</td>
                </tr>
              `).join('') : `
                <tr>
                  <td>10.0%</td>
                  <td>${data.total_ht.toFixed(2)} €</td>
                  <td>${data.total_tva.toFixed(2)} €</td>
                  <td>${data.total_ttc.toFixed(2)} €</td>
                </tr>
              `}
            </tbody>
          </table>

          <hr class="receipt-dashed-line">

          <!-- Règlements -->
          <div class="receipt-subtotal-row">
            <span>Mode de règlement :</span>
            <strong>${data.payment_method}</strong>
          </div>
          <div class="receipt-subtotal-row">
            <span>Montant reçu :</span>
            <span>${(data.amount_received || data.total_ttc).toFixed(2)} €</span>
          </div>
          ${data.change_returned > 0 ? `
            <div class="receipt-total-row" style="color: #059669; font-size: 1rem; margin-top: 4px;">
              <span>MONNAIE RENDUE</span>
              <span>${data.change_returned.toFixed(2)} €</span>
            </div>
          ` : ''}

          <!-- E-Ticket QR Code intégré dans le ticket papier -->
          <div style="text-align: center; margin: 10px 0 6px 0;">
            <img src="${qrEndpoint}" width="88" height="88" style="display: block; margin: 0 auto; border-radius: 4px;" alt="QR Code Ticket">
            <div style="font-size: 0.68rem; color: #475569; margin-top: 2px;">Retrouvez ce ticket sur votre smartphone (Loi AGEC)</div>
          </div>

          <!-- Scellement cryptographique NF 525 -->
          ${data.signature ? `
            <div class="receipt-signature-block">
              <div>🔒 <strong>Scellement Fiscal NF 525 (Art. 88 LF 2015-1785)</strong></div>
              <div style="margin-top: 2px;">Empreinte d'inaltérabilité SHA-256 :</div>
              <code style="font-size: 0.65rem; color: #1e293b;">${data.signature}</code>
            </div>
          ` : ''}

          <!-- Mentions légales finales -->
          <div class="receipt-legal-block">
            Système d'encaissement certifié conforme CGI art. 286, I-3° bis.<br>
            Conservez ce ticket, il vaut justificatif d'achat.
          </div>
          <div style="text-align: center; margin-top: 8px; font-weight: 600; font-size: 0.85rem;">
            Merci de votre visite et à bientôt !
          </div>
        </div>
      `;

      const actionBtn = document.getElementById('btn-receipt-next');
      if (actionBtn) {
        if (data.is_duplicata) {
          actionBtn.innerText = '⬅️ Retour Historique';
          actionBtn.onclick = () => {
            closeModal('receipt-modal');
            openHistoryModal();
          };
        } else {
          actionBtn.innerText = 'Client Suivant ➡️';
          actionBtn.onclick = () => closeModal('receipt-modal');
        }
      }

      openModal('receipt-modal');
    }

    // Z de Caisse (Rapport Journalier & Clôture Fiscale NF 525)
    async function openZReport() {
      const res = await fetch('/api/z_report');
      const data = await res.json();
      const container = document.getElementById('z-content');
      container.classList.add('print-visible');
      const recEl = document.getElementById('printable-receipt');
      if (recEl) recEl.classList.remove('print-visible');

      const tvaRows = Object.values(data.tva_breakdown || {});
      const co = data.company || currentCompany || {};

      container.innerHTML = `
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px;">
          <div style="text-align: center; border-bottom: 1px dashed #cbd5e1; padding-bottom: 8px; margin-bottom: 10px;">
            <div style="font-weight: 800; font-size: 1.05rem; text-transform: uppercase; color: #0f172a;">${co.name || 'ÉTABLISSEMENT'}</div>
            <div style="font-size: 0.78rem; color: #475569;">${co.legal_form || ''}</div>
            <div style="font-size: 0.76rem; color: #64748b;">${co.address ? co.address + ' | ' : ''}SIRET : ${co.siret || ''}</div>
            <div style="font-size: 0.76rem; color: #64748b;">Caisse : ${co.pos_id || 'CAISSE-01'} | N° TVA : ${co.tva_intra || ''}</div>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 1.1rem; font-weight: bold;">Date : ${data.date}</span>
            ${data.is_closed ? `
              <span style="background: #dcfce7; color: #166534; font-size: 0.8rem; font-weight: 700; padding: 3px 8px; border-radius: 9999px; border: 1px solid #86efac;">
                🔒 JOURNÉE CLÔTURÉE (${data.z_number})
              </span>
            ` : `
              <span style="background: #fef3c7; color: #92400e; font-size: 0.8rem; font-weight: 700; padding: 3px 8px; border-radius: 9999px; border: 1px solid #fcd34d;">
                ⏳ EN COURS (PROVISOIRE)
              </span>
            `}
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div>
              <div style="color: #64748b; font-size: 0.85rem;">TOTAL VENTES TTC</div>
              <div style="font-size: 1.6rem; font-weight: 900; color: #16a34a;">${data.total_sales_ttc.toFixed(2)} €</div>
            </div>
            <div>
              <div style="color: #64748b; font-size: 0.85rem;">NBRE DE TICKETS</div>
              <div style="font-size: 1.6rem; font-weight: 900;">${data.tickets_count}</div>
            </div>
          </div>

          <div style="margin-top: 8px; font-size: 0.85rem; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 6px;">
            Total HT : <strong>${data.total_sales_ht.toFixed(2)} €</strong> | TVA collectée : <strong>${data.total_tva.toFixed(2)} €</strong> | Panier moyen : <strong>${data.average_basket.toFixed(2)} €</strong>
          </div>

          <div style="margin-top: 6px; font-size: 0.85rem; color: #1e293b; background: #f1f5f9; padding: 6px 10px; border-radius: 6px;">
            📈 <strong>Compteur Perpétuel Cumulé (Grand Total NF 525) :</strong> ${(data.grand_total_ttc != null ? data.grand_total_ttc : data.total_sales_ttc).toFixed(2)} €
          </div>
        </div>

        <!-- Ventilation de la TVA par taux légal -->
        <div style="font-weight: bold; margin-top: 4px; font-size: 0.95rem;">📊 Ventilation Fiscale de la TVA (CGI art. 286) :</div>
        ${tvaRows.length === 0 ? '<div style="color: #94a3b8; font-size: 0.85rem;">Aucune vente enregistrée ce jour.</div>' : `
          <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem; background: white; border: 1px solid #e2e8f0; border-radius: 6px; overflow: hidden;">
            <thead>
              <tr style="background: #f1f5f9; border-bottom: 1px solid #cbd5e1; text-align: right;">
                <th style="padding: 6px 8px; text-align: left;">Taux</th>
                <th style="padding: 6px 8px;">Base HT</th>
                <th style="padding: 6px 8px;">TVA</th>
                <th style="padding: 6px 8px;">Total TTC</th>
              </tr>
            </thead>
            <tbody>
              ${tvaRows.map(r => `
                <tr style="border-bottom: 1px solid #f1f5f9; text-align: right;">
                  <td style="padding: 6px 8px; text-align: left; font-weight: 600;">${r.rate.toFixed(1)}%</td>
                  <td style="padding: 6px 8px;">${r.base_ht.toFixed(2)} €</td>
                  <td style="padding: 6px 8px; color: #2563eb; font-weight: 600;">${r.montant_tva.toFixed(2)} €</td>
                  <td style="padding: 6px 8px; font-weight: 700;">${r.total_ttc.toFixed(2)} €</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        `}

        <div style="font-weight: bold; margin-top: 4px; font-size: 0.95rem;">Ventilation des Règlements :</div>
        ${data.payments.length === 0 ? '<div style="color: #94a3b8; font-size: 0.85rem;">Aucun règlement enregistré ce jour.</div>' : data.payments.map(p => `
          <div style="display: flex; justify-content: space-between; padding: 6px 10px; background: #f1f5f9; border-radius: 6px; font-size: 0.9rem;">
            <span>${p.method} (${p.count} vente${p.count > 1 ? 's' : ''})</span>
            <span style="font-weight: bold;">${p.total.toFixed(2)} €</span>
          </div>
        `).join('')}

        <div style="font-weight: bold; margin-top: 4px; font-size: 0.95rem;">Top Articles Vendus :</div>
        ${data.top_items.length === 0 ? '<div style="color: #94a3b8; font-size: 0.85rem;">Aucun article vendu.</div>' : data.top_items.map(t => `
          <div style="display: flex; justify-content: space-between; padding: 4px 10px; font-size: 0.85rem;">
            <span>${t.name}</span>
            <span>${t.quantity} vendus (${t.total.toFixed(2)} €)</span>
          </div>
        `).join('')}

        ${data.is_closed ? `
          <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 10px; font-size: 0.75rem; color: #166534; word-break: break-all;">
            <div>🔒 <strong>Scellement NF 525 : Clôture ${data.z_number} scellée et inaltérable</strong></div>
            <div>Signature SHA-256 : <code>${data.signature}</code></div>
          </div>
        ` : `
          <div style="margin-top: 8px;">
            <button onclick="triggerCloseZ('${data.date}')" class="btn-pay" style="background: #dc2626; width: 100%; padding: 12px; font-size: 0.95rem;">
              🔒 Effectuer la Clôture Fiscale Définitive (Z Journalier NF 525)
            </button>
          </div>
        `}
      `;
      openModal('z-modal');
    }

    async function triggerCloseZ(dateStr) {
      if (!confirm('Confirmez-vous la clôture fiscale définitive de la journée ? Cette action est irréversible selon la norme NF 525.')) {
        return;
      }
      const res = await fetch('/api/z_report/close', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({date: dateStr})
      });
      const data = await res.json();
      alert(data.message || 'Clôture effectuée.');
      openZReport();
    }

    // Ajout Produit
    function openAddProductModal() { openModal('product-modal'); }
    async function submitNewProduct(e) {
      e.preventDefault();
      const name = document.getElementById('new-prod-name').value;
      const price = parseFloat(document.getElementById('new-prod-price').value);
      const tva = parseFloat(document.getElementById('new-prod-tva').value);
      const category = document.getElementById('new-prod-cat').value;

      await fetch('/api/products/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, price, category, tva_rate: tva})
      });

      closeModal('product-modal');
      e.target.reset();
      loadCatalog();
    }

    // Gestion des Catégories
    let loadedCategories = [];

    async function openCategoryManagerModal() {
      await loadCategoriesManagement();
      openModal('category-modal');
    }

    async function loadCategoriesManagement() {
      const res = await fetch('/api/categories');
      loadedCategories = await res.json();
      const listEl = document.getElementById('categories-manage-list');
      if (!loadedCategories || loadedCategories.length === 0) {
        listEl.innerHTML = '<div style="color: #94a3b8; text-align: center; padding: 16px;">Aucune catégorie existante.</div>';
        return;
      }
      listEl.innerHTML = loadedCategories.map((c, idx) => `
        <div id="cat-row-${idx}" style="display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;">
          <div id="cat-display-${idx}" style="display: flex; align-items: center; gap: 8px; flex: 1;">
            <span style="font-weight: 600; font-size: 1rem; color: #1e293b;">🏷️ ${c.category}</span>
            <span style="background: #e2e8f0; color: #475569; font-size: 0.8rem; padding: 2px 8px; border-radius: 12px; font-weight: 600;">
              ${c.count} ${c.count > 1 ? 'articles' : 'article'}
            </span>
          </div>
          <div id="cat-actions-${idx}" style="display: flex; gap: 6px;">
            <button class="btn-clear" style="color: #2563eb; background: #eff6ff; border: 1px solid #bfdbfe; font-size: 0.85rem; padding: 5px 10px;" onclick="startRenameCategory(${idx})">
              ✏️ Renommer
            </button>
            <button class="btn-clear" style="color: #dc2626; background: #fef2f2; border: 1px solid #fecaca; font-size: 0.85rem; padding: 5px 10px;" onclick="promptDeleteCategory(${idx})">
              🗑️ Supprimer
            </button>
          </div>
        </div>
      `).join('');
    }

    function startRenameCategory(idx) {
      const c = loadedCategories[idx];
      if (!c) return;
      const displayEl = document.getElementById(`cat-display-${idx}`);
      const actionsEl = document.getElementById(`cat-actions-${idx}`);
      displayEl.innerHTML = `
        <input type="text" id="rename-input-${idx}" class="search-input" value="${c.category}" style="padding: 6px 10px; font-size: 0.95rem; width: 90%; border-color: #3b82f6;">
      `;
      actionsEl.innerHTML = `
        <button class="btn-clear" style="color: #16a34a; background: #f0fdf4; border: 1px solid #bbf7d0; font-size: 0.85rem; padding: 5px 10px;" onclick="saveRenameCategory(${idx})">
          💾 Valider
        </button>
        <button class="btn-clear" style="color: #64748b; background: #f1f5f9; border: 1px solid #cbd5e1; font-size: 0.85rem; padding: 5px 10px;" onclick="loadCategoriesManagement()">
          ✖ Annuler
        </button>
      `;
      const input = document.getElementById(`rename-input-${idx}`);
      input.focus();
      input.select();
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') saveRenameCategory(idx);
        if (e.key === 'Escape') loadCategoriesManagement();
      });
    }

    async function saveRenameCategory(idx) {
      const c = loadedCategories[idx];
      if (!c) return;
      const input = document.getElementById(`rename-input-${idx}`);
      if (!input) return;
      const newName = input.value.trim();
      if (!newName || newName === c.category) {
        loadCategoriesManagement();
        return;
      }
      const res = await fetch('/api/categories/rename', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({old_name: c.category, new_name: newName})
      });
      const data = await res.json();
      if (data.status === 'SUCCESS') {
        if (currentCategory === c.category) {
          currentCategory = newName;
        }
        await loadCatalog();
        await loadCategoriesManagement();
      } else {
        alert('Erreur lors du renommage : ' + (data.error || 'Inconnue'));
      }
    }

    async function promptDeleteCategory(idx) {
      const c = loadedCategories[idx];
      if (!c) return;
      const confirmMsg = "Supprimer la catégorie « " + c.category + " » ?\\nSes " + c.count + " article(s) seront reclassés dans la catégorie « Divers ».";
      if (!confirm(confirmMsg)) return;

      const res = await fetch('/api/categories/delete', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({category: c.category, reassign_to: 'Divers'})
      });
      const data = await res.json();
      if (data.status === 'SUCCESS') {
        if (currentCategory === c.category) {
          currentCategory = 'Tout';
        }
        await loadCatalog();
        await loadCategoriesManagement();
      } else {
        alert('Erreur lors de la suppression : ' + (data.error || 'Inconnue'));
      }
    }

    // Gestion de l'Établissement & Mentions Légales
    let currentCompany = null;

    async function loadCompanyInfo() {
      try {
        const res = await fetch('/api/company');
        const data = await res.json();
        currentCompany = data;
        const sub = document.getElementById('header-company-subtitle');
        if (sub && data && data.name) {
          sub.innerText = '🏢 ' + data.name;
        }
        return data;
      } catch (err) {
        console.error('Erreur chargement mentions légales:', err);
      }
    }

    async function openCompanyModal() {
      const co = await loadCompanyInfo() || {};
      document.getElementById('co-name').value = co.name || '';
      document.getElementById('co-legal-form').value = co.legal_form || '';
      document.getElementById('co-phone').value = co.phone || '';
      document.getElementById('co-address').value = co.address || '';
      document.getElementById('co-siret').value = co.siret || '';
      document.getElementById('co-rcs').value = co.rcs || '';
      document.getElementById('co-naf').value = co.code_naf || '';
      document.getElementById('co-tva-intra').value = co.tva_intra || '';
      document.getElementById('co-pos-id').value = co.pos_id || 'CAISSE-01';

      const fb = document.getElementById('company-save-feedback');
      if (fb) fb.style.display = 'none';

      openModal('company-modal');
    }

    async function saveCompanyInfo(e) {
      e.preventDefault();
      const fb = document.getElementById('company-save-feedback');
      const payload = {
        name: document.getElementById('co-name').value.trim(),
        legal_form: document.getElementById('co-legal-form').value.trim(),
        phone: document.getElementById('co-phone').value.trim(),
        address: document.getElementById('co-address').value.trim(),
        siret: document.getElementById('co-siret').value.trim(),
        rcs: document.getElementById('co-rcs').value.trim(),
        code_naf: document.getElementById('co-naf').value.trim(),
        tva_intra: document.getElementById('co-tva-intra').value.trim(),
        pos_id: document.getElementById('co-pos-id').value.trim()
      };

      try {
        const res = await fetch('/api/company', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.status === 'SUCCESS') {
          currentCompany = data.company;
          const sub = document.getElementById('header-company-subtitle');
          if (sub && currentCompany && currentCompany.name) {
            sub.innerText = '🏢 ' + currentCompany.name;
          }
          if (fb) {
            fb.style.background = '#f0fdf4';
            fb.style.color = '#166534';
            fb.style.border = '1px solid #bbf7d0';
            fb.innerText = '✅ Dénomination sociale et mentions légales enregistrées avec succès !';
            fb.style.display = 'block';
          }
          setTimeout(() => {
            closeModal('company-modal');
          }, 900);
        } else {
          if (fb) {
            fb.style.background = '#fef2f2';
            fb.style.color = '#991b1b';
            fb.style.border = '1px solid #fecaca';
            fb.innerText = "❌ Erreur lors de l'enregistrement : " + (data.error || "Erreur");
            fb.style.display = 'block';
          }
        }
      } catch (err) {
        if (fb) {
          fb.style.background = '#fef2f2';
          fb.style.color = '#991b1b';
          fb.style.border = '1px solid #fecaca';
          fb.innerText = "❌ Erreur de communication réseau.";
          fb.style.display = 'block';
        }
      }
    }

    // Historique des Ventes & Consultation / Duplicata
    let currentHistoryFilter = 'today';
    let loadedHistoryTickets = [];

    async function openHistoryModal() {
      await setHistoryFilter('today');
      openModal('history-modal');
    }

    async function setHistoryFilter(mode, specificDate) {
      currentHistoryFilter = mode;
      const btnToday = document.getElementById('btn-hist-today');
      const btnAll = document.getElementById('btn-hist-all');
      const datePicker = document.getElementById('hist-date-picker');

      if (btnToday) btnToday.classList.toggle('active', mode === 'today');
      if (btnAll) btnAll.classList.toggle('active', mode === 'all');

      let url = '/api/history?limit=300';
      if (mode === 'today') {
        const todayStr = new Date().toISOString().split('T')[0];
        url += '&date=' + todayStr;
        if (datePicker) datePicker.value = '';
      } else if (mode === 'date') {
        const targetDate = specificDate || (datePicker ? datePicker.value : '');
        if (!targetDate) return;
        url += '&date=' + targetDate;
        if (btnToday) btnToday.classList.remove('active');
        if (btnAll) btnAll.classList.remove('active');
      } else if (mode === 'all') {
        url = '/api/history?limit=1000';
        if (datePicker) datePicker.value = '';
      }

      try {
        const res = await fetch(url);
        const data = await res.json();
        loadedHistoryTickets = data.tickets || [];

        const kpiTotal = document.getElementById('hist-kpi-total');
        const kpiCount = document.getElementById('hist-kpi-count');
        const kpiBasket = document.getElementById('hist-kpi-basket');
        if (kpiTotal) kpiTotal.innerText = (data.total_sales_ttc || 0).toFixed(2) + ' €';
        if (kpiCount) kpiCount.innerText = data.count || 0;
        if (kpiBasket) kpiBasket.innerText = (data.average_basket || 0).toFixed(2) + ' €';

        const searchInput = document.getElementById('hist-search-input');
        if (searchInput) searchInput.value = '';

        renderHistoryList(loadedHistoryTickets);
      } catch (err) {
        console.error('Erreur chargement historique', err);
      }
    }

    function renderHistoryList(tickets) {
      const listEl = document.getElementById('history-tickets-list');
      if (!listEl) return;
      if (!tickets || tickets.length === 0) {
        listEl.innerHTML = '<div style="color: #94a3b8; text-align: center; padding: 36px 16px; font-size: 0.95rem;">Aucun ticket enregistré pour cette sélection.</div>';
        return;
      }

      listEl.innerHTML = tickets.map(t => {
        const dateObj = new Date(t.created_at);
        const timeStr = !isNaN(dateObj.getTime()) ? dateObj.toLocaleTimeString('fr-FR', {hour: '2-digit', minute: '2-digit'}) : '';
        const dateStr = !isNaN(dateObj.getTime()) ? dateObj.toLocaleDateString('fr-FR') : t.created_at;

        let methodColor = '#2563eb';
        let methodBg = '#eff6ff';
        let methodIcon = '💳';
        if (t.payment_method === 'Espèces') {
          methodColor = '#16a34a';
          methodBg = '#f0fdf4';
          methodIcon = '💵';
        } else if ((t.payment_method || '').includes('Ticket')) {
          methodColor = '#d97706';
          methodBg = '#fffbeb';
          methodIcon = '🎟️';
        }

        const itemsPreview = (t.items || []).map(i => i.quantity + 'x ' + i.name).slice(0, 3).join(', ');
        const extraCount = (t.items || []).length > 3 ? ' (+' + (t.items.length - 3) + ' autres)' : '';

        return `
          <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: white; border: 1px solid #e2e8f0; border-radius: 8px; gap: 10px; transition: background 0.15s;" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='white'">
            <div style="display: flex; align-items: center; gap: 10px; min-width: 140px;">
              <span style="font-weight: 800; font-size: 0.95rem; color: #1e293b;">${timeStr || dateStr}</span>
              <span style="font-size: 0.76rem; color: #64748b;">${dateStr}</span>
            </div>

            <div style="flex: 1; min-width: 180px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-weight: 700; font-size: 0.88rem; font-family: monospace; color: #0f172a;">${t.ticket_number}</span>
                <span style="background: ${methodBg}; color: ${methodColor}; font-size: 0.78rem; font-weight: 700; padding: 2px 8px; border-radius: 12px; display: inline-flex; align-items: center; gap: 4px;">
                  ${methodIcon} ${t.payment_method}
                </span>
              </div>
              <div style="font-size: 0.78rem; color: #64748b; margin-top: 2px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; max-width: 340px;">
                ${itemsPreview}${extraCount}
              </div>
            </div>

            <div style="text-align: right; min-width: 95px;">
              <div style="font-weight: 900; font-size: 1.15rem; color: #1e293b;">${Number(t.total_ttc).toFixed(2)} €</div>
              <div style="font-size: 0.72rem; color: #64748b;">${t.items_count || 1} article${(t.items_count || 1) > 1 ? 's' : ''}</div>
            </div>

            <div>
              <button class="btn-clear" style="color: #4338ca; background: #eef2ff; border: 1px solid #c7d2fe; font-size: 0.85rem; padding: 6px 12px; border-radius: 6px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 4px;" onclick="viewHistoricalTicket('${t.ticket_number}')">
                👁️ Voir / Duplicata
              </button>
            </div>
          </div>
        `;
      }).join('');
    }

    function filterHistoryList() {
      const q = (document.getElementById('hist-search-input').value || '').toLowerCase().trim();
      if (!q) {
        renderHistoryList(loadedHistoryTickets);
        return;
      }
      const filtered = loadedHistoryTickets.filter(t => {
        const numMatch = (t.ticket_number || '').toLowerCase().includes(q);
        const methMatch = (t.payment_method || '').toLowerCase().includes(q);
        const priceMatch = (t.total_ttc || '').toString().includes(q);
        const itemsMatch = (t.items || []).some(i => (i.name || '').toLowerCase().includes(q));
        return numMatch || methMatch || priceMatch || itemsMatch;
      });
      renderHistoryList(filtered);
    }

    async function viewHistoricalTicket(ticketNumber) {
      try {
        const res = await fetch('/api/ticket/detail?number=' + encodeURIComponent(ticketNumber));
        const data = await res.json();
        if (data.status === 'SUCCESS') {
          closeModal('history-modal');
          showReceipt(data);
        } else {
          alert('Impossible de charger le ticket : ' + (data.message || 'Erreur'));
        }
      } catch (err) {
        alert('Erreur réseau lors de la récupération du ticket.');
      }
    }

    // Initialisation
    loadSystemInfo();
    loadCompanyInfo();
    loadCatalog();
  </script>
</body>
</html>
"""

HTML_PAGE = HTML_TEMPLATE.replace("/* __QRCODE_JS__ */", QR_CODE_JS)

