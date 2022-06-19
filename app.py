import streamlit as st
import database as db
from patient import Patient
from department import Department
from doctor import Doctor
from medical_test import Medical_Test
from prescription import Prescription
import config
import sqlite3 as sql

# функция проверки пароля


def verify_edit_mode_password():
   # edit_mode_password = st.sidebar.text_input('Введите пароль', type = 'password')
    edit_mode_password = st.sidebar.text_input(
        'Введите пароль доступа к редактированию', type='password')
    if edit_mode_password == config.edit_mode_password:
        st.sidebar.success('Верно')
        return True
    elif edit_mode_password == '':
        st.empty()
    else:
        st.sidebar.error('Пароль не верен')
        return False

# функция проверки кода доступа врача


def verify_dr_mls_access_code():
    dr_mls_access_code = st.sidebar.text_input(
        'Введите код врача', type='password')
    if dr_mls_access_code == config.dr_mls_access_code:
        st.sidebar.success('Верно')
        return True
    elif dr_mls_access_code == '':
        st.empty()
    else:
        st.sidebar.error('Не верный код')
        return False

# функция для выполнения различных операций с профилем пациента


def patients():
    st.header('Пациент')
    option_list = ['', 'Добавить пациента', 'Обновить данные пациента',
                   'Обновить данные пациента', 'Полная запись о пациенте', 'Поиск пациента']
    option = st.sidebar.selectbox('Выберете функцию', option_list)
    p = Patient()
    if (option == option_list[1] or option == option_list[2] or option == option_list[3]) and verify_edit_mode_password():
        if option == option_list[1]:
            st.subheader('Добавить пациента')
            p.add_patient()
        elif option == option_list[2]:
            st.subheader('Обновить данные пациента')
            p.update_patient()
        elif option == option_list[3]:
            st.subheader('Удалить данные пациента')
            try:
                p.delete_patient()
            # обрабатывает ошибку ограничения внешнего ключа (из-за ошибки целостности)
            except sql.IntegrityError:
                st.error(
                    'Эту запись нельзя удалить, так как она используется другими записями.')
    elif option == option_list[4]:
        st.subheader('Полная запись о пациенте')
        p.show_all_patients()
    elif option == option_list[5]:
        st.subheader('Поиск пациента')
        p.search_patient()

# функция для выполнения различных операций над профилем врача


def doctors():
    st.header('Врач')
    option_list = ['', 'Добавить врача', 'Обновить данные о враче', 'Удалить данные о враче',
                   'Полная запись о враче', 'Поиск врача']
    option = st.sidebar.selectbox('Выберете функцию', option_list)
    dr = Doctor()
    if (option == option_list[1] or option == option_list[2] or option == option_list[3]) and verify_edit_mode_password():
        if option == option_list[1]:
            st.subheader('Добавить врача')
            dr.add_doctor()
        elif option == option_list[2]:
            st.subheader('Обновить данные о враче')
            dr.update_doctor()
        elif option == option_list[3]:
            st.subheader('Удалить данные о враче')
            try:
                dr.delete_doctor()
            # обрабатывает ошибку ограничения внешнего ключа (из-за ошибки целостности)
            except sql.IntegrityError:
                st.error(
                    'Эту запись нельзя удалить, так как она используется другими записями.')
    elif option == option_list[4]:
        st.subheader('Полная запись о враче')
        dr.show_all_doctors()
    elif option == option_list[5]:
        st.subheader('Поиск врача')
        dr.search_doctor()

# функция для выполнения различных операций с рецептами


def prescriptions():
    st.header('Рецепт')
    option_list = ['', 'Добавить рецепт', 'Обновить рецепт', 'Удалить рецепт',
                   'Рецепт конкретного пациента']
    option = st.sidebar.selectbox('Выберете функцию', option_list)
    m = Prescription()
    if (option == option_list[1] or option == option_list[2] or option == option_list[3]) and verify_dr_mls_access_code():
        if option == option_list[1]:
            st.subheader('Добавить рецепт')
            m.add_prescription()
        elif option == option_list[2]:
            st.subheader('Обновить рецепт')
            m.update_prescription()
        elif option == option_list[3]:
            st.subheader('Удалить рецепт')
            m.delete_prescription()
    elif option == option_list[4]:
        st.subheader('Рецепт конкретного пациента')
        m.prescriptions_by_patient()

# функция для выполнения различных операций над анализами


def medical_test():
    st.header('Анализы')
    option_list = ['', 'Добавить анализ', 'Обнавить анализ', 'Удалить анализ',
                   'Анализы конкретного пациента']
    option = st.sidebar.selectbox('Веберите функцию', option_list)
    t = Medical_Test()
    if (option == option_list[1] or option == option_list[2] or option == option_list[
            3]) and verify_dr_mls_access_code():
        if option == option_list[1]:
            st.subheader('Добавить анализ')
            t.add_medical_test()
        elif option == option_list[2]:
            st.subheader('Обнавить анализ')
            t.update_medical_test()
        elif option == option_list[3]:
            st.subheader('Удалить анализ')
            t.delete_medical_test()
    elif option == option_list[4]:
        st.subheader('Анализы конкретного пациента')
        t.medical_tests_by_patient()

# функция для выполнения различных операций модуля отделения


def departments():
    st.header('Отделение')
    option_list = ['', 'Добавить отделени', 'Обновить отделение', 'Удалить отделение', 'Вся информация об отделении',
                   'Поиск отделения', 'Врачи отделения']
    option = st.sidebar.selectbox('Выберете функцию', option_list)
    d = Department()
    if (option == option_list[1] or option == option_list[2] or option == option_list[3]) and verify_edit_mode_password():
        if option == option_list[1]:
            st.subheader('Добавить отделение')
            d.add_department()
        elif option == option_list[2]:
            st.subheader('Обновить отделение')
            d.update_department()
        elif option == option_list[3]:
            st.subheader('Удалить отделение')
            try:
                d.delete_department()
            # обрабатывает ошибку ограничения внешнего ключа (из-за ошибки целостности)
            except sql.IntegrityError:
                st.error(
                    'Эту запись нельзя удалить, так как она используется другими записями.')
    elif option == option_list[4]:
        st.subheader('Вся информация об отделении')
        d.show_all_departments()
    elif option == option_list[5]:
        st.subheader('Поиск отделения')
        d.search_department()
    elif option == option_list[6]:
        st.subheader('Врачи отделения')
        d.list_dept_doctors()

# функция открытия главного меню при успешной аутентификации пользователя


def home():
    db.db_init()        # устанавливает соединение с базой данных и создает таблицы
    option = st.sidebar.selectbox(
        'Выберите модуль', ['', 'Пациент', 'Врач', 'Рецепт', 'Анализ', 'Отделение'])
    if option == 'Пациент':
        patients()
    elif option == 'Врач':
        doctors()
    elif option == 'Анализ':
        medical_test()
    elif option == 'Рецепт':
        prescriptions()
    elif option == 'Отделение':
        departments()


st.title('Коробочка')
# аутентификация пользователя по паролю
password = st.sidebar.text_input('Введите пароль', type='password')
if password == config.password:
    st.sidebar.success('Верно')
    home()
elif password == '':
    st.empty()
else:
    st.sidebar.error('Неправильный пароль')
