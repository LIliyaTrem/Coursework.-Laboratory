import streamlit as st
from datetime import datetime
import database as db
import pandas as pd
import patient
import doctor
import app

# функция для проверки ID рецепта
def verify_prescription_id(prescription_id):
    verify = False
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT id
            FROM prescription_record;
            """
        )
    for id in c.fetchall():
        if id[0] == prescription_id:
            verify = True
            break
    conn.close()
    return verify

# функция для отображения сведений о рецептах
def show_prescription_details(list_of_prescriptions):
    prescription_titles = ['ID рецепта', 'ID пациента', 'Имя пациента',
                           'ID врача', 'Имя врача', 'Диагноз', 'Комментарии',
                           'Название лекарства 1', 'Дозировка и описание лекарства 1',
                           'Название лекарства 2', 'Дозировка и описание лекарства 2',
                           'Название лекарства 3', 'Дозировка и описание лекарства 3',]
    if len(list_of_prescriptions) == 0:
        st.warning('Нет данных')
    elif len(list_of_prescriptions) == 1:
        prescription_details = [x for x in list_of_prescriptions[0]]
        series = pd.Series(data = prescription_details, index = prescription_titles)
        st.write(series)
    else:
        prescription_details = []
        for prescription in list_of_prescriptions:
            prescription_details.append([x for x in prescription])
        df = pd.DataFrame(data = prescription_details, columns = prescription_titles)
        st.write(df)

# функция для создания уникального ID рецепта с использованием текущей даты и времени
def generate_prescription_id():
    id_1 = datetime.now().strftime('%S%M%H')
    id_2 = datetime.now().strftime('%Y%m%d')[2:]
    id = f'M-{id_1}-{id_2}'
    return id

# функция для получения имени пациента из базы данных для данного ID пациента
def get_patient_name(patient_id):
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT name
            FROM patient_record
            WHERE id = :id;
            """,
            { 'id': patient_id }
        )
    return c.fetchone()[0]

