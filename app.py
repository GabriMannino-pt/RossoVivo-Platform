import sqlite3
import os
import importlib
from datetime import datetime, date
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
DB_PATH = "rosso_vivo.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/landing")
def landing_agosto():
    """Landing Page per la raccolta email di Agosto (Fase 1 Pre-Lancio)"""
    return render_template("landing_agosto.html")

@app.route("/fakedoor")
def landing_fakedoor():
    """Smoke Test 2: Landing Page Fake Door con Cassa 10kg a 29,90€ e Pre-Ordine"""
    return render_template("landing_fakedoor.html")


@app.route("/api/submit_lead", methods=["POST"])
def submit_lead():
    data = request.json or {}
    email = data.get("email")
    lead_source = data.get("lead_source", "Landing Page Agosto")
    now_str = datetime.now().isoformat()

    if not email or "@" not in email:
        return jsonify({"success": False, "message": "Inserisci un indirizzo email valido."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO prelaunch_leads (email, lead_source, created_at, status)
            VALUES (?, ?, ?, ?)
        """, (email, lead_source, now_str, 'ACTIVE'))

        cursor.execute("""
            INSERT INTO agent_logs (agent_name, action, details, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, ('Agente 06 - Email Marketing', 'NEW_LEAD_SUBMITTED', f'Nuovo lead raccolto da {lead_source}: {email}', 'SUCCESS', now_str))

        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Iscrizione completata con successo! Ti invieremo il materiale all indirizzo indicato."})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"success": True, "message": "Sei già iscritto alla nostra lista d attesa esclusiva!"})

@app.route("/api/kpis")
def get_kpis():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*), COALESCE(SUM(total_price), 0), COALESCE(SUM(profit), 0) FROM orders")
    total_orders, total_revenue, total_profit = cursor.fetchone()

    cursor.execute("SELECT COALESCE(SUM(available_kg), 0) FROM inventory")
    total_stock_kg = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(spend), 0) FROM marketing_spend")
    total_spend = cursor.fetchone()[0]

    aov = (total_revenue / total_orders) if total_orders > 0 else 0.0
    cac = (total_spend / total_orders) if total_orders > 0 else 0.0

    conn.close()

    return jsonify({
        "total_revenue": round(total_revenue, 2),
        "target_revenue": 200000.0,
        "total_profit": round(total_profit, 2),
        "total_orders": total_orders,
        "aov": round(aov, 2),
        "cac": round(cac, 2),
        "total_stock_kg": round(total_stock_kg, 1),
        "system_status": "OPERATIVO (Lean Stack + Agenti 16 & 17)" if total_stock_kg >= 500 else "ATTENZIONE"
    })

@app.route("/api/prelaunch")
def get_prelaunch_metrics():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM prelaunch_leads")
    total_leads = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(sold_quantity), 0) FROM prelaunch_offers")
    total_preorders = cursor.fetchone()[0]

    conn.close()

    target_leads = 2000
    target_preorders = 300
    preorder_revenue = total_preorders * 29.90
    est_net_profit = 4480.0

    return jsonify({
        "total_leads": total_leads,
        "target_leads": target_leads,
        "leads_pct": round((total_leads / target_leads) * 100, 1),
        "total_preorders": total_preorders,
        "target_preorders": target_preorders,
        "preorders_pct": round((total_preorders / target_preorders) * 100, 1),
        "preorder_revenue": round(preorder_revenue, 2),
        "est_net_profit": est_net_profit
    })

@app.route("/api/bandi")
def get_bandi():
    """API per i bandi attivi ed idonei (Agente 16)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bandi WHERE idoneo = 1 ORDER BY scadenza ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route("/api/scadenze_fiscali")
def get_scadenze_fiscali():
    """API per le scadenze fiscali (Agente 17)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scadenze_fiscali ORDER BY data_scadenza ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route("/api/proiezioni_fiscali")
