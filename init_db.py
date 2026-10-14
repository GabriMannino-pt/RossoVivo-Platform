import sqlite3
import os
from datetime import datetime, date

DB_PATH = "rosso_vivo.db"

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Ordini
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shopify_order_id TEXT,
        customer_email TEXT,
        total_price REAL,
        product_sku TEXT,
        quantity_kg REAL,
        shipping_cost REAL,
        cogs REAL,
        profit REAL,
        source TEXT,
        created_at TIMESTAMP
    );
    """)

    # 2. Inventario
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE,
        stock_kg REAL,
        reserved_kg REAL,
        available_kg REAL,
        reorder_point REAL,
        last_updated TIMESTAMP
    );
    """)

    # 3. Marketing Spend
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marketing_spend (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT,
        campaign_id TEXT,
        spend REAL,
        revenue REAL,
        roas REAL,
        cac REAL,
        date DATE
    );
    """)

    # 4. Clienti
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        first_order DATE,
        last_order DATE,
        total_orders INTEGER,
        total_spent REAL,
        is_subscriber INTEGER,
        segment TEXT,
        nps INTEGER
    );
    """)

    # 5. Content Calendar
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS content_calendar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT,
        content_type TEXT,
        caption TEXT,
        visual_notes TEXT,
        scheduled_at TIMESTAMP,
        status TEXT,
        engagement_estimate REAL
    );
    """)

    # 6. Competitor Pricing
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS competitor_pricing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        competitor TEXT,
        sku TEXT,
        price REAL,
        shipping REAL,
        total_price REAL,
        promotion TEXT,
        scraped_at TIMESTAMP
    );
    """)

    # 7. Brand Intelligence
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS brand_intelligence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric_name TEXT,
        metric_value REAL,
        source TEXT,
        notes TEXT,
        recorded_at TIMESTAMP
    );
    """)

    # 8. Market Context
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS market_context (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        title TEXT,
        content TEXT,
        source_url TEXT,
        impact_level TEXT,
        brix_reading REAL,
        brix_measured_at TIMESTAMP,
        farmer_notes TEXT,
        recorded_at TIMESTAMP
    );
    """)

    # 9. Agent Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_name TEXT,
        action TEXT,
        details TEXT,
        status TEXT,
        created_at TIMESTAMP
    );
    """)

    # 10. Decision Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS decision_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE,
        proposed_by TEXT,
        decided_by TEXT,
        date_proposed TIMESTAMP,
        date_decided TIMESTAMP,
        date_executed TIMESTAMP,
        decision TEXT,
        motivation TEXT,
        expected_outcome TEXT,
        verification_date DATE,
        actual_outcome TEXT,
        roi REAL,
        lesson_learned TEXT
    );
    """)

    # 11. Pre-Launch Leads
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prelaunch_leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        lead_source TEXT,
        referral_code TEXT,
        created_at TIMESTAMP,
        status TEXT
    );
    """)

    # 12. Pre-Launch Offers
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prelaunch_offers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        offer_name TEXT UNIQUE,
        price REAL,
        target_quantity INTEGER,
        sold_quantity INTEGER,
        status TEXT
    );
    """)

    # 13. Bandi (Agente 16)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bandi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codice TEXT UNIQUE,
        titolo TEXT,
        fonte TEXT,
        url TEXT,
        scadenza DATE,
        importo_max REAL,
        tipo_contributo TEXT,
        stato TEXT,
        idoneo INTEGER,
        documenti TEXT,
        bozza_path TEXT,
        alert_sent INTEGER DEFAULT 0,
        created_at TIMESTAMP
    );
    """)

    # 14. Scadenze Fiscali (Agente 17)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scadenze_fiscali (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descrizione TEXT,
        data_scadenza DATE UNIQUE,
        tipo TEXT,
        importo_previsto REAL,
        stato TEXT,
        alert_date DATE,
        created_at TIMESTAMP
    );
    """)

    # 15. Proiezioni Fiscali (Agente 17)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS proiezioni_fiscali (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scenario TEXT,
        anno INTEGER,
        mese INTEGER,
        fatturato REAL,
        costi REAL,
        reddito_imponibile REAL,
        imposta_totale REAL,
        netto REAL,
        updated_at TIMESTAMP
    );
    """)

    # --- SEED DATA INIZIALE ---
    now = datetime.now().isoformat()

    # Seed Inventory
    inventory_items = [
        ('SKU1_5KG', 250.0, 0.0, 250.0, 500.0, now),
        ('SKU2_10KG', 600.0, 0.0, 600.0, 500.0, now),
        ('SKU3_15KG', 300.0, 0.0, 300.0, 500.0, now),
        ('SKU4_GIFT', 100.0, 0.0, 100.0, 200.0, now),
        ('SKU5_SUB10KG', 400.0, 0.0, 400.0, 500.0, now),
        ('SKU6_B2B20KG', 300.0, 0.0, 300.0, 500.0, now)
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO inventory (sku, stock_kg, reserved_kg, available_kg, reorder_point, last_updated)
        VALUES (?, ?, ?, ?, ?, ?)
    """, inventory_items)

    # Seed Scadenze Fiscali
    scadenze = [
        ('Acconto IVA 1° Trimestre', '2026-04-16', 'iva', 450.0, 'pending', '2026-04-09', now),
        ('Saldo IVA + Acconto Unico', '2026-06-16', 'iva', 1200.0, 'pending', '2026-06-07', now),
        ('Acconto IRAP / IRES 2° Trimestre', '2026-09-16', 'irap', 650.0, 'pending', '2026-09-07', now),
        ('Acconto IVA 4° Trimestre', '2026-11-16', 'iva', 800.0, 'pending', '2026-11-07', now),
        ('Dichiarazione Annuale IVA/Redditi', '2026-11-30', 'dichiarazione', 0.0, 'pending', '2026-11-15', now)
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO scadenze_fiscali (descrizione, data_scadenza, tipo, importo_previsto, stato, alert_date, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, scadenze)

    # Seed Bandi di Prova
    seed_bandi = [
        ('PSR-SICILIA-4.1', 'Investimenti nelle Aziende Agricole Siciliane', 'PSR Sicilia 2014-2027', 'https://www.psrsicilia.it', '2026-10-15', 50000.0, 'Fondo Perduto 70%', 'PRIORITARIO', 1, '["SPID", "Business Plan", "Visura Camerale"]', 'reports/bandi/2026-10-15_bando_PSR-SICILIA-4.1.md', 0, now),
        ('INVITALIA-RESTO-SUD', 'Resto al Sud 2.0 - Agevolazioni Imprese Mezzogiorno', 'Invitalia', 'https://www.invitalia.it', '2026-11-30', 40000.0, 'Fondo Perduto 50% + Finanziamento 50%', 'RILEVANTE', 1, '["Business Plan", "Firma Digitale"]', 'reports/bandi/2026-11-30_bando_INVITALIA-RESTO-SUD.md', 0, now)
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO bandi (codice, titolo, fonte, url, scadenza, importo_max, tipo_contributo, stato, idoneo, documenti, bozza_path, alert_sent, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, seed_bandi)

    cursor.execute("""
        INSERT INTO agent_logs (agent_name, action, details, status, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, ('SYSTEM', 'INIT_AGENTS_16_17', 'Database SQLite aggiornato con le tabelle bandi, scadenze_fiscali e proiezioni_fiscali.', 'SUCCESS', now))

    conn.commit()
    conn.close()
    print("Database SQLite aggiornato con le tabelle per gli Agenti 16 & 17!")

if __name__ == "__main__":
    init_database()
