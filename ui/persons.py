import streamlit as st
from backend import models
from backend import api
import pandas as pd
from time import sleep
from streamlit_local_storage import LocalStorage



storage = LocalStorage()
access_token = storage.getItem('access_token')

#====================
#   PERSONS
#====================

def show_add_person_form():
    with st.form('add_person_form'):
        name = st.text_input('Name').title().strip()
        phone = st.text_input('Phone number', type = 'phone').strip()
        addr = st.text_input('Address').strip()
        region = st.text_input('Region')

        if st.form_submit_button('Add person'):
            print('submitted')
            person = models.PersonInput(
                name = name,
                phone = phone,
                addr = addr,
                region = region
            )
            try:
                api.add_persons([person], access_token)
                st.info('Successfully added new person')
            except Exception as e:
                st.error(f'Failed to add {e}')
            sleep(1)
            st.rerun()

def show_edit_person_form(row: pd.Series):
    with st.form('edit_person_form'):
        name = st.text_input('Name', value = row['name'])
        phone = st.text_input('Phone', type = 'phone', value = row['phone'])
        addr = st.text_input('Address', value = row['addr'])
        region = st.text_input('Region', value = row['region'])

        if st.form_submit_button('Save Changes'):
            try:
                api.update_person(models.PersonInput(
                    name = name,
                    phone = phone,
                    addr = addr,
                    region = region,
                ), person_id = row['id'], token = access_token)
                st.success('Changes saved')
            except Exception as e:
                print(e)
                st.error(f'Failed to save changes')
            sleep(1)
            st.rerun()

