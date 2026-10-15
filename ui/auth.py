import streamlit as st
from streamlit_local_storage import LocalStorage


storage = LocalStorage()

def show_logout_form():
    with st.sidebar:
        if st.button('Logout'):
            storage.deleteItem('access_token')
            st.switch_page('app.py')