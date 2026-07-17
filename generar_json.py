import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials

# Configuración (la misma que ya tienes)
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1YJ4ioXBTDSUifqoMf3VY2_vhakrmOY6q8RS9aituNKk").worksheet("CATALOGO")

def generar_archivo():
    print("Descargando datos...")
    datos = sheet.get_all_records()
    productos = []
    for p in datos:
        codigo = str(p.get('CODIGO', '')).strip()
        # Verificar imágenes (esto puedes hacerlo manualmente si quieres)
        if codigo:
            # Limpiamos precio aquí para no sufrir en JS
            try:
                p['PRECIO'] = float(str(p.get('PRECIO', 0)).replace('.','').replace('$',''))
            except:
                p['PRECIO'] = 0
            productos.append(p)
    
    with open('productos.json', 'w', encoding='utf-8') as f:
        json.dump(productos, f, ensure_ascii=False, indent=4)
    print("¡Archivo productos.json generado con éxito!")

if __name__ == '__main__':
    generar_archivo()