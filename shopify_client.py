import os
import requests
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key

load_dotenv()

ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
SHOPIFY_STORE = os.getenv('SHOPIFY_STORE', 'your-store.myshopify.com')
CLIENT_ID = os.getenv('SHOPIFY_CLIENT_ID', '')
CLIENT_SECRET = os.getenv('SHOPIFY_CLIENT_SECRET', '')
ADMIN_API_TOKEN = os.getenv('SHOPIFY_ADMIN_API_TOKEN', '')
API_VERSION = os.getenv('SHOPIFY_API_VERSION', '2024-10')
DB_PATH = os.getenv('DB_PATH', 'rosso_vivo.db')


def refresh_access_token():
    """Rinnova il token di accesso tramite Client Credentials Grant (Shopify M2M)"""
    global ADMIN_API_TOKEN
    if not CLIENT_ID or not CLIENT_SECRET:
        print("[SHOPIFY] Client credentials not set in environment.")
        return None

    url = f"https://{SHOPIFY_STORE}/admin/oauth/access_token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            data = res.json()
            ADMIN_API_TOKEN = data.get("access_token")
            os.environ['SHOPIFY_ADMIN_API_TOKEN'] = ADMIN_API_TOKEN
            try:
                set_key(ENV_PATH, 'SHOPIFY_ADMIN_API_TOKEN', ADMIN_API_TOKEN)
            except Exception:
                pass
            return ADMIN_API_TOKEN
    except Exception as e:
        print(f"[SHOPIFY] Errore rinnovo token: {e}")
    return None


def get_headers():
    global ADMIN_API_TOKEN
    if not ADMIN_API_TOKEN:
        refresh_access_token()
    return {
        'X-Shopify-Access-Token': ADMIN_API_TOKEN,
        'Content-Type': 'application/json'
    }


def is_connected():
    return bool(ADMIN_API_TOKEN and not ADMIN_API_TOKEN.startswith("your_"))


def shopify_request(method, endpoint, params=None, json_data=None):
    url = f"https://{SHOPIFY_STORE}/admin/api/{API_VERSION}/{endpoint}.json"
    headers = get_headers()
    
    try:
        res = requests.request(method, url, headers=headers, params=params, json=json_data, timeout=45)
        if res.status_code == 401:
            print("[SHOPIFY] 401 Unauthorized - Attempting token refresh...")
            new_token = refresh_access_token()
            if new_token:
                headers = get_headers()
                res = requests.request(method, url, headers=headers, params=params, json=json_data, timeout=45)
        return res
    except Exception as e:
        print(f"[SHOPIFY] Errore richiesta {method} {endpoint}: {e}")
        return None


def sync_inventory_from_shopify():
    """Scarica livelli inventario e aggiorna il database locale SQLite"""
    res = shopify_request('GET', 'products')
    if not res or res.status_code != 200:
        print("[SHOPIFY] Impossibile scaricare prodotti.")
        return False
        
    products = res.json().get('products', [])
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    
    for prod in products:
        for var in prod.get('variants', []):
            sku = var.get('sku')
            qty = var.get('inventory_quantity', 0)
            if sku:
                cursor.execute("""
                    INSERT INTO inventory (sku, stock_kg, available_kg, last_updated)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(sku) DO UPDATE SET
                    stock_kg = excluded.stock_kg,
                    available_kg = excluded.available_kg,
                    last_updated = excluded.last_updated
                """, (sku, qty, qty, now_str))
                
    conn.commit()
    conn.close()
    return True
