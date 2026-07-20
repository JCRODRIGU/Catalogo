import json
import os

def contar_publicados():
    # Cargar los productos
    try:
        with open('productos.json', 'r', encoding='utf-8') as f:
            productos = json.load(f)
    except FileNotFoundError:
        print("No se encontró el archivo productos.json")
        return

    # Contadores
    conteo = {
        "CATEGORIA": {},
        "PUBLICO": {}
    }

    print("Analizando inventario...")
    
    for p in productos:
        codigo = str(p.get('CODIGO', '')).strip()
        # Verificamos si existe alguna imagen del producto
        # (Esto imita la lógica que usa tu catálogo en el navegador)
        variantes = [f'{codigo}.jpg', f'{codigo}_1.jpg', f'{codigo}_2.jpg', f'{codigo}(1).jpg', f'{codigo}(2).jpg']
        tiene_imagen = any(os.path.exists(v) for v in variantes)
        
        if tiene_imagen:
            cat = p.get('CATEGORIA', 'Sin Categoría')
            pub = p.get('PUBLICO', 'Sin Público')
            
            conteo["CATEGORIA"][cat] = conteo["CATEGORIA"].get(cat, 0) + 1
            conteo["PUBLICO"][pub] = conteo["PUBLICO"].get(pub, 0) + 1

    # Mostrar resultados
    print("\n--- RESUMEN DE PRODUCTOS PUBLICADOS ---")
    print("\nPor Categoría:")
    for cat, total in conteo["CATEGORIA"].items():
        print(f"- {cat}: {total}")
        
    print("\nPor Público:")
    for pub, total in conteo["PUBLICO"].items():
        print(f"- {pub}: {total}")

if __name__ == '__main__':
    contar_publicados()