import sqlite3
import os
import csv

# ==============================================================================
# Demo LLM - Phase C : Étape 1a : Setup SQL Marvel (Données Structurées)
# ==============================================================================
# Ce script initialise la base de données en lisant des fichiers CSV externes.
# ASPECT CLÉ : Séparation des données et de la logique pour plus de clarté.
# ==============================================================================

DB_PATH = os.path.join("data", "marvel_data.db")
DATA_DIR = "data"

def setup_database():
    print(f"\n[INITIALISATION] Connexion à la base de données : {DB_PATH}")
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # On repart de zéro pour la démo
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(" [INFO] Ancienne base supprimée.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("[ACTION] Création des tables...")

    cursor.execute("""
    CREATE TABLE heroes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        superhero_name TEXT,
        real_name TEXT,
        intelligence INTEGER,
        strength INTEGER,
        speed INTEGER,
        durability INTEGER,
        energy_projection INTEGER,
        fighting_skills INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        release_year INTEGER,
        box_office_revenue_mil REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE hero_appearances (
        hero_id INTEGER,
        movie_id INTEGER,
        PRIMARY KEY (hero_id, movie_id),
        FOREIGN KEY (hero_id) REFERENCES heroes (id),
        FOREIGN KEY (movie_id) REFERENCES movies (id)
    )
    """)

    # --- ALIMENTATION VIA CSV ---
    
    # 1. Héros
    print(" [ACTION] Chargement de heroes.csv...")
    with open(os.path.join(DATA_DIR, "heroes.csv"), mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT INTO heroes (superhero_name, real_name, intelligence, strength, speed, durability, energy_projection, fighting_skills)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (row['superhero_name'], row['real_name'], int(row['intelligence']), int(row['strength']), 
                  int(row['speed']), int(row['durability']), int(row['energy_projection']), int(row['fighting_skills'])))

    # 2. Films
    print(" [ACTION] Chargement de movies.csv...")
    with open(os.path.join(DATA_DIR, "movies.csv"), mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT INTO movies (title, release_year, box_office_revenue_mil)
                VALUES (?, ?, ?)
            """, (row['title'], int(row['release_year']), float(row['box_office_revenue_mil'])))

    # 3. Apparitions (Relation basée sur les noms pour la facilité du CSV)
    print(" [ACTION] Chargement de hero_appearances.csv...")
    with open(os.path.join(DATA_DIR, "hero_appearances.csv"), mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # On récupère les IDs via les noms
            cursor.execute("SELECT id FROM heroes WHERE superhero_name = ?", (row['superhero_name'],))
            hero_id = cursor.fetchone()[0]
            cursor.execute("SELECT id FROM movies WHERE title = ?", (row['movie_title'],))
            movie_id = cursor.fetchone()[0]
            
            cursor.execute("INSERT OR IGNORE INTO hero_appearances (hero_id, movie_id) VALUES (?, ?)", (hero_id, movie_id))

    conn.commit()
    conn.close()
    print("\n[SUCCÈS] Base SQLite initialisée à partir des fichiers CSV.")

if __name__ == "__main__":
    setup_database()

if __name__ == "__main__":
    setup_database()
