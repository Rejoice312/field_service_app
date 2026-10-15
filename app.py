import streamlit as st
from backend import api
from backend import models
from streamlit_local_storage import LocalStorage
from backend.logic import errors


storage = LocalStorage()
access_token = storage.getItem('access_token')
if access_token is not None:
    st.switch_page('pages/dashboard.py')

login_tab, signup_tab = st.tabs(['Log in', 'Sign up'], on_change = 'rerun')

#==============
#   LOGIN
#==============
with login_tab:
    with st.form('login_form'):
        email = st.text_input('Email address', type = 'email').strip().lower()
        password = st.text_input('Password', type = 'password').strip()
        display = st.empty()

        if st.form_submit_button('Log in'):
            try:
                access_token = api.login(models.LoginUser(
                    email = email,
                    password = password
                ))
            except (errors.AuthenticationError, errors.DoesNotExistError) as e:
                display.error(e)
                st.stop()
            except Exception as e:
                display.error('Failed to login, check your internet')
                st.stop()

            # save token and switch page
            storage.setItem('access_token', access_token)
            display.info('Logging in...')
            st.switch_page('pages/dashboard.py')


#====================
#   SIGN UP
#====================
with signup_tab:
    with st.form('signup_Form'):
        email = st.text_input('Email address', type = 'email').strip().lower()
        name = st.text_input('Full name').strip().title()
        password = st.text_input('Password', type = 'password').strip()
        confirm_password = st.text_input('Confirm password', type = 'password').strip()
        display = st.empty()

        if st.form_submit_button('Sign up'):
            if password != confirm_password:
                display.error('Passwords do not match')
                st.stop()
            try:
                access_token = api.signup(models.UserInput(
                    email = email,
                    name = name,
                    password = password
                ))
            except errors.AuthenticationError as e:
                display.error(e)
                st.stop()
            except Exception as e:
                print(e)
                display.error('Failed to signup. Check your internet connection')
                st.stop()

            # save token and switch page
            storage.setItem('access_token', access_token)
            st.switch_page('pages/dashboard.py')
            
