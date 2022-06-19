import streamlit as st
from datetime import datetime, date
import database as db
import pandas as pd
import department

# функция для проверки ID врача
def verify_doctor_id(doctor_id):
    verify = False
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT id
            FROM doctor_record;
            """
        )
    for id in c.fetchall():
        if id[0] == doctor_id:
            verify = True
            break
    conn.close()
    return verify

# функция для отображения сведений о врачах, указанных в списке
def show_doctor_details(list_of_doctors):
    doctor_titles = ['ID врача', 'Имя', 'Возраст', 'Пол', 'Дата рождения (ДД-ММ-ГГГГ)',
                      'Группа крови', 'ID отдела', 'Название отделения',
                      'Контактный номер', 'Дополнительный контактный номер',
                      'Электроная почта', 'Квалификация', 'Специализация',
                      'Опыт', 'Адрес', 'Город', 'Страна', 'ПИН-код']
    if len(list_of_doctors) == 0:
        st.warning('нет данных')
    elif len(list_of_doctors) == 1:
        doctor_details = [x for x in list_of_doctors[0]]
        series = pd.Series(data = doctor_details, index = doctor_titles)
        st.write(series)
    else:
        doctor_details = []
        for doctor in list_of_doctors:
            doctor_details.append([x for x in doctor])
        df = pd.DataFrame(data = doctor_details, columns = doctor_titles)
        st.write(df)

# функция для расчета возраста по заданной дате рождения
def calculate_age(dob):
    today = date.today()
    age = today.year - dob.year - ((dob.month, dob.day) > (today.month, today.day))
    return age

# функция для создания уникального ID врача с использованием текущей даты и времени
def generate_doctor_id():
    id_1 = datetime.now().strftime('%S%M%H')
    id_2 = datetime.now().strftime('%Y%m%d')[2:]
    id = f'DR-{id_1}-{id_2}'
    return id

# функция для получения названия отделения из базы данных для заданного Id отделен
def get_department_name(dept_id):
    conn, c = db.connection()
    with conn:
        c.execute(
            """
            SELECT name
            FROM department_record
            WHERE id = :id;
            """,
            { 'id': dept_id }
        )
    return c.fetchone()[0]

# класс, содержащий все поля и методы, необходимые для работы с таблицей врачей в базе данных
class Doctor:

    def __init__(self):
        self.name = str()
        self.id = str()
        self.age = int()
        self.gender = str()
        self.date_of_birth = str()
        self.blood_group = str()
        self.department_id = str()
        self.department_name = str()
        self.contact_number_1 = str()
        self.contact_number_2 = str()
        self.email_id = str()
        self.qualification = str()
        self.specialisation = str()
        self.years_of_experience = int()
        self.address = str()
        self.city = str()
        self.state = str()
        self.pin_code = str()

    # метод для добавления новой записи врача в базу данных
    def add_doctor(self):
        st.write('Введите данные')
        self.name = st.text_input('ФИО')
        gender = st.radio('Пол', ['Female', 'Male', 'Other'])
        if gender == 'Other':
            gender = st.text_input('Выберите')
        self.gender = gender
        dob = st.date_input('Дата рождения (ГГГГ/ММ/ДД)')
        st.info('Если нужной даты нет в календаре, введите ее в поле выше.')
        self.date_of_birth = dob.strftime('%d-%m-%Y')       # преобразует дату рождения в желаемый строку
        self.age = calculate_age(dob)
        self.blood_group = st.text_input('Группа крови')
        department_id = st.text_input('ID врача')
        if department_id == '':
            st.empty()
        elif not department.verify_department_id(department_id):
            st.error('ID неверный')
        else:
            st.success('Верно')
            self.department_id = department_id
            self.department_name = get_department_name(department_id)
        self.contact_number_1 = st.text_input('Контакный номер')
        contact_number_2 = st.text_input('Дополнительный номер')
        self.contact_number_2 = (lambda phone : None if phone == '' else phone)(contact_number_2)
        self.email_id = st.text_input('Email')
        self.qualification = st.text_input('Квалификация')
        self.specialisation = st.text_input('Специализация')
        self.years_of_experience = st.number_input('Опыт', value = 0, min_value = 0, max_value = 100)
        self.address = st.text_area('Адрес')
        self.city = st.text_input('Город')
        self.state = st.text_input('Страна')
        self.pin_code = st.text_input('PIN code')
        self.id = generate_doctor_id()
        save = st.button('Сохранить')

        # SQLite для сохранения новой записи врача в базу данных
        if save:
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    INSERT INTO doctor_record
                    (
                        id, name, age, gender, date_of_birth, blood_group,
                        department_id, department_name, contact_number_1,
                        contact_number_2, email_id,
                        qualification, specialisation, years_of_experience,
                        address, city, state, pin_code
                    )
                    VALUES (
                        :id, :name, :age, :gender, :dob, :blood_group, :dept_id,
                        :dept_name, :phone_1, :phone_2, :uid, :email_id, :qualification,
                        :specialisation, :experience, :address, :city, :state, :pin
                    );
                    """,
                    {
                        'id': self.id, 'name': self.name, 'age': self.age,
                        'gender': self.gender, 'dob': self.date_of_birth,
                        'blood_group': self.blood_group,
                        'dept_id': self.department_id,
                        'dept_name': self.department_name,
                        'phone_1': self.contact_number_1,
                        'phone_2': self.contact_number_2,
                        'qualification': self.qualification,
                        'specialisation': self.specialisation,
                        'experience': self.years_of_experience,
                        'address': self.address, 'city': self.city,
                        'state': self.state, 'pin': self.pin_code
                    }
                )
            st.success('Данные успешно сохранены')
            st.write('ID доктора: ', self.id)
            conn.close()

   # обновить существующую запись врача в базе данных
    def update_doctor(self):
        id = st.text_input('Ведите ID врача')
        if id == '':
            st.empty()
        elif not verify_doctor_id(id):
            st.error('ID неверный')
        else:
            st.success('Верно')
            conn, c = db.connection()

            # показывает текущие данные врача перед обновлением
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM doctor_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Данные:')
                show_doctor_details(c.fetchall())

            st.write('Введите новые данные врача:')
            department_id = st.text_input('ID отделения')
            if department_id == '':
                st.empty()
            elif not department.verify_department_id(department_id):
                st.error('ID неверный')
            else:
                st.success('Верно')
                self.department_id = department_id
                self.department_name = get_department_name(department_id)
            self.contact_number_1 = st.text_input('Номер телефона')
            contact_number_2 = st.text_input('AДополнительный номер')
            self.contact_number_2 = (lambda phone : None if phone == '' else phone)(contact_number_2)
            self.email_id = st.text_input('Email')
            self.qualification = st.text_input('Квалификация')
            self.specialisation = st.text_input('Специальность')
            self.years_of_experience = st.number_input('Опыт', value = 0, min_value = 0, max_value = 100)
            self.address = st.text_area('Адрес')
            self.city = st.text_input('Город')
            self.state = st.text_input('Страна')
            self.pin_code = st.text_input('PIN code')
            update = st.button('Обновить')

            # SQLite для обнавления записи врача в базу данных
            if update:
                with conn:
                    c.execute(
                        """
                        SELECT date_of_birth
                        FROM doctor_record
                        WHERE id = :id;
                        """,
                        { 'id': id }
                    )

                    # преобразует дату рождения 
                    dob = [int(d) for d in c.fetchone()[0].split('-')[::-1]]
                    dob = date(dob[0], dob[1], dob[2])
                    self.age = calculate_age(dob)

                with conn:
                    c.execute(
                        """
                        UPDATE doctor_record
                        SET age = :age, department_id = :dept_id,
                        department_name = :dept_name, contact_number_1 = :phone_1,
                        contact_number_2 = :phone_2, email_id = :email_id,
                        qualification = :qualification, specialisation = :specialisation,
                        years_of_experience = :experience, address = :address,
                        city = :city, state = :state, pin_code = :pin
                        WHERE id = :id;
                        """,
                        {
                            'id': id, 'age': self.age, 'dept_id': self.department_id,
                            'dept_name': self.department_name,
                            'phone_1': self.contact_number_1,
                            'phone_2': self.contact_number_2, 'email_id': self.email_id,
                            'qualification': self.qualification,
                            'specialisation': self.specialisation,
                            'experience': self.years_of_experience,
                            'address': self.address, 'city': self.city,
                            'state': self.state, 'pin': self.pin_code
                        }
                    )
                st.success('Doctor details updated successfully.')
                conn.close()

    # удалить существующую запись врача из базы данных
    def delete_doctor(self):
        id = st.text_input('Введите ID врача')
        if id == '':
            st.empty()
        elif not verify_doctor_id(id):
            st.error('ID неврный')
        else:
            st.success('Верно')
            conn, c = db.connection()

            # показывает текущие данные врача перед удалением
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM doctor_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Данные:')
                show_doctor_details(c.fetchall())

                confirm = st.checkbox('Установите флажок, чтобы подтвердить удаление')
                if confirm:
                    delete = st.button('Удалить')

                    # SQLite для удаления записи врача в базу данных
                    if delete:
                        c.execute(
                            """
                            DELETE FROM doctor_record
                            WHERE id = :id;
                            """,
                            { 'id': id }
                        )
                        st.success('Данные врача удалены')
            conn.close()

    # показать полную запись врача
    def show_all_doctors(self):
        conn, c = db.connection()
        with conn:
            c.execute(
                """
                SELECT *
                FROM doctor_record;
                """
            )
            show_doctor_details(c.fetchall())
        conn.close()

    # поиск и отображение сведений о враче в базе данных 
    def search_doctor(self):
        id = st.text_input('Введите ID')
        if id == '':
            st.empty()
        elif not verify_doctor_id(id):
            st.error('ID неверный')
        else:
            st.success('Верно')
            conn, c = db.connection()
            with conn:
                c.execute(
                    """
                    SELECT *
                    FROM doctor_record
                    WHERE id = :id;
                    """,
                    { 'id': id }
                )
                st.write('Данные врача:')
                show_doctor_details(c.fetchall())
            conn.close()
