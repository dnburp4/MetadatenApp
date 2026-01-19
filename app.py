import pandas as pd
import streamlit as st 
import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os

load_dotenv()

def database_connection():

    user = os.getenv('user')
    password = os.getenv('password')
    host = os.getenv("host")
    port = os.getenv("port")
    database = os.getenv("database")

    engine = create_engine(
    f"mssql+pyodbc://{user}:{password}@{host}:{port}/{database}?"
    "driver=ODBC+Driver+17+for+SQL+Server&"
    "TrustServerCertificate=yes"
    )

    return engine
    


def load_data(datenbank_id, datenbank_name, verantwortlicher_person, rolle, pfad_quellen):

    metadata_to_insert = {
        "datenbank_id": datenbank_id, 
        "datenbank_name": datenbank_name, 
        "verantwortlicher_person": verantwortlicher_person, 
        "rolle": rolle,
        "pfad_quellen": pfad_quellen,
        "letztes_update": datetime.datetime.now()
    }

    insert_to_sql = text("""
    INSERT INTO metadaten_info (datenbank_id, datenbank_name, verantwortlicher_person, rolle, pfad_quellen, letztes_update) 
    VALUES (:datenbank_id, :datenbank_name, :verantwortlicher_person, :rolle, :pfad_quellen, :letztes_update)
    """
    )


    with database_connection().begin() as conn: 
        conn.execute(insert_to_sql, metadata_to_insert)

        st.success(f"Metadaten für die Datenbank {datenbank_name} erfolgreich gespeichert")


st.header("Metadaten Datenbank")


with st.form("Metadaten_form", clear_on_submit=True, enter_to_submit=False):

    datenbank_id = st.text_input("datenbank_id") 
    datenbank_name = st.text_input("datenbank_name")
    verantwortlicher_person = st.text_input("verantwortlicher_person")
    rolle = st.selectbox("Rolle", ["Admin", "Data Engineer", "Analyst", "Viewer", "Manager"])
    pfad_quellen = st.text_input("pfad_quellen")

    submitted = st.form_submit_button(
        "Speichern"
    )

    if submitted: 
        if datenbank_id and datenbank_name: 
            try:
                load_data(datenbank_id, datenbank_name, verantwortlicher_person, rolle, pfad_quellen)
            except Exception as e: 
                st.error(f"Fehler beim Speichern {e}")
        else: 
            st.error("Bitte mindestens ID und Name angeben!")

df_table = pd.read_sql_query(
    """
SELECT * FROM metadaten_info
""", database_connection()
)

st.dataframe(df_table)

