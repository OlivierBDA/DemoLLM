import sqlite3
import os
import csv

# ==============================================================================
# Demo LLM - Phase C : Étape 2a : Setup Catalogue (Gouvernance)
# ==============================================================================
# Ce script crée deux tables de métadonnées pour aider le LLM à naviguer 
# dans la base sans connaître les noms techniques a priori.
# ==============================================================================

DB_PATH = os.path.join("data", "marvel_data.db")
DATA_DIR = "data"

def setup_catalog():
    print(f"\n[INITIALISATION] Connexion à la base pour le Catalogue : {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(" [ERREUR] La base de données marvel_data.db est introuvable. Lancez l'étape 7a d'abord.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("[ACTION] Création des tables de catalogue...")

    # 1. CATALOGUE GLOBAL (Niveau Table)
    cursor.execute("DROP TABLE IF EXISTS table_catalog")
    cursor.execute("""
    CREATE TABLE table_catalog (
        table_name TEXT PRIMARY KEY,
        functional_domain TEXT,
        scope_description TEXT,
        business_concepts TEXT
    )
    """)

    # 2. CATALOGUE DÉTAILLÉ (Niveau Colonne)
    cursor.execute("DROP TABLE IF EXISTS column_catalog")
    cursor.execute("""
    CREATE TABLE column_catalog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_name TEXT,
        column_name TEXT,
        business_label TEXT,
        description TEXT,
        relationships TEXT,
        FOREIGN KEY (table_name) REFERENCES table_catalog (table_name)
    )
    """)

    print("[ACTION] Alimentation depuis les fichiers CSV...")

    # Chargement table_catalog
    print("  -> Chargement de table_catalog.csv...")
    with open(os.path.join(DATA_DIR, "table_catalog.csv"), mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT INTO table_catalog (table_name, functional_domain, scope_description, business_concepts)
                VALUES (?, ?, ?, ?)
            """, (row['table_name'], row['functional_domain'], row['scope_description'], row['business_concepts']))

    # Chargement column_catalog
    print("  -> Chargement de column_catalog.csv...")
    with open(os.path.join(DATA_DIR, "column_catalog.csv"), mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT INTO column_catalog (table_name, column_name, business_label, description, relationships)
                VALUES (?, ?, ?, ?, ?)
            """, (row['table_name'], row['column_name'], row['business_label'], row['description'], row['relationships']))

    conn.commit()
    conn.close()
    
    print("\n[SUCCÈS] Le Catalogue de Données Hiérarchique est prêt !")
    print(" Tables documentées : 3")
    print(" Colonnes documentées : 13")

if __name__ == "__main__":
    setup_catalog()
