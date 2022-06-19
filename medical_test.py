import streamlit as st
from datetime import datetime, time
import database as db
import pandas as pd
import patient
import doctor

# функция для проверки ID анализа
def verify_medical_test_id(medical_test_id):
    verify = False
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT id
            FROM medical_test_record;
            """
        )
    for id in c.fetchall():
        if id[0] == medical_test_id:
            verify = True
            break
    conn.close()
    return verify

# функция для отображения сведений о анализах указанных в списке
def show_medical_test_details(list_of_medical_tests):
    medical_test_titles = ['ID анализа', 'Название', 'ID пациента',
                           'Имя пациента', 'ID врача', 'Имя врача',
                           'ID лаборанта',
                           'Дата и время проверки [ДД-ММ-ГГГГ (чч:мм)]',
                           'Дата и время результата [ДД-ММ-ГГГГ (чч:мм)]',
                           'Результат и диагноз', 'Описание',
                           'Комментарии', 'Стоимость (руб)']
    if len(list_of_medical_tests) == 0:
        st.warning('Нет данных')
    elif len(list_of_medical_tests) == 1:
        medical_test_details = [x for x in list_of_medical_tests[0]]
        series = pd.Series(data = medical_test_details, index = medical_test_titles)
        st.write(series)
    else:
        medical_test_details = []
        for medical_test in list_of_medical_tests:
            medical_test_details.append([x for x in medical_test])
        df = pd.DataFrame(data = medical_test_details, columns = medical_test_titles)
        st.write(df)

# функция для создания уникального ID анализа с использованием текущей даты и времени
def generate_medical_test_id():
    id_1 = datetime.now().strftime('%S%M%H')
    id_2 = datetime.now().strftime('%Y%m%d')[2:]
    id = f'T-{id_1}-{id_2}'
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

# класс, содержащий все поля и методы, необходимые для работы с таблицей медицинских тестов в базе данных
class Medical_Test:

    def __init__(self):
        self.id = str()
        self.test_name = str()
        self.patient_id = str()
        self.patient_name = str()
        self.doctor_id = str()
        self.doctor_name = str()
        self.medical_lab_scientist_id = str()
        self.test_date_time = str()
        self.result_date_time = str()
        self.cost = int()
        self.result_and_diagnosis = str()
        self.description = str()
        self.comments = str()

    # метод для добавления новой записи о анализе в базу данных
    def add_medical_test(self):
        st.write('Введите данные анализа:')
        self.test_name = st.text_input('Название')
        patient_id = st.text_input('ID пациента')
        if patient_id == '':
            st.empty()
        elif not patient.verify_patient_id(patient_id):
            st.error('ID неверный')
        else:
            st.success('Верно')
            self.patient_id = patient_id
            self.patient_name = get_patient_name(patient_id)
        doctor_id = st.text_input('ID доктора')
        if doctor_id == '':
            st.empty()
        elif not doctor.verify_doctor_id(doctor_id):
            st.error('ID неверное')
        else:
            st.success('Верно')
            self.doctor_id = doctor_id
            self.doctor_name = get_doctor_name(doctor_id)
        self.medical_lab_scientist_id = st.text_input('ID лаборанта')
        test_date = st.date_input('Дата (YYYY/MM/DD)').strftime('%d-%m-%Y')
        st.info('Если нужной даты нет в календаре, введите ее в поле выше.')
        test_time = st.time_input('Время (hh:mm)', time(0, 0)).strftime('%H:%M')
        st.info('Если требуемое время отсутствует в раскрывающемся списке, введите его в поле выше.')
        self.test_date_time = f'{test_date} ({test_time})'
        result_date = st.date_input('Дата результата (YYYY/MM/DD)').strftime('%d-%m-%Y')
        st.info('Если нужной даты нет в календаре, введите ее в поле выше.')
        result_time = st.time_input('Время результата (hh:mm)', time(0, 0)).strftime('%H:%M')
        st.info('Если требуемое время отсутствует в раскрывающемся списке, введите его в поле выше.')
        self.result_date_time = f'{result_date} ({result_time})'
        self.cost = st.number_input('Стоймость (руб)', value = 0, min_value = 0, max_value = 10000)
        result_and_diagnosis = st.text_area('Результат')
        self.result_and_diagnosis = (lambda res_diag : 'Ожидается результат теста' if res_diag == '' else res_diag)(result_and_diagnosis)
        description = st.text_area('Описание')
        self.description = (lambda desc : None if desc == '' else desc)(description)
        comments = st.text_area('Комментарии (если есть)')
        self.comments = (lambda comments : None if comments == '' else comments)(comments)
        self.id = generate_medical_test_id()
        save = st.button('Сохранить')

        #SQLite для сохранения новой записи о анализк в базу данных
        if save:
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    INSERT INTO medical_test_record
                    (
                        id, test_name, patient_id, patient_name, doctor_id,
                        doctor_name, medical_lab_scientist_id, test_date_time,
                        result_date_time, cost, result_and_diagnosis, description,
                        comments
                    )
                    VALUES (
                        :id, :name, :p_id, :p_name, :dr_id, :dr_name, :mls_id,
                        :test_date_time, :result_date_time, :cost,
                        :result_diagnosis, :desc, :comments
                    );
                    """,
                    {
                        'id': self.id, 'name': self.test_name,
                        'p_id': self.patient_id, 'p_name': self.patient_name,
                        'dr_id': self.doctor_id, 'dr_name': self.doctor_name,
                        'mls_id': self.medical_lab_scientist_id,
                        'test_date_time': self.test_date_time,
                        'result_date_time': self.result_date_time, 'cost': self.cost,
                        'result_diagnosis': self.result_and_diagnosis,
                        'desc': self.description, 'comments': self.comments
                    }
                )
            st.success('Сведения о анализах успешно сохранены.')
            st.write('ID анализа: ', self.id)
            conn.close()

    # обновить существующую запись о анализе в базе данных
    def update_medical_test(self):
        id = st.text_input('Введите ID анализа, чтобы обновить')
        if id == '':
            st.empty()
        elif not verify_medical_test_id(id):
            st.error('ID не найден')
        else:
            st.success('Верно')
            conn, c = db.connection()

            # показывает текущую информацию о медицинском тесте перед обновлением
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM medical_test_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Данные об анализе:')
                show_medical_test_details(c.fetchall())

            st.write('Введите новые данные анализа:')
            result_and_diagnosis = st.text_area('Результат')
            self.result_and_diagnosis = (lambda res_diag : 'Ожидается результат теста' if res_diag == '' else res_diag)(result_and_diagnosis)
            description = st.text_area('Описание')
            self.description = (lambda desc : None if desc == '' else desc)(description)
            comments = st.text_area('Коментарий')
            self.comments = (lambda comments : None if comments == '' else comments)(comments)
            update = st.button('Обновить')

            # SQLite для обновления записи анализа в базе данных
            if update:
                with conn:
                    c.execute(
                        """
                        UPDATE medical_test_record
                        SET result_and_diagnosis = :result_diagnosis,
                        description = :description, comments = :comments
                        WHERE id = :id;
                        """,
                        {
                            'id': id, 'result_diagnosis': self.result_and_diagnosis,
                            'description': self.description, 'comments': self.comments
                        }
                    )
                st.success('Сведения о анализе успешно обновлены.')
                conn.close()

   # метод для удаления существующей записи о анализе из базы данных
    def delete_medical_test(self):
        id = st.text_input('Введите ID анализа для удаления')
        if id == '':
            st.empty()
        elif not verify_medical_test_id(id):
            st.error('ID неверный')
        else:
            st.success('Верно')
            conn, c = db.connection()

            # просморт анализа перед удалением
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM medical_test_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Анализ который вы удаляете:')
                show_medical_test_details(c.fetchall())

                confirm = st.checkbox('Установите флажок, чтобы подтвердить удаление')
                if confirm:
                    delete = st.button('Удалить')

                    # SQLite для удаления записи анализа из базы данных
                    if delete:
                        c.execute(
                            """
                            DELETE FROM medical_test_record
                            WHERE id = :id;
                            """,
                            { 'id': id }
                        )
                        st.success('Анализ удален')
            conn.close()

    # медот показывает все анализы конкретного пациента
    def medical_tests_by_patient(self):
        patient_id = st.text_input('Введите ID пациента, чтобы получить медицинскую карту пациента.')
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
                    FROM medical_test_record
                    WHERE patient_id = :p_id;
                    """,
                    { 'p_id': patient_id }
                )
                st.write('Медкарта пациента', get_patient_name(patient_id), ':')
                show_medical_test_details(c.fetchall())
            conn.close()
