import streamlit as st

def mostrar_efecto_mundial():
    st.markdown("""
    <style>
        /* Contenedor que llena la pantalla pero no bloquea clics */
        .contenedor-balones {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            pointer-events: none;
            z-index: 9999;
            overflow: hidden;
        }
        /* El estilo de cada balón */
        .balon {
            position: absolute;
            top: -50px;
            font-size: 25px;
            animation: caer 8s linear infinite;
        }
        @keyframes caer {
            0% { transform: translateY(0); }
            100% { transform: translateY(110vh); }
        }
        /* Generamos varios balones con diferentes retrasos y posiciones */
        .balon:nth-child(1) { left: 10%; animation-delay: 0s; }
        .balon:nth-child(2) { left: 30%; animation-delay: 2s; }
        .balon:nth-child(3) { left: 50%; animation-delay: 4s; }
        .balon:nth-child(4) { left: 70%; animation-delay: 6s; }
        .balon:nth-child(5) { left: 90%; animation-delay: 1s; }
    </style>
    
    <div class="contenedor-balones">
        <div class="balon">⚽</div>
        <div class="balon">⚽</div>
        <div class="balon">⚽</div>
        <div class="balon">⚽</div>
        <div class="balon">⚽</div>
    </div>
    """, unsafe_allow_html=True)

# Llama a la función al principio
mostrar_efecto_mundial()

import urllib.parse
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import re
import urllib.parse
from streamlit_carousel import carousel

# --- 1. CONFIGURACIÓN ---
ID_CARPETA_IMAGENES = "1vlB4xwewupJU1GZj2ZPsfbKXDB7Jrjf4"
st.set_page_config(page_title="Librería Logos", layout="wide", initial_sidebar_state="collapsed")

