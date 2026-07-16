from flask import Flask, render_template, request
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

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
        if os.path.exists(ruta_base):
            return f"0-imagenes/{codigo}.jpg"
        else:
            return f"0-imagenes/{codigo}_1.jpg"
    return f"0-imagenes/{codigo}_{indice}.jpg"

app.jinja_env.globals.update(contar_imagenes=contar_imagenes, obtener_ruta_imagen=obtener_ruta_imagen)

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

def get_data():
    datos = sheet.get_all_records()
    productos_limpios = []
    for p in datos:
        nombre = str(p.get('PRODUCTO', '')).strip()
        codigo = str(p.get('CODIGO', '')).strip()
        # Verificar imágenes para validar producto
        existe_img = os.path.exists(os.path.join('static', '0-imagenes', f"{codigo}.jpg")) or \
                     os.path.exists(os.path.join('static', '0-imagenes', f"{codigo}_1.jpg"))
        if len(nombre) > 2 and codigo != "" and existe_img:
            productos_limpios.append(p)
    return productos_limpios

@app.route('/')
def index():
    todos_los_productos = get_data()
    
    # Capturamos como listas usando .getlist
    cats = request.args.getlist('categoria')
    pubs = request.args.getlist('publico')
    vers = request.args.getlist('version')
    
    # Filtrado acumulativo
    productos = todos_los_productos
    if cats: productos = [p for p in productos if p['CATEGORIA'] in cats]
    if pubs: productos = [p for p in productos if p['PUBLICO'] in pubs]
    if vers: productos = [p for p in productos if p['VERSION'] in vers]
        
    categorias = sorted(list(set(p['CATEGORIA'] for p in todos_los_productos if p.get('CATEGORIA'))))
    publicos = sorted(list(set(p['PUBLICO'] for p in todos_los_productos if p.get('PUBLICO'))))
    versiones = sorted(list(set(p['VERSION'] for p in todos_los_productos if p.get('VERSION'))))
    
    return render_template('index.html', 
                           productos=productos, 
                           categorias=categorias, publicos=publicos, versiones=versiones,
                           cat_activos=cats, pub_activos=pubs, ver_activos=vers)
    
if __name__ == '__main__':
    app.run(debug=True)