# функция для получения имени врача из базы данных для заданного ID врача
def get_doctor_name(doctor_id):
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT name
            FROM doctor_record
            WHERE id = :id;
            """,
            { 'id': doctor_id }
        )
    return c.fetchone()[0]

# класс, содержащий все поля и методы, необходимые для работы с таблицей рецептов в базе данных
class Prescription:

    def __init__(self):
        self.id = str()
        self.patient_id = str()
        self.patient_name = str()
        self.doctor_id = str()
        self.doctor_name = str()
        self.diagnosis = str()
        self.comments = str()
        self.medicine_1_name = str()
        self.medicine_1_dosage_description = str()
        self.medicine_2_name = str()
        self.medicine_2_dosage_description = str()
        self.medicine_3_name = str()
        self.medicine_3_dosage_description = str()

    # метод для добавления новой записи рецепта в базу данных
    def add_prescription(self):
        st.write('Введите данные рецепта:')
        patient_id = st.text_input('ID пациента')
        if patient_id == '':
            st.empty()
        elif not patient.verify_patient_id(patient_id):
            st.error('Пациент не найден')
        else:
            st.success('Верно')
            self.patient_id = patient_id
            self.patient_name = get_patient_name(patient_id)
        doctor_id = st.text_input('ID врача')
        if doctor_id == '':
            st.empty()
        elif not doctor.verify_doctor_id(doctor_id):
            st.error('Врач не найден')
        else:
            st.success('Верно')
            self.doctor_id = doctor_id
            self.doctor_name = get_doctor_name(doctor_id)
        self.diagnosis = st.text_area('Диагноз')
        comments = st.text_area('Описание (не объезательно)')
        self.comments = (lambda comments : None if comments == '' else comments)(comments)
        self.medicine_1_name = st.text_input('Лекарство 1 название')
        self.medicine_1_dosage_description = st.text_area('Лекарство 1 дозировка и описание')
        med_2_name = st.text_input('Название лекарства 2 (если есть)')
        self.medicine_2_name = (lambda name : None if name == '' else name)(med_2_name)
        med_2_dose_desc = st.text_area('Лекарство 2 дозировка и описание')
        self.medicine_2_dosage_description = (lambda dose_desc: None if dose_desc == '' else dose_desc)(med_2_dose_desc)
        med_3_name = st.text_input('Название лекарства 3 (если есть)')
        self.medicine_3_name = (lambda name : None if name == '' else name)(med_3_name)
        med_3_dose_desc = st.text_area('Лекарство 3 дозировка и описание')
        self.medicine_3_dosage_description = (lambda dose_desc: None if dose_desc == '' else dose_desc)(med_3_dose_desc)
        self.id = generate_prescription_id()
        save = st.button('Сохранить')

       # SQLite для сохранения новой записи рецепта в базе данных
        if save:
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    INSERT INTO prescription_record
                    (
                        id, patient_id, patient_name, doctor_id,
                        doctor_name, diagnosis, comments,
                        medicine_1_name, medicine_1_dosage_description,
                        medicine_2_name, medicine_2_dosage_description,
                        medicine_3_name, medicine_3_dosage_description
                    )
                    VALUES (
                        :id, :p_id, :p_name, :dr_id, :dr_name, :diagnosis,
                        :comments, :med_1_name, :med_1_dose_desc, :med_2_name,
                        :med_2_dose_desc, :med_3_name, :med_3_dose_desc
                    );
                    """,
                    {
                        'id': self.id, 'p_id': self.patient_id,
                        'p_name': self.patient_name, 'dr_id': self.doctor_id,
                        'dr_name': self.doctor_name, 'diagnosis': self.diagnosis,
                        'comments': self.comments,
                        'med_1_name': self.medicine_1_name,
                        'med_1_dose_desc': self.medicine_1_dosage_description,
                        'med_2_name': self.medicine_2_name,
                        'med_2_dose_desc': self.medicine_2_dosage_description,
                        'med_3_name': self.medicine_3_name,
                        'med_3_dose_desc': self.medicine_3_dosage_description,
                    }
                )
            st.success('Сведения о рецепте успешно сохранены.')
            st.write('ID рецепта: ', self.id)
            conn.close()

    # метод для обновления существующей записи рецепта в базе данных
    def update_prescription(self):
        id = st.text_input('Введите ID рецепта, который необходимо обновить.')
        if id == '':
            st.empty()
        elif not verify_prescription_id(id):
            st.error('Недействительный ID рецепта')
        else:
            st.success('Верно')
            conn, c = db.connection()

            # показывает текущие детали рецепта перед обновлением
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM prescription_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Вот текущие детали рецепта:')
                show_prescription_details(c.fetchall())

            st.write('Введите новые данные рецепта:')
            self.diagnosis = st.text_area('Диагноз')
            comments = st.text_area('Коментарии')
            self.comments = (lambda comments : None if comments == '' else comments)(comments)
            self.medicine_1_name = st.text_input('Лекарство 1 название')
            self.medicine_1_dosage_description = st.text_area('Лекарство 1 дозировка и описание')
            med_2_name = st.text_input('Лекарство 2 название (необязательно)')
            self.medicine_2_name = (lambda name : None if name == '' else name)(med_2_name)
            med_2_dose_desc = st.text_area('Лекарство 2 дозировка и описание')
            self.medicine_2_dosage_description = (lambda dose_desc: None if dose_desc == '' else dose_desc)(med_2_dose_desc)
            med_3_name = st.text_input('Лекарство 3 название (необязательно)')
            self.medicine_3_name = (lambda name : None if name == '' else name)(med_3_name)
            med_3_dose_desc = st.text_area('Лекарство 3 дозировка и описание')
            self.medicine_3_dosage_description = (lambda dose_desc: None if dose_desc == '' else dose_desc)(med_3_dose_desc)
            update = st.button('Обновить')

            # SQLite для обновления записи этого рецепта в базе данных
            if update:
                with conn:
                    c.execute(
                        """
                        UPDATE prescription_record
                        SET diagnosis = :diagnosis, comments = :comments,
                        medicine_1_name = :med_1_name,
                        medicine_1_dosage_description = :med_1_dose_desc,
                        medicine_2_name = :med_2_name,
                        medicine_2_dosage_description = :med_2_dose_desc,
                        medicine_3_name = :med_3_name,
                        medicine_3_dosage_description = :med_3_dose_desc
                        WHERE id = :id;
                        """,
                        {
                            'id': id, 'diagnosis': self.diagnosis,
                            'comments': self.comments,
                            'med_1_name': self.medicine_1_name,
                            'med_1_dose_desc': self.medicine_1_dosage_description,
                            'med_2_name': self.medicine_2_name,
                            'med_2_dose_desc': self.medicine_2_dosage_description,
                            'med_3_name': self.medicine_3_name,
                            'med_3_dose_desc': self.medicine_3_dosage_description
                        }
                    )
                st.success('Сведения о рецепте успешно обновлены.')
                conn.close()

    # метод для удаления существующей записи рецепта из базы данных
    def delete_prescription(self):
        id = st.text_input('Введите ID рецепта, который необходимо удалить.')
        if id == '':
            st.empty()
        elif not verify_prescription_id(id):
            st.error('ID не найден')
        else:
            st.success('Верно')
            conn, c = db.connection()

            # показывает текущие детали рецепта перед удалением
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM prescription_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Детали рецепта, который нужно удалить:')
                show_prescription_details(c.fetchall())

                confirm = st.checkbox('Установите флажок, чтобы подтвердить удаление')
                if confirm:
                    delete = st.button('Удалить')

                    # SQLite для удаления записи этого рецепта из базы данных
                    if delete:
                        c.execute(
                            """
                            DELETE FROM prescription_record
                            WHERE id = :id;
                            """,
                            { 'id': id }
                        )
                        st.success('Сведения о рецепте успешно удалены')
            conn.close()

    # способ показать все рецепты конкретного пациента
    def prescriptions_by_patient(self):
        patient_id = st.text_input('Введите ID пациента, чтобы получить запись о назначении этого пациента')
        if patient_id == '':
            st.empty()
        elif not patient.verify_patient_id(patient_id):
            st.error('Неверный ID')
        else:
            st.success('Верно')
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM prescription_record
                    WHERE patient_id = :p_id;
                    """,
                    { 'p_id': patient_id }
                )
                st.write('Запись рецепта', get_patient_name(patient_id), ':')
                show_prescription_details(c.fetchall())
            conn.close()
