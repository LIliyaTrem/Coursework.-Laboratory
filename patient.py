import streamlit as st
from datetime import datetime, date
import database as db
import pandas as pd

# функция для проверки id пациента
def verify_patient_id(patient_id):
    verify = False
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT id
            FROM patient_record;
            """
        )
    for id in c.fetchall():
        if id[0] == patient_id:
            verify = True
            break
    conn.close()
    return verify

# функция для создания уникального id пациента с использованием текущей даты и времени
def generate_patient_id(reg_date, reg_time):
    id_1 = ''.join(reg_time.split(':')[::-1])
    id_2 = ''.join(reg_date.split('-')[::-1])[2:]
    id = f'P-{id_1}-{id_2}'
    return id

# функция для вычисления возраста по дате рождения
def calculate_age(dob):
    today = date.today()
    age = today.year - dob.year - ((dob.month, dob.day) > (today.month, today.day))
    return age

# функция для отображения сведений о пациенте, указанных в списке
def show_patient_details(list_of_patients):
    patient_titles = ['ID пациента', 'ФИО', 'Возраст', 'Пол', 'Дата рождения (ДД-ММ-ГГГГ)',
                      'Группа крови',"Контактный номер",'Дополнительный контактный номер',
                      "ID Aadhar / ID избирателя", "Вес (кг)", "Рост (см)", "Адрес",
                      'Город',"Страна","ПИН-код","ФИО ближайших родственников",
                      'Ближайшее родственное отношение к пациенту',
                      'Контактный номер ближайшего родственника','Идентификатор электронной почты',
                      'Дата регистрации (ДД-ММ-ГГГГ)','Время регистрации (чч:мм:сс)']
    if len(list_of_patients) == 0:
        st.warning('Нет данных для отображения')
    elif len(list_of_patients) == 1:
        patient_details = [x for x in list_of_patients[0]]
        series = pd.Series(data = patient_details, index = patient_titles)
        st.write(series)
    else:
        patient_details = []
        for patient in list_of_patients:
            patient_details.append([x for x in patient])
        df = pd.DataFrame(data = patient_details, columns = patient_titles)
        st.write(df)

# класс, содержащий все поля и методы, необходимые для работы с таблицей пациентов в базе данных
class Patient:

    def __init__(self):
        self.name = str()
        self.id = str()
        self.gender = str()
        self.age = int()
        self.contact_number_1 = str()
        self.contact_number_2 = str()
        self.date_of_birth = str()
        self.blood_group = str()
        self.date_of_registration = str()
        self.time_of_registration = str()
        self.email_id = str()
        self.height = int()
        self.weight = int()
        self.next_of_kin_name = str()
        self.next_of_kin_relation_to_patient = str()
        self.next_of_kin_contact_number = str()
        self.address = str()
        self.city = str()
        self.state = str()
        self.pin_code = str()

    # метод для добавления новой записи пациента в базу данных
    def add_patient(self):
        st.write('Введите данные пациента:')
        self.name = st.text_input('ФИО')
        gender = st.radio('Пол', ['Female', 'Male', 'Other'])
        if gender == 'Other':
            gender = st.text_input('Пожалуйста, укажите')
        self.gender = gender
        dob = st.date_input('Дата рождения (ГГГГ/ММ/ДД)')
        st.info('Если нужной даты нет в календаре, введите ее в поле выше.')
        self.date_of_birth = dob.strftime('%d-%m-%Y')       # преобразует дату рождения в строку
        self.age = calculate_age(dob)
        self.blood_group = st.text_input('Группа крови')
        self.contact_number_1 = st.text_input('Контактный телефон')
        contact_number_2 = st.text_input('Дополнительный телефон (необязательно)')
        self.contact_number_2 = (lambda phone : None if phone == '' else phone)(contact_number_2)
        self.weight = st.number_input('Вес (в кг)', value = 0, min_value = 0, max_value = 400)
        self.height = st.number_input('Рост (в см)', value = 0, min_value = 0, max_value = 275)
        self.address = st.text_area('Адресс')
        self.city = st.text_input('Город')
        self.state = st.text_input('Страна')
        self.pin_code = st.text_input('PIN code')
        self.next_of_kin_name = st.text_input("Имя ближайшего родственника")
        self.next_of_kin_relation_to_patient = st.text_input("Степень родства")
        self.next_of_kin_contact_number = st.text_input("Контактный телефон ближайших родственников")
        email_id = st.text_input('Email (необезательно)')
        self.email_id = (lambda email : None if email == '' else email)(email_id)
        self.date_of_registration = datetime.now().strftime('%d-%m-%Y')
        self.time_of_registration = datetime.now().strftime('%H:%M:%S')
        self.id = generate_patient_id(self.date_of_registration,
                    self.time_of_registration)
        save = st.button('Сохранить')

        #  SQLite сохранения новой записи пациента в базе данных
        if save:
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    INSERT INTO patient_record
                    (
                        id, name, age, gender, date_of_birth, blood_group,
                        contact_number_1, contact_number_2,
                        weight, height, address, city, state, pin_code,
                        next_of_kin_name, next_of_kin_relation_to_patient,
                        next_of_kin_contact_number, email_id,
                        date_of_registration, time_of_registration
                    )
                    VALUES (
                        :id, :name, :age, :gender, :dob, :blood_group,
                        :phone_1, :phone_2, :weight, :height,
                        :address, :city, :state, :pin,
                        :kin_name, :kin_relation, :kin_phone, :email_id,
                        :reg_date, :reg_time
                    );
                    """,
                    {
                        'id': self.id, 'name': self.name, 'age': self.age,
                        'gender': self.gender, 'dob': self.date_of_birth,
                        'blood_group': self.blood_group,
                        'phone_1': self.contact_number_1,
                        'phone_2': self.contact_number_2,
                        'weight': self.weight,
                        'height': self.height, 'address': self.address,
                        'city': self.city, 'state': self.state,
                        'pin': self.pin_code, 'kin_name': self.next_of_kin_name,
                        'kin_relation': self.next_of_kin_relation_to_patient,
                        'kin_phone': self.next_of_kin_contact_number,
                        'email_id': self.email_id,
                        'reg_date': self.date_of_registration,
                        'reg_time': self.time_of_registration
                    }
                )
            st.success('Данные пациента успешно сохранены.')
            st.write('ID пациента:', self.id)
            conn.close()

    # метод для обновления существующей записи пациента в базе данных
    def update_patient(self):
        id = st.text_input('Введите ID пациента для обновления')
        if id == '':
            st.empty()
        elif not verify_patient_id(id):
            st.error('Недействительный ID пациента')
        else:
            st.success('Верный ID')
            conn, c = db.connection()

            # показывает текущие данные пациента перед обновлением
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM patient_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Tекущие данные пациента:')
                show_patient_details(c.fetchall())

            st.write('Введите новые данные пациента:')
            self.contact_number_1 = st.text_input('Номер телефона')
            contact_number_2 = st.text_input('Дополнительный номер телефона(необезательно)')
            self.contact_number_2 = (lambda phone : None if phone == '' else phone)(contact_number_2)
            self.weight = st.number_input('Вес (в кг)', value = 0, min_value = 0, max_value = 400)
            self.height = st.number_input('Рост (в см)', value = 0, min_value = 0, max_value = 275)
            self.address = st.text_area('Адресс')
            self.city = st.text_input('Город')
            self.state = st.text_input('Страна')
            self.pin_code = st.text_input('PIN code')
            self.next_of_kin_name = st.text_input("Имя ближайшего родственника")
            self.next_of_kin_relation_to_patient = st.text_input("Степень родства")
            self.next_of_kin_contact_number = st.text_input("Контактный телефон ближайших родственников")
            email_id = st.text_input('Email(необезательно)')
            self.email_id = (lambda email : None if email == '' else email)(email_id)
            update = st.button('Обновить')

            # SQLite для обновления записи этого пациента в базе данных
            if update:
                with conn:
                    c.execute(
                        """
                        SELECT date_of_birth
                        FROM patient_record
                        WHERE id = :id;
                        """,
                        { 'id': id }
                    )

                    # преобразует дату рождения в нужный формат для подсчета возраста
                    dob = [int(d) for d in c.fetchone()[0].split('-')[::-1]]
                    dob = date(dob[0], dob[1], dob[2])
                    self.age = calculate_age(dob)

                with conn:
                    c.execute(
                        """
                        UPDATE patient_record
                        SET age = :age, contact_number_1 = :phone_1,
                        contact_number_2 = :phone_2, weight = :weight,
                        height = :height, address = :address, city = :city,
                        state = :state, pin_code = :pin, next_of_kin_name = :kin_name,
                        next_of_kin_relation_to_patient = :kin_relation,
                        next_of_kin_contact_number = :kin_phone, email_id = :email_id
                        WHERE id = :id;
                        """,
                        {
                            'id': id, 'age': self.age,
                            'phone_1': self.contact_number_1,
                            'phone_2': self.contact_number_2,
                            'weight': self.weight, 'height': self.height,
                            'address': self.address, 'city': self.city,
                            'state': self.state, 'pin': self.pin_code,
                            'kin_name': self.next_of_kin_name,
                            'kin_relation': self.next_of_kin_relation_to_patient,
                            'kin_phone': self.next_of_kin_contact_number,
                            'email_id': self.email_id
                        }
                    )
                st.success('Данные пациента успешно обновлены.')
                conn.close()

    # удалить существующую запись пациента из базы данных
    def delete_patient(self):
        id = st.text_input('Введите ID пациента, которого необходимо удалить.')
        if id == '':
            st.empty()
        elif not verify_patient_id(id):
            st.error('Недействительный ID пациента')
        else:
            st.success('Верно')
            conn, c = db.connection()

            # показывает текущие данные пациента перед удалением
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM patient_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Сведения об удаляемом пациенте:')
                show_patient_details(c.fetchall())

                confirm = st.checkbox('Установите флажок, чтобы подтвердить удаление')
                if confirm:
                    delete = st.button('Удалить')

                    # SQLite для удаления записи этого пациента из базы данных
                    if delete:
                        c.execute(
                            """
                            DELETE FROM patient_record
                            WHERE id = :id;
                            """,
                            { 'id': id }
                        )
                        st.success('Данные пациента успешно удалены.')
            conn.close()

   # показать полную запись пациента
    def show_all_patients(self):
        conn, c = db.connection()
        with conn:
            c.execute(
                """
                SELECT *
                FROM patient_record;
                """
            )
            show_patient_details(c.fetchall())
        conn.close()

   # метод поиска и отображения сведений о конкретном пациенте в базе данных с использованием ID пациента
    def search_patient(self):
        id = st.text_input('Введите ID пациента для поиска.')
        if id == '':
            st.empty()
        elif not verify_patient_id(id):
            st.error('Недействительный ID пациента')
        else:
            st.success('Верно')
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM patient_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Вот сведения о пациенте, которого вы искали:')
                show_patient_details(c.fetchall())
            conn.close()
