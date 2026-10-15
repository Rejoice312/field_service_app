import streamlit as st 
from streamlit_local_storage import LocalStorage

storage = LocalStorage()
access_token = storage.getItem('access_token')
if access_token is None:
    st.switch_page('app.py')

with st.sidebar:
    if st.button('Logout'):
        storage.deleteItem('access_token')
        st.switch_page('app.py')