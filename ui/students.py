import pandas as pd
from backend import api
from backend import models
import streamlit as st
import datetime as dt
from time import sleep
from streamlit_local_storage import LocalStorage



storage = LocalStorage()
access_token = storage.getItem('access_token')
#==================
#   STUDENTS
#==================
def show_add_student_form(row: pd.Series):
    with st.form('add_student_form'):
        std_date = st.date_input(
            'Date of being a student', 
            max_value = dt.date.today()
        )
        if st.form_submit_button('Add as student'):
            try:
                api.add_student(models.Student(
                    person_id = row['id'],
                    std_date = std_date
                ), token = access_token)
                st.success('Added student successfully')
            except Exception as e:
                st.error(f'Failed to add as student: {e}')        
            sleep(1)
            st.rerun()


def show_delete_student_form(row: pd.Series):
    with st.form('delete_student_form'):
        confirm_deletion = st.checkbox(f'Delete {row['name']} as student?')
        if st.form_submit_button('Confirm'):
            if not confirm_deletion:
                st.error('Confirm deletion first')
                st.stop()
            try:
                api.delete_student(row['person_id'], access_token)
                st.success('Deleted student successfully')
            except Exception as e:
                st.error(f'Failed to delete student: {e}')
            sleep(1)
            st.rerun()
            