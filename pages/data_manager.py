import streamlit as st
import ui
from logic.utils import get_selected_row, load_data
from backend.logic import errors
from time import sleep
from streamlit_local_storage import LocalStorage


storage = LocalStorage()
access_token = storage.getItem('access_token')
if access_token is None:
    st.switch_page('app.py')

ui.show_logout_form()

p_tab, c_tab, s_tab = st.tabs(
    ['Persons', 'Conversations', 'Students'],
    on_change = 'rerun'
)

#==================
#   PERSONS
#==================
try:
    persons = load_data(table = 'persons')
except errors.AuthenticationError:
    st.error('Login required')
    sleep(1)
    st.switch_page('app.py')
except Exception as e:
    print(e)
    st.error('Failed to load data, try again')
    st.stop()

person_names = persons.set_index('id')['name'] if not persons.empty else None
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
                'id': 'Person ID'
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
    if c_tab.open:
        try:
            conversations = load_data(table = 'conversations')
        except errors.AuthenticationError:
            st.error('Login required')
            sleep(1)
            st.switch_page('app.py')
        except Exception as e:
            print(e)
            st.error('Failed to load data, try again')
            st.stop()
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
                    'id': None,
                    'user_id': None,
                    'person_id': 'Person ID',
                    'type': 'Conversation type'
                },
                column_order = [
                    'date', 'name', 
                    'topic', 'next_topic',
                    'type', 'person_id'
                ]
            )

            selected_row = get_selected_row(event, conversations)

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
    if s_tab.open:
        try:
            students = load_data(table = 'students')
        except errors.AuthenticationError:
            st.error('Login required')
            sleep(1)
            st.switch_page('app.py')
        except Exception as e:
            st.error('Failed to load data, try again.')
            st.stop()

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
                    'person_id': 'Person ID',
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
