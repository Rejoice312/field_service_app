import streamlit as st
import pandas as pd
import datetime as dt
from backend import models
from backend import api
from time import sleep
from streamlit_local_storage import LocalStorage


storage = LocalStorage()
access_token = storage.getItem('access_token')

#====================
#   CONVERSATIONS
#====================
def show_add_conversation_form(row: pd.Series):
    st.subheader(f'New conversation with {row['name']}')
    with st.form('add_conversation'):
        today = dt.date.today()
        date = st.date_input(
            'Date of conversation', 
            max_value = today,
            min_value = today - dt.timedelta(days = 360)
        )
        topic = st.text_input('Topic discussed').strip()
        next_topic = st.text_input('Next topic to be discussed').strip()
        type = st.selectbox(
            'Conversation type',
            ['Initial Call', 'Following Up', 'Bible Study']
        )
        if st.form_submit_button('Add conversation'):
            try:
                api.add_conversation(models.ConversationInput(
                    date = date,
                    topic = topic,
                    next_topic = next_topic,
                    type = type,
                    person_id = row['id']
                ), token = access_token)
                st.success('Successfully added conversation')
            except Exception as e:
                st.error(f'Failed to add coversation: {e}')
            sleep(1)
            st.rerun()


def show_delete_conversation_form(row: pd.Series):
    with st.form('delete_conversation_form'):
        confirm_deletion = st.checkbox(f'Delete selected conversation for {row['name']}?')
        if st.form_submit_button('Confirm deletion'):
            if not confirm_deletion:
                st.info('Confirm deletion first')
                return
            try:
                api.delete_conversation(row['id'], access_token)
                st.success('Deleted conversation')
            except Exception as e:
                st.error(f'Failed to delete conversation: {e}')
            sleep(1)
            st.rerun()