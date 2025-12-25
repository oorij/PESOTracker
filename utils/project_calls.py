import os
import sys
import sqlite3

# DB in same folder as EXE
app_folder = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(app_folder, "database.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_projects_list():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT project_id, project_name, category FROM projects"
        )
        return cursor.fetchall()

def get_projects_map():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT project_id, project_name FROM projects"
        )
        return dict(cursor.fetchall())

def get_project_by_id(project_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT project_name, category FROM projects WHERE project_id = ?",
            (project_id,)
        )
        return cursor.fetchone()
    
def validate_project(project_name, category):
    project_name = project_name.strip()
    category = category.strip()

    if not project_name or not category:
        return False, "Project Name and Category are required."

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM projects
            WHERE project_name = ? AND category = ?
            LIMIT 1
        """, (project_name, category))

        if cursor.fetchone():
            return False, "Project already exists."

    return True, ""
    
def add_project(project_name, category):
    project_name = project_name.strip() or "-"
    category = category.strip() or "-"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO projects (project_name, category)
            VALUES (?, ?)
        """, (project_name, category))

def edit_project(project_id, project_name, category):
    project_name = project_name.strip() or "-"
    category = category.strip() or "-"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE projects
            SET project_name = ?, category = ?
            WHERE project_id = ?
        """, (project_name, category, project_id))


def delete_project(project_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM projects WHERE project_id = ?",
            (project_id,)
        )