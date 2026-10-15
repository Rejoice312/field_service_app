import os
from dotenv import load_dotenv
import streamlit as st
from urllib.parse import quote_plus

DEBUG = False

if DEBUG:
    load_dotenv()
    DB_URI = os.getenv('DB_URI')
    JWT_KEY = os.getenv('JWT_KEY')
else:
    DB_PASSWORD = st.secrets['DB_PASSWORD']
    DB_URI_FORMAT = 'postgresql://postgres.wplsidnxifehdytxqoti:{password}@aws-0-eu-west-1.pooler.supabase.com:5432/postgres'
    DB_URI = DB_URI_FORMAT.format(password = quote_plus(DB_PASSWORD))
    JWT_KEY = st.secrets['JWT_KEY']


