#!/usr/bin/env python3
"""
Script pour réinitialiser la base de données des candidatures
"""

import os
import sqlite3
import sys
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def reset_database():
    """Supprime toutes les candidatures de la base de données"""
    db_path = os.getenv('DATABASE_PATH')
    
    if not db_path:
        print("Erreur: DATABASE_PATH non défini dans le fichier .env")
        sys.exit(1)
    
    # Vérifier si le chemin est absolu ou relatif
    if not os.path.isabs(db_path):
        # Convertir en chemin absolu relatif au répertoire du projet
        project_root = Path(__file__).parent.parent
        db_path = os.path.join(project_root, db_path)
    
    try:
        print(f"Connexion à la base de données: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Compter les candidatures avant suppression
        cursor.execute("SELECT COUNT(*) FROM applications")
        count_before = cursor.fetchone()[0]
        print(f"Nombre de candidatures avant suppression: {count_before}")
        
        # Supprimer toutes les candidatures
        cursor.execute("DELETE FROM applications")
        conn.commit()
        
        # Vérifier que tout a bien été supprimé
        cursor.execute("SELECT COUNT(*) FROM applications")
        count_after = cursor.fetchone()[0]
        print(f"Nombre de candidatures après suppression: {count_after}")
        
        print("Réinitialisation de la base de données terminée avec succès.")
        conn.close()
        return True
    
    except Exception as e:
        print(f"Erreur lors de la réinitialisation de la base de données: {e}")
        return False

if __name__ == "__main__":
    print("Réinitialisation de la base de données des candidatures...")
    reset_database()
