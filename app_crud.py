import pandas as pd
import streamlit as st 
import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os

# Umgebungsvariablen laden (Cargar variables de entorno)
load_dotenv()

# --- SEITENKONFIGURATION (Configuración de página) ---
st.set_page_config(page_title="Metadaten Management", layout="wide")

# --- DATENBANKVERBINDUNG MIT CACHE (Conexión a BD) ---
# Wir nutzen cache_resource, um die Verbindung nicht bei jedem Klick neu aufzubauen
@st.cache_resource
def get_connection():
    user = os.getenv('user')
    password = os.getenv('password')
    host = os.getenv("host")
    port = os.getenv("port")
    database = os.getenv("database")

    # Sicherstellen, dass alle Variablen vorhanden sind
    if not all([user, password, host, port, database]):
        st.error("Fehlende Umgebungsvariablen in der .env Datei")
        st.stop()

    engine = create_engine(
        f"mssql+pyodbc://{user}:{password}@{host}:{port}/{database}?"
        "driver=ODBC+Driver+17+for+SQL+Server&"
        "TrustServerCertificate=yes"
    )
    return engine

# --- CRUD FUNKTIONEN (Funciones CRUD) ---

# 1. READ (Daten lesen)
def get_all_data():
    conn = get_connection()
    try:
        sql = "SELECT * FROM metadaten_info"
        df = pd.read_sql_query(sql, conn)
        return df
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
        return pd.DataFrame()

# 2. CREATE (Datensatz erstellen)
def create_data(d_id, d_name, person, role, path):
    engine = get_connection()
    timestamp = datetime.datetime.now()
    
    insert_sql = text("""
    INSERT INTO metadaten_info (datenbank_id, datenbank_name, verantwortlicher_person, rolle, pfad_quellen, letztes_update) 
    VALUES (:id, :name, :person, :role, :path, :update)
    """)
    
    try:
        with engine.begin() as conn: 
            conn.execute(insert_sql, {
                "id": d_id, "name": d_name, "person": person, 
                "role": role, "path": path, "update": timestamp
            })
            st.success(f"✅ Datenbank '{d_name}' erfolgreich gespeichert.")
    except Exception as e:
        st.error(f"❌ Fehler beim Speichern: {e}")

# 3. UPDATE (Datensatz aktualisieren)
def update_data(original_id, d_name, person, role, path):
    engine = get_connection()
    timestamp = datetime.datetime.now()
    
    update_sql = text("""
    UPDATE metadaten_info 
    SET datenbank_name = :name, 
        verantwortlicher_person = :person, 
        rolle = :role, 
        pfad_quellen = :path, 
        letztes_update = :update
    WHERE datenbank_id = :id
    """)
    
    try:
        with engine.begin() as conn:
            conn.execute(update_sql, {
                "id": original_id, "name": d_name, "person": person, 
                "role": role, "path": path, "update": timestamp
            })
            st.success(f"🔄 Eintrag '{original_id}' erfolgreich aktualisiert.")
    except Exception as e:
        st.error(f"❌ Fehler beim Aktualisieren: {e}")

# 4. DELETE (Datensatz löschen)
def delete_data(d_id):
    engine = get_connection()
    delete_sql = text("DELETE FROM metadaten_info WHERE datenbank_id = :id")
    
    try:
        with engine.begin() as conn:
            conn.execute(delete_sql, {"id": d_id})
            st.success(f"🗑️ Eintrag '{d_id}' gelöscht.")
    except Exception as e:
        st.error(f"❌ Fehler beim Löschen: {e}")

# --- BENUTZEROBERFLÄCHE (UI) ---

st.title("🗃️ Metadaten Management System")

# Seitenleiste für Navigation
menu = st.sidebar.selectbox("Menü", ["Daten anzeigen", "Neuer Eintrag", "Bearbeiten/Löschen"])

# BEREICH: DATEN ANZEIGEN (READ)
if menu == "Daten anzeigen":
    st.subheader("📋 Metadaten Liste")
    df = get_all_data()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # Button zum manuellen Aktualisieren
        if st.button("Tabelle aktualisieren"):
            st.rerun()
    else:
        st.info("Keine Daten verfügbar oder Verbindung fehlgeschlagen.")

# BEREICH: NEUER EINTRAG (CREATE)
elif menu == "Neuer Eintrag":
    st.subheader("➕ Neue Datenbank hinzufügen")
    
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d_id = col1.text_input("Datenbank ID (Eindeutig)")
        d_name = col2.text_input("Datenbank Name")
        person = col1.text_input("Verantwortliche Person")
        role = col2.selectbox("Rolle", ["Admin", "Data Engineer", "Analyst", "Viewer", "Manager"])
        path = st.text_input("Pfad Quellen")
        
        submitted = st.form_submit_button("Speichern")
        
        if submitted:
            if d_id and d_name:
                create_data(d_id, d_name, person, role, path)
            else:
                st.warning("⚠️ ID und Name sind erforderlich!")

# BEREICH: BEARBEITEN ODER LÖSCHEN (UPDATE / DELETE)
elif menu == "Bearbeiten/Löschen":
    st.subheader("✏️ Datensätze verwalten")
    
    df = get_all_data()
    
    if not df.empty:
        # ID auswählen, die bearbeitet werden soll
        list_ids = df['datenbank_id'].tolist()
        selected_id = st.selectbox("Wähle ID zum Bearbeiten/Löschen:", list_ids)
        
        # Aktuelle Daten für diese ID abrufen (zum Vorausfüllen des Formulars)
        current_data = df[df['datenbank_id'] == selected_id].iloc[0]
        
        st.divider()
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### 📝 Informationen bearbeiten")
            with st.form("edit_form"):
                # ID anzeigen, aber deaktiviert (Primary Key sollte nicht geändert werden)
                st.text_input("ID (Nicht änderbar)", value=current_data['datenbank_id'], disabled=True)
                
                new_name = st.text_input("Datenbank Name", value=current_data['datenbank_name'])
                new_person = st.text_input("Verantwortliche Person", value=current_data['verantwortlicher_person'])
                
                # Logik, um die aktuelle Rolle als Standard auszuwählen
                roles_list = ["Admin", "Data Engineer", "Analyst", "Viewer", "Manager"]
                current_role_index = roles_list.index(current_data['rolle']) if current_data['rolle'] in roles_list else 0
                new_role = st.selectbox("Rolle", roles_list, index=current_role_index)
                
                new_path = st.text_input("Pfad Quellen", value=current_data['pfad_quellen'])
                
                update_submitted = st.form_submit_button("Daten aktualisieren")
                if update_submitted:
                    update_data(selected_id, new_name, new_person, new_role, new_path)
                    st.rerun() # Seite neu laden, um Änderungen zu sehen
        
        with col2:
            st.markdown("### 🚨 Gefahrenzone")
            st.warning("Diese Aktion kann nicht rückgängig gemacht werden.")
            if st.button("Eintrag löschen", type="primary"):
                delete_data(selected_id)
                st.rerun() # Seite neu laden
                
    else:
        st.info("Keine Daten zum Bearbeiten vorhanden.")