import os
import sys
import sqlite3

# DB in same folder as EXE
app_folder = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(app_folder, "database.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_beneficiaries():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        beneficiary_id,
        COALESCE(NULLIF(lname, ''), '-'),
        COALESCE(NULLIF(fname, ''), '-'),
        COALESCE(NULLIF(mname, ''), '-'),
        COALESCE(NULLIF(suffix, ''), '-'),
        COALESCE(NULLIF(gender, ''), '-'),
        COALESCE(NULLIF(street, ''), '-'),
        COALESCE(NULLIF(barangay, ''), '-'),
        COALESCE(NULLIF(contactno, ''), '-'),
        project_id
    FROM beneficiaries
    """)

    beneficiaries = cursor.fetchall()
    conn.close()
    return beneficiaries

def get_beneficiary_by_id(beneficiary_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT lname, fname, mname, suffix, gender, street, barangay, contactno, project_id
            FROM beneficiaries
            WHERE beneficiary_id = ?
        """, (beneficiary_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        print("Fetch Error:", e)
        return None

def validate_beneficiary(lname, fname, suffix, project_id, mname="", beneficiary_id=None):
    if not lname.strip() or not fname.strip():
        return False, "Last name and First name are required."

    if project_id is None:
        return False, "Please select a valid project."

    mname = mname.strip()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Optional: check project exists
        cursor.execute("SELECT category FROM projects WHERE project_id = ?", (project_id,))
        project = cursor.fetchone()
        if not project:
            return False, "Invalid project selected."

        # Check for duplicates, excluding current beneficiary if editing
        query = """
            SELECT COUNT(*) FROM beneficiaries
            WHERE lname = ? AND fname = ? AND mname = ? AND suffix = ?
        """
        params = [lname, fname, mname, suffix]

        if beneficiary_id is not None:
            query += " AND beneficiary_id != ?"
            params.append(beneficiary_id)

        cursor.execute(query, params)

        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, "Duplicate beneficiary exists."

        conn.close()
        return True, ""

    except Exception as e:
        return False, f"Database error: {e}"


def add_beneficiary(lname, fname, project_id, mname="", suffix="", gender="", street="", barangay="", contactno=""):

    mname = mname.strip()
    street = street.strip()
    barangay = barangay.strip()
    contactno = contactno.strip()

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO beneficiaries
            (lname, fname, mname, suffix, gender, street, barangay, contactno, project_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (lname, fname, mname, suffix, gender, street, barangay, contactno, project_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Add Error:", e)

def edit_beneficiary(beneficiary_id, lname, fname, project_id, mname="", suffix="", gender="", street="", barangay="", contactno=""):
    mname = mname.strip()
    street = street.strip()
    barangay = barangay.strip()
    contactno = contactno.strip()

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE beneficiaries
            SET lname = ?, fname = ?, mname = ?, suffix = ?, gender = ?, street = ?, barangay = ?, contactno = ?, project_id = ?
            WHERE beneficiary_id = ?
        """, (
    lname, fname, mname, suffix, gender,
    street, barangay, contactno,
    project_id, beneficiary_id
))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Edit Error:", e)

def delete_beneficiary(beneficiary_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM beneficiaries WHERE beneficiary_id=?", (beneficiary_id,))
    
    conn.commit()
    conn.close()

def has_livelihood_project(beneficiary_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM beneficiary_projects bp
        JOIN projects p ON bp.project_id = p.project_id
        WHERE bp.beneficiary_id = ?
          AND p.category = 'LIVELIHOOD'
    """, (beneficiary_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0
