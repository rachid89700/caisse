# 🏪 Ma Caisse Enregistreuse Facile

Application moderne de caisse enregistreuse tactile, conforme à la législation française (NF 525 / Art. 286 du CGI / Loi AGEC), utilisable sur ordinateur, tablette (iPad, Android) et smartphone.

---

## ✨ Fonctionnalités Principales

- **Interface Tactile Responsive** : Conçue pour iPad, tablettes Android et écrans tactiles POS.
- **Conformité Fiscale NF 525 & CGI art. 286** :
  - Scellement cryptographique SHA-256 de chaque vente.
  - Chaînage inaltérable des tickets (empreinte du ticket précédent).
  - Clôture journalière (Rapport Z) avec cumul perpétuel inaltérable.
  - Mentions légales obligatoires (SIRET, adresse, ventilation HT/TVA/TTC).
- **Ticket Dématérialisé (Loi AGEC)** :
  - Génération de QR code officiel scannable directement sur l'écran par le client.
  - Page web dédiée du ticket électronique pour mobile (4G/5G).
- **Historique Illimité & Recherche** :
  - Consultation par calendrier (date exacte, mois complet).
  - Réimpression de duplicatas officiels certifiés.
- **Gestion du Catalogue** :
  - Ajout direct d'articles avec taux de TVA personnalisés (20%, 10%, 5.5%).
  - Personnalisation complète des catégories.
- **Application Web Progressive (PWA)** :
  - Installation sur écran d'accueil de tablette en 1 clic.
  - Affichage plein écran autonome sans barre de navigation.

---

## 🚀 Démarrage Local

Pour lancer l'application sur votre machine locale :

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer la caisse
python lancer_caisse.py
```

L'application s'ouvre automatiquement sur : `http://localhost:8080`.

---

## ☁️ Déploiement Gratuit sur Render.com

1. Créez un compte gratuit sur [Render.com](https://render.com) (via GitHub).
2. Cliquez sur **"New +" -> "Web Service"**.
3. Liez ce dépôt GitHub.
4. Render détecte automatiquement la configuration :
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `python lancer_caisse.py`
   - **Plan** : `Free`
5. Votre caisse est en ligne avec une adresse sécurisée HTTPS (`https://votre-caisse.onrender.com`).
