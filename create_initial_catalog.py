import os
import base64
import shopify_client
import time

def encode_image(filepath, alt_text):
    if not os.path.exists(filepath):
        print(f"File non trovato: {filepath}")
        return None
    with open(filepath, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return {
        "attachment": encoded,
        "filename": os.path.basename(filepath),
        "alt": alt_text
    }

def create_catalog_with_images():
    print("--- CARICAMENTO CATALOGO UFFICIALE CON IMMAGINI SU SHOPIFY ---")
    
    img_box_10kg = encode_image("static/images/box_10kg.jpg", "Cassetta 10kg Arance Rosse Tarocco Lempso Rosso Vivo")
    img_hero = encode_image("static/images/hero_tarocco.jpg", "Arance Rosse Tarocco Lempso spaccate polpa rossa Etna")
    img_spremuta = encode_image("static/images/spremuta.jpg", "Spremuta fresca di arance rosse Tarocco di Sicilia")
    img_gift = encode_image("static/images/gift_box.jpg", "Gift Box Premium Selezione Rosso Vivo")
    img_raccolta = encode_image("static/images/contadino_etna.jpg", "Raccolta a mano arance rosse Sicilia")

    # 1. Best Seller: Cassetta 10kg
    p1 = {
        "title": "Cassetta 10kg — Arance Rosse Tarocco Lempso",
        "product_type": "Agrumi Freschi",
        "vendor": "Rosso Vivo",
        "tags": "arance rosse, tarocco lempso, sicilia, best seller, 10kg, piana di catania",
        "body_html": """
        <p><strong>Il nostro Best Seller. Arance rosse di Sicilia raccolte ieri e spedite oggi direttamente dall'agrumeto a casa tua.</strong></p>
        <p>Il <em>Tarocco Lempso</em> &egrave; rinomato per la sua polpa intensamente pigmentata, ricchissima di antocianine naturali e con un perfetto equilibrio zuccherino (elevato grado Brix) che dona quel gusto inconfondibile che non trovi nei supermercati.</p>
        <ul>
            <li><strong>Formato:</strong> Cassetta da 10 kg (~50-60 arance freschissime)</li>
            <li><strong>Origine:</strong> Contrada Jannarello, Piana di Catania, Sicilia</li>
            <li><strong>Trattamenti post-raccolta:</strong> ZERO. Nessuna cera, nessun conservante superficiale.</li>
            <li><strong>Spedizione:</strong> Rapida in 24/48h con imballaggio protettivo 100% riciclabile.</li>
        </ul>
        """,
        "variants": [
            {
                "price": "39.90",
                "sku": "RV-LEMPSO-10KG",
                "inventory_management": "shopify",
                "inventory_policy": "continue",
                "requires_shipping": True,
                "weight": 10.0,
                "weight_unit": "kg",
                "title": "Default Title"
            }
        ],
        "images": [img_box_10kg, img_hero] if img_box_10kg else []
    }

    # 2. Cassetta 5kg
    p2 = {
        "title": "Cassetta 5kg — Arance Rosse Tarocco Lempso",
        "product_type": "Agrumi Freschi",
        "vendor": "Rosso Vivo",
        "tags": "arance rosse, tarocco lempso, sicilia, 5kg",
        "body_html": """
        <p><strong>Il formato compatto perfetto per coppie o consumi settimanali.</strong></p>
        <p>Tutta la freschezza e la pigmentazione del vero Tarocco Lempso della Piana di Catania, raccolto a mano e spedito immediatamente per preservare intatte vitamina C e proprietà antiossidanti.</p>
        <ul>
            <li><strong>Formato:</strong> Cassetta da 5 kg (~25 arance)</li>
            <li><strong>Origine:</strong> Sicilia (Piana di Catania)</li>
            <li><strong>Trattamenti:</strong> Nessun trattamento chimico post-raccolta.</li>
            <li><strong>Spedizione:</strong> Diretta dal campo in 24/48h.</li>
        </ul>
        """,
        "variants": [
            {
                "price": "24.90",
                "sku": "RV-LEMPSO-5KG",
                "inventory_management": "shopify",
                "inventory_policy": "continue",
                "requires_shipping": True,
                "weight": 5.0,
                "weight_unit": "kg",
                "title": "Default Title"
            }
        ],
        "images": [img_hero, img_box_10kg] if img_hero else []
    }

    # 3. Cassetta 15kg Scorta Famiglia
    p3 = {
        "title": "Cassetta 15kg Scorta Famiglia — Arance Rosse Tarocco Lempso",
        "product_type": "Agrumi Freschi",
        "vendor": "Rosso Vivo",
        "tags": "arance rosse, tarocco lempso, 15kg, scorta, famiglia, spremute",
        "body_html": """
        <p><strong>La massima convenienza per veri amanti della spremuta fresca e famiglie numerose.</strong></p>
        <p>Una scorta generosa di arance Tarocco Lempso ad altissima resa in succo. Frutti selezionati dal nostro agrumeto nella Valle del Simeto a 45m s.l.m., dove le forti escursioni termiche esaltano il tipico colore rosso rubino.</p>
        <ul>
            <li><strong>Formato:</strong> Cassetta da 15 kg (€ 3.66/kg)</li>
            <li><strong>Origine:</strong> Sicilia (C.da Jannarello)</li>
            <li><strong>Spedizione:</strong> 24/48h tracciata.</li>
        </ul>
        """,
        "variants": [
            {
                "price": "54.90",
                "sku": "RV-LEMPSO-15KG",
                "inventory_management": "shopify",
                "inventory_policy": "continue",
                "requires_shipping": True,
                "weight": 15.0,
                "weight_unit": "kg",
                "title": "Default Title"
            }
        ],
        "images": [img_spremuta, img_box_10kg] if img_spremuta else []
    }

    # 4. Gift Box Premium
    p4 = {
        "title": "Gift Box Premium — Selezione Pregiata Rosso Vivo",
        "product_type": "Confezioni Regalo",
        "vendor": "Rosso Vivo",
        "tags": "gift box, regalo, natale, premium, tarocco lempso, confezione lusso",
        "body_html": """
        <p><strong>L'eccellenza agrumicola siciliana in un'esclusiva confezione regalo da donare o regalarsi.</strong></p>
        <p>Selezione manuale dei calibri più grandi e perfetti di Tarocco Lempso, incartati singolarmente in carta velina pregiata all'interno di un'elegante box rigida kraft con nastro in tessuto, sigillo di garanzia e cartolina dell'agrumeto con note di degustazione.</p>
        <ul>
            <li><strong>Contenuto:</strong> Selezione calibro extra frutti scelti</li>
            <li><strong>Packaging:</strong> Confezione regalo ecosostenibile di lusso + nastro in seta e cartolina</li>
            <li><strong>Ideale per:</strong> Regali aziendali, festività natalizie e occasioni speciali.</li>
        </ul>
        """,
        "variants": [
            {
                "price": "49.90",
                "sku": "RV-GIFTBOX-PREMIUM",
                "inventory_management": "shopify",
                "inventory_policy": "continue",
                "requires_shipping": True,
                "weight": 8.0,
                "weight_unit": "kg",
                "title": "Default Title"
            }
        ],
        "images": [img_gift] if img_gift else []
    }

    # 5. Pre-ordine Early Bird Prima Raccolta
    p5 = {
        "title": "PRE-ORDINE — Cassetta 10kg Prima Raccolta Dicembre",
        "product_type": "Pre-ordini",
        "vendor": "Rosso Vivo",
        "tags": "pre-ordine, offerta lancio, prima raccolta, dicembre, sconto",
        "body_html": """
        <p><strong>Prenota in anteprima le prime arance della stagione 2026/2027 a prezzo di lancio bloccato.</strong></p>
        <p>Le prime arance Tarocco Lempso verranno staccate dall'albero a metà dicembre, non appena avranno raggiunto il perfetto viraggio di pigmentazione rossa e la maturazione ottimale. Prenotando ora ti assicuri il primo lotto di raccolta con uno sconto speciale di benvenuto.</p>
        <ul>
            <li><strong>Prezzo Promozionale Pre-ordine:</strong> € 29.90 anziché € 39.90</li>
            <li><strong>Consegna garantita:</strong> Settimana pre-natalizia (15-20 Dicembre)</li>
            <li><strong>Quantità disponibili:</strong> Limitata ai primi 300 ordini riservati della campagna pre-lancio.</li>
        </ul>
        """,
        "variants": [
            {
                "price": "29.90",
                "compare_at_price": "39.90",
                "sku": "RV-PREORDINE-10KG",
                "inventory_management": "shopify",
                "inventory_policy": "continue",
                "requires_shipping": True,
                "weight": 10.0,
                "weight_unit": "kg",
                "title": "Default Title"
            }
        ],
        "images": [img_box_10kg, img_raccolta] if img_box_10kg else []
    }

    products = [p1, p2, p3, p4, p5]
    created = []

    for p in products:
        print(f"Caricamento '{p['title']}' con relative immagini...")
        res = shopify_client.shopify_post('products', {'product': p})
        prod_data = res.get('product', {})
        if prod_data.get('id'):
            print(f"  -> OK! Creato con ID {prod_data.get('id')} e {len(prod_data.get('images', []))} immagini.")
            created.append(prod_data)
        else:
            print(f"  -> ERRORE: {res}")
        time.sleep(1.0) # rate limit prudenziale per upload immagini pesanti

    print(f"\nCOMPLETATO! Creati con successo {len(created)} prodotti con immagini su Shopify.")
    return created

if __name__ == "__main__":
    create_catalog_with_images()
