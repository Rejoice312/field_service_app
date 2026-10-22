"""Application configuration and environment setup for the Field Service backend.

This module centralizes the database connection string and JWT signing key.
It supports local development by loading values from a .env file and a Streamlit
production fallback via secrets.
"""

import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
import streamlit as st

DEBUG = False

# Local development loads environment variables from a .env file. When DEBUG is
# false, the app expects values to be available in the Streamlit secrets manager.
if DEBUG:
    load_dotenv()
    DB_URI = os.getenv('DB_URI')
    JWT_KEY = os.getenv('JWT_KEY')
else:
    # This is kept for Streamlit-hosted deployment, where secrets are injected into
    # the app environment rather than reading a local .env file.
    DB_PASSWORD = st.secrets['DB_PASSWORD']
    DB_URI_FORMAT = 'postgresql://postgres.wplsidnxifehdytxqoti:{password}@aws-0-eu-west-1.pooler.supabase.com:5432/postgres'
    DB_URI = DB_URI_FORMAT.format(password=quote_plus(DB_PASSWORD))
    JWT_KEY = st.secrets['JWT_KEY']



