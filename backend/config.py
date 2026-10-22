"""Application configuration and environment setup for the Field Service backend.

This module centralizes the database connection string and JWT signing key.
It supports local development by loading values from a .env file and a Streamlit
production fallback via secrets.
"""

import os
from urllib.parse import quote_plus
from dotenv import load_dotenv


DEBUG = False

# Local development loads environment variables from a .env file. When DEBUG is
# false, the app expects values to be available in the Streamlit secrets manager.
if DEBUG:
    JWT_KEY = '98RN29203NUnm983NB2Rp89nRMpn39RMI098n8nm3ru90rn2r83R9983nrN83R29NR932F32Hf23hfbbbb3FFF8o2no73fffONNNNNN7FY7Y88RN932FFFFF8F23NNNNN832N9F3F8M2982M938UN29FN32'
    DB_URI = 'postgresql://rejoice:jowayo@localhost:5432/field_service_app'
else:
    # This is kept for Streamlit-hosted deployment, where secrets are injected into
    # the app environment rather than reading a local .env file.
    load_dotenv()
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_URI_FORMAT = 'postgresql://postgres.wplsidnxifehdytxqoti:{password}@aws-0-eu-west-1.pooler.supabase.com:5432/postgres'
    DB_URI = DB_URI_FORMAT.format(password=quote_plus(DB_PASSWORD))
    JWT_KEY = os.getenv('JWT_KEY')