def get_proiezioni_fiscali():
    """API per il confronto delle simulazioni fiscali A, B, C (Agente 17)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM proiezioni_fiscali ORDER BY scenario ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route("/api/agents")
def get_agents():
    agents_def = [
        {"id": "15", "name": "Strategy & Audit Supervisor", "cycle": "Ogni giorno 07:30", "phase": "Supervisor Proattivo"},
        {"id": "01", "name": "Marketing Content", "cycle": "Ogni giorno 07:00", "phase": "Attivo (Lean)"},
        {"id": "02", "name": "Paid Ads Optimizer", "cycle": "Ogni giorno 09:00 e 18:00", "phase": "Attivo (Lean)"},
        {"id": "03", "name": "Customer Care AI", "cycle": "Shopify Inbox", "phase": "Attivo (Lean)"},
        {"id": "04", "name": "Analytics Dashboard", "cycle": "Ogni giorno 08:00", "phase": "Attivo (Lean)"},
        {"id": "05", "name": "Supply Chain", "cycle": "Moving Average 7gg", "phase": "Attivo (Lean)"},
        {"id": "06", "name": "Email Marketing", "cycle": "Shopify Email Nativo", "phase": "Attivo (Lean)"},
        {"id": "07", "name": "Social Media Manager", "cycle": "Ogni 3 ore", "phase": "Attivo (Lean)"},
        {"id": "08", "name": "SEO & Content", "cycle": "Settimanale (Lunedì)", "phase": "Attivo (Lean)"},
        {"id": "09", "name": "Revenue & Pricing", "cycle": "Settimanale (Mercoledì)", "phase": "Attivo (Lean)"},
        {"id": "10", "name": "Pre-Sales Conversion", "cycle": "Exit-intent widget", "phase": "Attivo (Lean)"},
        {"id": "11", "name": "Social Proof & UGC", "cycle": "Shopify Reviews", "phase": "Attivo (Lean)"},
        {"id": "12", "name": "Compliance & Admin", "cycle": "Shopify Privacy", "phase": "Attivo (Lean)"},
        {"id": "13", "name": "Brand Intelligence", "cycle": "Multi-frequenza", "phase": "Attivo (Lean)"},
        {"id": "14", "name": "Market Research", "cycle": "Meteo API + Brix manuale", "phase": "Attivo (Lean)"},
        {"id": "16", "name": "Bandi Radar & Preparatore", "cycle": "Lunedì 08:00 + Monthly", "phase": "Attivo (€0/mo Gemini)"},
        {"id": "17", "name": "Fiscal Simulator & Doc Org", "cycle": "1° del mese + Trimestrale", "phase": "Attivo (€0/mo Gemini)"}
    ]

    conn = get_db_connection()
    cursor = conn.cursor()

    for agent in agents_def:
        agent_id_str = agent["id"]
        cursor.execute("""
            SELECT action, status, created_at FROM agent_logs
            WHERE agent_name LIKE ?
            ORDER BY id DESC LIMIT 1
        """, (f"%{agent_id_str}%",))
        row = cursor.fetchone()

        if row:
            agent["last_action"] = row["action"]
            agent["status"] = row["status"]
            agent["last_run"] = row["created_at"]
        else:
            agent["last_action"] = "Pronto all esecuzione"
            agent["status"] = "PENDING"
            agent["last_run"] = "-"

    conn.close()
    return jsonify(agents_def)

@app.route("/api/proposals")
def get_proposals():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM decision_log 
        WHERE proposed_by LIKE '%Agente 15%' 
        ORDER BY id DESC LIMIT 5
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route("/api/decide_proposal", methods=["POST"])
def decide_proposal():
    data = request.json
    proposal_id = data.get("id")
    action = data.get("action")
    now_str = datetime.now().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE decision_log 
        SET decided_by = 'Kimi', date_decided = ?, date_executed = ?
        WHERE id = ?
    """, (now_str, now_str if action == 'APPROVA' else None, proposal_id))

    cursor.execute("""
        INSERT INTO agent_logs (agent_name, action, details, status, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, ('SYSTEM', 'DECISION_KIMI', f'Kimi ha impostato {action} sulla proposta #{proposal_id}', 'SUCCESS', now_str))

    conn.commit()
    conn.close()

    from agents.agent_04_analytics import run_agent_04
    run_agent_04()

    return jsonify({"success": True, "message": f"Proposta #{proposal_id} registrata come {action}!"})

@app.route("/api/run_agent/<agent_id>", methods=["POST"])
def trigger_agent(agent_id):
    agent_mapping = {
        "15": ("agents.agent_15_supervisor", "run_agent_15"),
        "01": ("agents.agent_01_marketing_content", "run_agent_01"),
        "02": ("agents.agent_02_paid_ads", "run_agent_02"),
        "03": ("agents.agent_03_customer_care", "run_agent_03"),
        "04": ("agents.agent_04_analytics", "run_agent_04"),
        "05": ("agents.agent_05_supply_chain", "run_agent_05"),
        "06": ("agents.agent_06_email_marketing", "run_agent_06"),
        "07": ("agents.agent_07_social_media", "run_agent_07"),
        "08": ("agents.agent_08_seo_content", "run_agent_08"),
        "09": ("agents.agent_09_revenue_pricing", "run_agent_09"),
        "10": ("agents.agent_10_pre_sales", "run_agent_10"),
        "11": ("agents.agent_11_social_proof", "run_agent_11"),
        "12": ("agents.agent_12_compliance", "run_agent_12"),
        "13": ("agents.agent_13_brand_intelligence", "run_agent_13"),
        "14": ("agents.agent_14_market_research", "run_agent_14"),
        "16": ("agents.agent_16_bandi_radar", "run_agent_16"),
        "17": ("agents.agent_17_fiscal_simulator", "run_agent_17"),
        "18": ("agents.agent_18_agronomic_consultant", "Agent18AgronomicConsultant")
    }

    if agent_id in agent_mapping:
        mod_name, func_name = agent_mapping[agent_id]
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
        if agent_id == "18":
            consultant = func()
            res = consultant.generate_daily_briefing()
            return jsonify({"success": True, "message": "Agente 18 eseguito!", "data": res})
        else:
            func()
            return jsonify({"success": True, "message": f"Agente {agent_id} eseguito con successo!"})
    else:
        return jsonify({"success": False, "message": f"Agente {agent_id} non valido."})

@app.route("/api/agronomo/briefing", methods=["GET"])
def agronomo_briefing():
    from agents.agent_18_agronomic_consultant import Agent18AgronomicConsultant
    consultant = Agent18AgronomicConsultant()
    res = consultant.generate_daily_briefing()
    return jsonify({"success": True, "briefing": res})

@app.route("/api/shopify/status", methods=["GET"])
def shopify_status():
    import shopify_client
    shop_info = shopify_client.get_shop_info()
    products = shopify_client.get_products(limit=10)
    orders = shopify_client.get_orders(limit=10)
    customers = shopify_client.get_customers(limit=10)
    
    return jsonify({
        "connected": bool(shop_info.get("id")),
        "store_name": shop_info.get("name", "N/D"),
        "myshopify_domain": shop_info.get("myshopify_domain", shopify_client.SHOPIFY_STORE),
        "email": shop_info.get("email"),
        "currency": shop_info.get("currency", "EUR"),
        "plan": shop_info.get("plan_name", "basic"),
        "total_products_online": len(products),
        "total_orders_online": len(orders),
        "total_customers_online": len(customers)
    })

@app.route("/api/shopify/sync", methods=["POST"])
def shopify_sync():
    import shopify_client
    result = shopify_client.sync_shopify_to_local_db()
    return jsonify({"success": True, "result": result, "message": "Sincronizzazione completata con successo!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

