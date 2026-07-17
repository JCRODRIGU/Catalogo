from flask import Flask, render_template, request
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from urllib.parse import urlencode 

app = Flask(__name__)

# --- NUEVA FUNCIÓN: CONSTRUCTOR DE URLs PARA FILTROS ---
def generar_url(tipo, valor, cats, pubs, vers):
    c = cats.copy()
    p = pubs.copy()
    v = vers.copy()
    
    if tipo == 'categoria':
        if valor in c: c.remove(valor)
        else: c.append(valor)
    elif tipo == 'publico':
        if valor in p: p.remove(valor)
        else: p.append(valor)
    elif tipo == 'version':
        if valor in v: v.remove(valor)
        else: v.append(valor)
        
    params = []
    for x in c: params.append(('categoria', x))
    for x in p: params.append(('publico', x))
    for x in v: params.append(('version', x))
    
    if not params: return "/"
    return "/?" + urlencode(params)

# --- FUNCIONES DE IMAGEN ---
def contar_imagenes(codigo):
    contador = 0
    if os.path.exists(os.path.join('static', '0-imagenes', f"{codigo}.jpg")):
        contador += 1
    while True:
        sufijo = f"_{contador + 1 if contador > 0 else 1}"
        ruta = os.path.join('static', '0-imagenes', f"{codigo}{sufijo}.jpg")
        if os.path.exists(ruta):
            contador += 1
        else:
            break
    return contador

def obtener_ruta_imagen(codigo, indice):
    if indice == 1:
        ruta_base = os.path.join('static', '0-imagenes', f"{codigo}.jpg")
        if os.path.exists(ruta_base): return f"0-imagenes/{codigo}.jpg"
        else: return f"0-imagenes/{codigo}_1.jpg"
    return f"0-imagenes/{codigo}_{indice}.jpg"

app.jinja_env.globals.update(contar_imagenes=contar_imagenes, obtener_ruta_imagen=obtener_ruta_imagen, generar_url=generar_url)

# --- CONFIGURACIÓN GOOGLE SHEETS ---
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
if creds_json:
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

client = gspread.authorize(creds)
sheet = client.open_by_key("1YJ4ioXBTDSUifqoMf3VY2_vhakrmOY6q8RS9aituNKk").worksheet("CATALOGO")

def limpiar_precio(valor):
    if isinstance(valor, (int, float)): return float(valor)
    limpio = str(valor).replace('$', '').replace('.', '').replace(',', '')
    try: return float(limpio)
    except ValueError: return 0.0

def get_data():
    datos = sheet.get_all_records()
    productos_limpios = []
    for p in datos:
        nombre = str(p.get('PRODUCTO', '')).strip()
        codigo = str(p.get('CODIGO', '')).strip()
        p['PRECIO'] = limpiar_precio(p.get('PRECIO', 0))
        existe_img = os.path.exists(os.path.join('static', '0-imagenes', f"{codigo}.jpg")) or \
                     os.path.exists(os.path.join('static', '0-imagenes', f"{codigo}_1.jpg"))
        if len(nombre) > 2 and codigo != "" and existe_img:
            productos_limpios.append(p)
    return productos_limpios

@app.route('/')
def index():
    todos_los_productos = get_data()
    
    # Capturar filtros de selección
    cats = request.args.getlist('categoria')
    pubs = request.args.getlist('publico')
    vers = request.args.getlist('version')
    
    # Calcular límites de precios globales
    precios = [p['PRECIO'] for p in todos_los_productos if p['PRECIO'] > 0]
    min_global = min(precios) if precios else 0
    max_global = max(precios) if precios else 100000
    
    # Capturar parámetros del slider
    p_min_actual = float(request.args.get('precio_min', min_global))
    p_max_actual = float(request.args.get('precio_max', max_global))
    
    # Listas para los botones
    categorias = sorted(list(set(p['CATEGORIA'] for p in todos_los_productos if p.get('CATEGORIA'))))
    publicos = sorted(list(set(p['PUBLICO'] for p in todos_los_productos if p.get('PUBLICO'))))
    versiones = sorted(list(set(p['VERSION'] for p in todos_los_productos if p.get('VERSION'))))
    
    # Filtrado final
    productos = [p for p in todos_los_productos 
                 if p_min_actual <= p['PRECIO'] <= p_max_actual
                 and (not cats or p['CATEGORIA'] in cats)
                 and (not pubs or p['PUBLICO'] in pubs)
                 and (not vers or p['VERSION'] in vers)]
    
    return render_template('index.html', 
                           productos=productos,
                           categorias=categorias, publicos=publicos, versiones=versiones,
                           cat_activos=cats, pub_activos=pubs, ver_activos=vers,
                           min_g=min_global, max_g=max_global,
                           p_min_actual=p_min_actual, p_max_actual=p_max_actual)
        
if __name__ == '__main__':
    app.run(debug=True)