# --- 2. DISEÑO CSS (FIJO Y ESTÉTICO) ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display: none;}
    .block-container { padding-top: 0.5rem !important; }
    
    .portada-validada { text-align: center; padding: 30px 15px; background: white; }
    .logo-grande { width: 100%; max-width: 320px; height: auto; margin-bottom: 20px; }
    
    /* BLOQUE FIJO PARA BOTONES */
    [data-testid="stVerticalBlock"] > div:has(div.nav-container) {
        position: sticky;
        top: 0rem;
        background-color: white;
        z-index: 1000;
        padding-bottom: 10px;
        border-bottom: 2px solid #002366;
    }

    .producto-card-gigante {
        background: white; padding: 20px; border-radius: 25px;
        border: 1px solid #eee; margin-bottom: 30px; text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.07);
    }
    
    .descripcion-box {
        background: #f9f9f9; padding: 12px; border-radius: 12px;
        text-align: left; margin: 12px 0; border-left: 5px solid #2e7d32; font-size: 0.9em;
    }

    .stButton > button { border-radius: 15px !important; font-weight: bold !important; height: 50px !important; }
    
    div.stButton > button:first-child[kind="primary"] {
        background-color: #2e7d32 !important;
        color: white !important;
        border: none !important;
    }

    .barra-resumen {
        background: #002366; color: white; padding: 10px; border-radius: 10px;
        text-align: center; margin-bottom: 10px; font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. NUEVA LÓGICA DE CLASIFICACIÓN GRANULAR TOTAL ---
def clasificar_inteligente(nombre):
    n = nombre.upper()

    # ---------------- BIBLIAS ----------------

    if "BIBLIA" in n:

        categorias = []

        if any(x in n for x in ["ESTUDIO", "EXPLICADA", "REFERENCIAS", "ANOTADA"]):
            categorias.append("DE ESTUDIO")

        if any(x in n for x in ["VALIENTE","SIEMPRE","PEQUEÑITOS","ACCIÓN","PORTATIL",
                                "VIVAMOS","BEBE","HEROE","NIÑO","NIÑA","PEQUEÑOS",
                                "ILUSTRADA","HISTORIAS","AVENTURA"]):
            categorias.append("INFANTILES")

        if any(x in n for x in ["BIBLIA AGENDA","RVR1960","CRONOLOGICO",
                                "PASTORAL","APUNTES","REINA VALERA",
                                "RVR60","RV1960","RV 1960"]):
            categorias.append("REINA VALERA 1960")

        if "NTV" in n or "VIVIENTE" in n:
            categorias.append("NTV (NUEVA TRAD. VIVIENTE)")

        if "NVI" in n or "INTERNACIONAL" in n:
            categorias.append("NVI (NUEVA VERS. INTERNACIONAL)")

        if "TLA" in n or "LENGUAJE ACTUAL" in n:
            categorias.append("LENGUAJE ACTUAL")

        if "BILINGÜE" in n or "INGLES" in n:
            categorias.append("BILINGÜES")

        if any(x in n for x in [
            "LETRA GRANDE",
            "LETRA GIGANTE",
            "SUPERGIGANTE",
            "ULTRAGIGANTE"
        ]):
            categorias.append("LETRA GRANDE")

        if not categorias:
            categorias.append("OTRAS VERSIONES")

        return "BIBLIAS", categorias

    # ---------------- LIBROS ----------------

    if any(x in n for x in ["MATRIMONIO", "ESPOSO", "ESPOSA", "PAREJA", "BODA", "AMOR"]):
        return "LIBROS", ["FAMILIA Y MATRIMONIO"]

    if any(x in n for x in ["HIJO", "PADRES", "CRIANZA", "MAMÁ", "PAPÁ"]):
        return "LIBROS", ["FAMILIA Y MATRIMONIO"]

    if any(x in n for x in ["MUJER", "PRINCESA", "DAMA", "CONFORME"]):
        return "LIBROS", ["MUJERES"]

    # etc...

    # ---------------- DETALLES ----------------

    if any(x in n for x in ["MUG", "POCILLO", "VASO"]):
        return "DETALLES", ["MUGS Y TAZAS"]

    if any(x in n for x in ["CAMISETA", "T-SHIRT", "ROPA"]):
        return "DETALLES", ["CAMISETAS"]

    if any(x in n for x in ["DIARIO", "AGENDA", "LIBRETA"]):
        return "DETALLES", ["AGENDAS Y DIARIOS"]

    return "LIBROS", ["LITERATURA GENERAL"]

# --- 4. CARGA DE DATOS ---
@st.cache_data(ttl=300)
def cargar_todo():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive.readonly"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("cre.json", scope)
        srv = build('drive', 'v3', credentials=creds)
        res = srv.files().list(q=f"'{ID_CARPETA_IMAGENES}' in parents and trashed = false", fields="files(id, name)", pageSize=1000).execute()
        archivos = res.get('files', [])
        
        mapa_p = {} 
        l_id = None
        
        for f in archivos:
            nombre = f['name'].strip()
            if "Logo_2025.png" in nombre: 
                l_id = f['id']; continue
            
            # Limpiamos el nombre para comparaciones
            nombre_sin_ext = nombre.split('.')[0].strip()
            codigo_base = nombre_sin_ext.split('_')[0].strip().upper()
            
            if codigo_base not in mapa_p:
                mapa_p[codigo_base] = []
            
            # --- LÓGICA DE PRIORIDAD ---
            # Si el archivo es el código puro o termina en _1, va a la posición 0
            if nombre_sin_ext.upper() == codigo_base or nombre_sin_ext.upper().endswith('_1'):
                mapa_p[codigo_base].insert(0, f['id'])
            else:
                # Si es una foto secundaria, la agregamos al final
                mapa_p[codigo_base].append(f['id'])
            
        cli = gspread.authorize(creds)
        hoja = cli.open("Ventas").worksheet("INVENT")
        datos = hoja.get_all_values()
        db = []
        for f in datos[3:]:
            if len(f) < 22: continue
            codigo_n = str(f[13]).strip().replace(" ", "").upper()
            
            # Usamos get() por seguridad
            if codigo_n in mapa_p:
                nombre_prod = f[9]
                p_raw = re.sub(r'[^\d]', '', str(f[8]))
                
                cat_final, subs_finales = clasificar_inteligente(nombre_prod)

                db.append({
                    "id": codigo_n,
                    "nom": nombre_prod,
                    "pre": int(p_raw or 0),
                    "cat": cat_final,
                    "all_subs": subs_finales,
                    "fid": mapa_p.get(codigo_n, []),
                    "des": f[19] if len(f) > 19 and f[19] else "Disponible en Librería Cristiana Logos."
                })
        return db, l_id, mapa_p
    except Exception as e:
        # Imprimir el error en consola ayuda a saber por qué falla
        print(f"Error cargando datos: {e}")
        return [], None, {}

# Llamada correcta:
inv, logo_id, mapa_p = cargar_todo()

# --- 5. ESTADOS ---
if 'pagina' not in st.session_state: st.session_state.pagina = 'inicio'
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'query' not in st.session_state: st.session_state.query = ""

# --- 6. NAVEGACIÓN FIJA ---
if st.session_state.pagina != 'inicio':
    t_items = len(st.session_state.carrito)
    t_dinero = sum(x['pre'] for x in st.session_state.carrito)
    
    with st.container():
        st.markdown(f'<div class="nav-container"><div class="barra-resumen">🛒 {t_items} ítem(s) | <b>${t_dinero:,.0f}</b></div></div>', unsafe_allow_html=True)
        c_nav1, c_nav2 = st.columns(2)
        with c_nav1:
            if st.button("🏠 MENÚ", use_container_width=True):
                st.session_state.pagina = 'menu'; st.session_state.query = ""; st.rerun()
        with c_nav2:
            if st.button("📦 MI PEDIDO", use_container_width=True):
                st.session_state.pagina = 'final'; st.rerun()
    
    if st.session_state.pagina != 'final':
        st.session_state.query = st.text_input("🔍 Buscar por nombre o código...", value=st.session_state.query)

# --- 7. PANTALLAS ---
if st.session_state.pagina == 'inicio':
    url_l = f"https://drive.google.com/thumbnail?id={logo_id}&sz=w1000" if logo_id else ""
    st.markdown(f'''
        <div class="portada-validada">
            <img src="{url_l}" class="logo-grande">
            <p class="info-contacto"><b>Librería Cristiana Logos</b></p>
            <p class="info-contacto">Calle 35C Sur No 78A-18 Kennedy Central</p>
            <p class="info-contacto">Bogotá, Colombia | Celular 312-5756581</p>
            <div class="confianza-box">
                <p>🌟 <b>Compra con confianza</b></p>
                <p>Nequi, Daviplata, Efectivo</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("ENTRAR AL CATÁLOGO", use_container_width=True, type="primary"):
        st.session_state.pagina = 'menu'; st.rerun()

elif st.session_state.pagina == 'menu':
    if st.session_state.query: st.session_state.pagina = 'ver_productos'; st.rerun()
    st.subheader("Categorías Principales")
    cats = sorted(list(set(p['cat'] for p in inv if p['cat'])))
    for c in cats:
        n = len([p for p in inv if p['cat'] == c])
        if st.button(f"📁 {c} ({n})", use_container_width=True):
            st.session_state.f_cat = c; st.session_state.pagina = 'sub_menu'; st.rerun()

elif st.session_state.pagina == 'sub_menu':
    if st.session_state.query: st.session_state.pagina = 'ver_productos'; st.rerun()
    st.subheader(f"Sección: {st.session_state.f_cat}")
    subs_set = {s for p in inv if p['cat'] == st.session_state.f_cat for s in p['all_subs']}
    for s in sorted(list(subs_set)):
        n = len([p for p in inv if p['cat'] == st.session_state.f_cat and s in p['all_subs']])
        if st.button(f"{s} ({n})", use_container_width=True):
            st.session_state.f_sub = s; st.session_state.pagina = 'ver_productos'; st.rerun()

elif st.session_state.pagina == 'ver_productos':
    if st.session_state.query:
        q = st.session_state.query.upper()
        items_f = [p for p in inv if q in p['nom'].upper() or q in p['id'].upper()]
    else:
        items_f = [p for p in inv if p['cat'] == st.session_state.f_cat and st.session_state.f_sub in p['all_subs']]
        
    items_f.sort(key=lambda x: x['pre'], reverse=True)
    
    # AQUÍ PUEDES MOSTRAR EL CONTADOR REAL
    st.info(f"Mostrando {len(items_f)} productos en esta sección")
            
        # 2. ORDENAMIENTO (ESTO ES LO QUE BUSCABAS)
    # Esta línea asegura que, sin importar el filtro anterior, siempre ordene por precio
    items_f.sort(key=lambda x: x['pre'], reverse=True)
    
    # --- LÓGICA DE GRILLA (2 columnas para que se vea bien en celular) ---
    COLS_POR_FILA = 2
    for i in range(0, len(items_f), COLS_POR_FILA):
        fila = items_f[i:i + COLS_POR_FILA]
        cols = st.columns(COLS_POR_FILA)
        
        for idx, p in enumerate(fila):
            # --- REEMPLAZA LO QUE ESTABA AQUÍ POR ESTO ---
            with cols[idx]:
                st.markdown(f'<div class="producto-card-gigante">', unsafe_allow_html=True)
                
                # Obtenemos la lista de fotos de forma segura
                fotos = p.get('fid', [])
                
                # VISOR DE IMÁGENES ESTABLE
                if fotos and isinstance(fotos, list):
                    if len(fotos) > 1:
                        # Creamos pestañas para navegar entre fotos
                        tabs = st.tabs([f"📸 {i+1}" for i in range(len(fotos))])
                        for i, tab in enumerate(tabs):
                            with tab:
                                st.image(f"https://drive.google.com/thumbnail?id={fotos[i]}&sz=w400", use_container_width=True)
                    else:
                        # Si solo hay una imagen, la mostramos directa
                        st.image(f"https://drive.google.com/thumbnail?id={fotos[0]}&sz=w400", use_container_width=True)
                else:
                    st.warning("Sin imágenes")
                
                # Nombre y precio debajo de la imagen
                st.markdown(f'''
                    <div style="min-height: 80px;">
                        <b>{p["nom"]}</b><br>
                        <span style="color: #2e7d32; font-weight: bold;">${p["pre"]:,.0f}</span>
                    </div>
                ''', unsafe_allow_html=True)
                
                # --- NUEVO: BOTÓN DE DETALLES ---
                with st.expander("ℹ️ Ver descripción"):
                    st.markdown(f'<div class="descripcion-box">{p["des"]}</div>', unsafe_allow_html=True)
                
                # Tu botón de añadir sigue igual
                if st.button(f"🛒 AÑADIR", key=f"add_{p['id']}_{i}", type="primary", use_container_width=True):
                    st.session_state.carrito.append(p)
                    st.toast(f"✅ Añadido: {p['nom']}")
                
                st.markdown(f'</div>', unsafe_allow_html=True)
                
                # Link de WhatsApp integrado
                link_wpp = f"https://wa.me/573125756581?text=Hola,%20me%20interesa:%20{urllib.parse.quote(p['nom'])}"
                
              
elif st.session_state.pagina == 'final':
    st.header("🛒 Mi Pedido")
    if not st.session_state.carrito: 
        st.info("Tu carrito está vacío.")
    else:
        total = sum(x['pre'] for x in st.session_state.carrito)
        
        # --- LISTA DE PRODUCTOS CON MINIATURA ---
        for i, x in enumerate(st.session_state.carrito):
            col_img, col_txt, col_borrar = st.columns([0.6, 3, 1])
            
            # 1. MOSTRAR LA IMAGEN EN PEQUEÑO
            # Aseguramos que x['fid'] sea una lista y tomamos el primer elemento [0]
            fotos = x.get('fid', [])
            if fotos and isinstance(fotos, list):
                url_miniatura = f"https://drive.google.com/thumbnail?id={fotos[0]}&sz=w200"
                col_img.image(url_miniatura, width=50)
            else:
                col_img.write("🖼️") # Icono alternativo si no hay imagen
            
            # 2. NOMBRE DEL PRODUCTO
            col_txt.markdown(f"**{x['nom']}**\n\n${x['pre']:,.0f}")
            
            # 3. BOTÓN DE BORRAR (Sin la X roja gigante)
            if col_borrar.button("Borrar", key=f"del_{i}"): 
                st.session_state.carrito.pop(i)
                st.rerun()
        
        st.divider()
        st.subheader(f"Total: ${total:,.0f}")
        
        # --- MENSAJE DE WHATSAPP ---
        # Usamos el icono de la biblia/libro para el texto
        cuerpo_pedido = "\n".join([f"📖 {item['nom']} (Cód: {item['id']})" for item in st.session_state.carrito])
        msg = f"¡Hola Logos! 🌟 Quisiera realizar este pedido:\n\n{cuerpo_pedido}\n\n💰 *Total: ${total:,.0f}*"
        
        st.link_button("🚀 ENVIAR A WHATSAPP", 
                       f"https://wa.me/573125756581?text={urllib.parse.quote(msg)}", 
                       type="primary", 
                       use_container_width=True)
        
    if st.button("🗑️ VACIAR CARRITO"): 
        st.session_state.carrito = []
        st.session_state.pagina = 'menu'
        st.rerun()