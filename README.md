# 🍊 RossoVivo Platform — Agritech E-Commerce & Supply Chain Inventory Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Shopify API](https://img.shields.io/badge/Shopify-Admin%20GraphQL%20%2F%20REST-96BF48?style=for-the-badge&logo=shopify&logoColor=white)](https://shopify.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-Local%20Inventory-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **Enterprise Agritech platform connecting agronomic harvest scheduling, batch lot traceability, and bidirectional Shopify Admin API inventory synchronization for premium agricultural commodities.**

---

## 🇮🇹 Executive Summary (Italiano)

**RossoVivo Platform** è una soluzione integrata agritech ed e-commerce concepita per gestire la filiera corta di agrumi siciliani d'eccellenza (Arance Rosse IGP Tarocco e Moro).  
Il sistema fa da ponte tra la produzione agronomica in campo (mappatura lotti, stima resa in kg per ettaro, data ottimale di raccolta per grado zuccherino e pigmentazione) e la vendita diretta sia al consumatore finale (B2C) che a distributori esteri (B2B), sincronizzando in tempo reale il catalogo prodotti e le giacenze tramite le **API Admin di Shopify**.

### Punti di Forza Ingegneristici:
- **Sincronizzazione Bidirezionale Shopify:** Connessione Machine-to-Machine (M2M) con rinnovo automatico del token di accesso (Client Credentials Grant), gestione dei rate limits e riconciliazione ordini.
- **Tracciabilità di Lotto (Farm-to-Fork):** Monitoraggio della provenienza agronomica di ciascuna cassa venduta, collegando il codice lotto (`batch_lot`) al lotto catastale e alla finestra di raccolta.
- **Controllo di Gestione del Margine Unitario:** Calcolo in tempo reale di COGS (Cost of Goods Sold), spese di spedizione refrigerata, costi di imballaggio e margine operativo netto per chilogrammo.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph FIELD["Agronomic & Production Layer"]
        ORCHARD["Citrus Groves & Parcels<br/>(Lotti Catastali Etna)"]
        HARVEST["Yield Forecasting & Harvest Batches<br/>(Kg Stored vs Kg Available)"]
        MAP["Interactive Parcel Map<br/>(mappa_lotti.html)"]
        ORCHARD --> HARVEST --> MAP
    end

    subgraph BACKEND["Flask Core Engine & Persistence"]
        DB[("SQLite ACID Database<br/>• orders<br/>• inventory<br/>• customers<br/>• production_lots")]
        APP["Flask Application Core<br/>(REST Endpoints, Leads, Funnel Smoke Tests)"]
        MAP --> DB
        APP --> DB
    end

    subgraph SYNC_LAYER["Shopify Integration Engine"]
        M2M["Token Refresher<br/>(OAuth Client Credentials)"]
        SYNC["Shopify Client (shopify_client.py)<br/>• Product Catalog Push<br/>• Live Inventory Sync<br/>• Webhook Order Ingestion"]
        APP --> SYNC
        SYNC --> M2M
    end

    subgraph SALES_CHANNELS["Digital Distribution Channels"]
        SHOPIFY["Shopify Storefront<br/>(B2C & B2B Purchasing)"]
        LANDING["Pre-Launch & Lead Generation Funnels<br/>(/landing, /fakedoor)"]
        SYNC <--> SHOPIFY
        APP --> LANDING
    end
```

---

## ⚡ Technical Highlights

1. **Autonomous Shopify M2M Authentication:**
   - Implements automated token refresh logic using Shopify's modern Client Credentials Grant, abstracting authentication headers for background daemons.
2. **Idempotent Inventory Sync:**
   - Database operations use `ON CONFLICT(sku) DO UPDATE` to guarantee that concurrent stock changes from field harvesting and online sales never produce race conditions.
3. **Smoke Testing & Validation Architecture:**
   - Includes validation routes (`/fakedoor`, `/landing`) to conduct market demand validation and measure CAC/conversion rates before crop harvesting.

---

## 🚀 Quickstart

### 1. Requirements
- Python >= 3.10
- Dependencies in `requirements.txt`

### 2. Installation
```bash
git clone https://github.com/GabriMannino-pt/RossoVivo-Platform.git
cd RossoVivo-Platform
pip install -r requirements.txt
```

### 3. Initialize Database
Initialize the SQLite schema with table indexes:
```bash
python init_db.py
```

### 4. Configure Environment
Copy `.env.example` to `.env` and fill in your Shopify credentials:
```bash
cp .env.example .env
```

### 5. Launch Application
```bash
python app.py
```
Visit `http://localhost:5000` to access the platform.

---

## 📁 Repository Structure

```
RossoVivo-Platform/
├── templates/
│   ├── index.html               # Main dashboard UI
│   ├── landing_agosto.html      # Lead acquisition funnel
│   └── landing_fakedoor.html    # Market validation test
├── sample_data/
│   └── mock_catalog.json        # Synthetic product catalog & batches
├── mappa_lotti.html             # Field parcel mapping viewer
├── shopify_client.py            # Shopify Admin API wrapper & token manager
├── app.py                       # Flask server & business endpoints
├── init_db.py                   # Database schema definition
├── create_initial_catalog.py    # Product seeding script
├── .env.example                 # Configuration template
├── .gitignore                   # Strict compliance filter
├── requirements.txt             # Python dependencies
└── README.md                    # Enterprise technical specification
```

---

## 🛡️ Privacy & Compliance Notice
This repository contains the software engine and synthetic mock catalog data. **No real customer records, private tax documents, purchase invoices, or live store production secrets are stored or committed.**

---

## 👨‍💻 Author
**Gabriele Mannino**  
- Software Engineer & Automation Architect  
- LinkedIn: [linkedin.com/in/gabriele-mannino-dev](https://linkedin.com/in/gabriele-mannino-dev)  
- GitHub: [@GabriMannino-pt](https://github.com/GabriMannino-pt)  
- Email: `gabri.mannino.lavoro@gmail.com`
