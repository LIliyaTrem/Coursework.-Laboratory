import sqlite3 as sql
import config

# функция для соединения с базой данных и внешнего ключа и создания
def connection():
    conn = sql.connect(config.database_name + '.db')
    conn.execute("PRAGMA foreign_keys = ON;")
    c = conn.cursor()
    return conn, c

# функция для установления соединения с базой данных и создания таблиц
def db_init():
    conn, c = connection()
    with conn:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS patient_record (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                blood_group TEXT NOT NULL,
                contact_number_1 TEXT NOT NULL,
                contact_number_2 TEXT,
                weight INTEGER NOT NULL,
                height INTEGER NOT NULL,
                address TEXT NOT NULL,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                pin_code TEXT NOT NULL,
                next_of_kin_name TEXT NOT NULL,
                next_of_kin_relation_to_patient TEXT NOT NULL,
                next_of_kin_contact_number TEXT NOT NULL,
                email_id TEXT,
                date_of_registration TEXT NOT NULL,
                time_of_registration TEXT NOT NULL
            );
            """
        )
    with conn:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS doctor_record (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                blood_group TEXT NOT NULL,
                department_id TEXT NOT NULL,
                department_name TEXT NOT NULL,
                contact_number_1 TEXT NOT NULL,
                contact_number_2 TEXT,
                email_id TEXT NOT NULL UNIQUE,
                qualification TEXT NOT NULL,
                specialisation TEXT NOT NULL,
                years_of_experience INTEGER NOT NULL,
                address TEXT NOT NULL,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                pin_code TEXT NOT NULL,
                FOREIGN KEY (department_id) REFERENCES department_record(id)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
            );
            """
        )
    with conn:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS department_record (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                contact_number_1 TEXT NOT NULL,
                contact_number_2 TEXT,
                address TEXT NOT NULL,
                email_id TEXT NOT NULL UNIQUE
            );
            """
        )
    with conn:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS prescription_record (
                id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                patient_name TEXT NOT NULL,
                doctor_id TEXT NOT NULL,
                doctor_name TEXT NOT NULL,
                diagnosis TEXT NOT NULL,
                comments TEXT,
                medicine_1_name TEXT NOT NULL,
                medicine_1_dosage_description TEXT NOT NULL,
                medicine_2_name TEXT,
                medicine_2_dosage_description TEXT,
                medicine_3_name TEXT,
                medicine_3_dosage_description TEXT,
                FOREIGN KEY (patient_id) REFERENCES patient_record(id)
                ON UPDATE CASCADE
                ON DELETE RESTRICT,
                FOREIGN KEY (doctor_id) REFERENCES doctor_record(id)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
            );
            """
        )
    with conn:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS medical_test_record (
                id TEXT PRIMARY KEY,
                test_name TEXT NOT NULL,
                patient_id TEXT NOT NULL,
                patient_name TEXT NOT NULL,
                doctor_id TEXT NOT NULL,
                doctor_name TEXT NOT NULL,
                medical_lab_scientist_id TEXT NOT NULL,
                test_date_time TEXT NOT NULL,
                result_date_time TEXT NOT NULL,
                result_and_diagnosis TEXT,
                description TEXT,
                comments TEXT,
                cost INTEGER NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patient_record(id)
                ON UPDATE CASCADE
                ON DELETE RESTRICT,
                FOREIGN KEY (doctor_id) REFERENCES doctor_record(id)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
            );
            """
        )
    conn.close()