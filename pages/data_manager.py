import streamlit as st
from backend import api
import pandas as pd
import ui
from logic.utils import get_selected_row, load_data
from backend.logic import errors
from time import sleep
from streamlit_local_storage import LocalStorage


storage = LocalStorage()
access_token = storage.getItem('access_token')
if access_token is None:
    st.switch_page('app.py')

try:
    data = load_data()
    user = data['user']
    persons, conversations, students = data['data']
except errors.AuthenticationError as e:
    st.error(e)
    sleep(1)
    st.switch_page('app.py')
except Exception as e:
    print(f'Error: {e}')
    st.error(f'Unable to load data: {e}')
    st.stop()

person_names = persons.set_index('id')['name'] if not persons.empty else None

p_tab, c_tab, s_tab = st.tabs(
    ['Persons', 'Conversations', 'Students'],
    on_change = 'rerun'
)

#==================
#   PERSONS
#==================
with p_tab:
    if p_tab.open:
        with st.sidebar:
            with st.expander('Add new person'):
                ui.show_add_person_form()
    if persons.empty:
        st.info('You have added no persons yet')
    else:
        event = st.dataframe(
            persons,
            hide_index = True,
            selection_mode = 'single-row',
            on_select = 'rerun',
            placeholder = '',
            column_config = {
                'name': 'Name',
                'phone': 'Phone Number',
                'addr': 'Address',
                'region': 'Region',
                'user_id': None,
                'id': None
            }
        )

        selected_row = get_selected_row(event, persons)

        if p_tab.open:
            with st.sidebar:
                with st.expander('Edit selected row'):
                    if selected_row is None:
                        st.info('Select row to edit')
                    else:
                        ui.show_edit_person_form(selected_row)

                with st.expander('Add new conversation'):
                    if selected_row is None:
                        st.info('Select person conversed with')
                    else:
                        ui.show_add_conversation_form(selected_row)

                with st.expander('Add new student'):
                    if selected_row is None:
                        st.info('Select the person to make student')
                    else:
                        ui.show_add_student_form(selected_row)

                
#====================
#   CONVERSATIONS
#====================
with c_tab:
    if conversations.empty:
        st.info('You have added not conversations yet')
    else:
        conversations['name'] = conversations.person_id.map(person_names)
        event = st.dataframe(
            conversations, 
            hide_index = True,
            on_select = 'rerun',
            selection_mode = 'single-row',
            column_config = {
                'date': 'Date',
                'name': 'Person name',
                'topic': 'Topic',
                'next_topic': 'Next topic',
                'person_id': None,
                'id': None,
                'user_id': None,
            }
        )

        selected_row = get_selected_row(event, conversations)

        if c_tab.open:
            with st.sidebar:
                with st.expander('Delete conversation'):
                    if selected_row is None:
                        st.info('Select a row to delete')
                    else:
                        ui.show_delete_conversation_form(selected_row)


#=================
#   STUDENTS
#=================
with s_tab:
    if students.empty:
        st.info('You have no students yet')
    else:
        students['name'] = students.person_id.map(person_names)
        event = st.dataframe(
            students,
            hide_index = True,
            selection_mode = 'single-row',
            placeholder = '',
            on_select = 'rerun',
            column_order = ['name', 'std_date', 'handover_teacher', 'handover_date'],
            column_config = {
                'person_id': None,
                'std_date': 'Became student on',
                'handover_date': 'Handed over on',
                'handover_teacher': 'Handed over to',
                'name': 'Student name'
            }
        )

        row = get_selected_row(event, students)

        if s_tab.open:
            with st.sidebar:
                with st.expander('Delete student'):
                    if row is not None:
                        ui.show_delete_student_form(row)
