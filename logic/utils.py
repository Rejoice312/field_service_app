import pandas as pd
from backend import api
from streamlit_local_storage import LocalStorage
from streamlit import cache_data
from typing import Literal



storage = LocalStorage()
access_token = storage.getItem('access_token')
#=============
#   UTILS
#=============  
def get_selected_row(event, df: pd.DataFrame) -> pd.Series | None:
    try:
        selected_row_index= event.selection.rows[0] 
        selected_row = df.iloc[selected_row_index]
    except IndexError:
        selected_row = None
    return selected_row


# Data loading
@cache_data
def load_data(table: Literal['persons', 'conversations', 'students']) -> pd.DataFrame:
    if table == 'persons':
        result = api.get_persons(token = access_token)
    elif table == 'conversations':
        result = api.get_conversations(token = access_token)
    elif table == 'students':
        result = api.get_students(token = access_token)

    return pd.DataFrame([result_item.model_dump() for result_item in result])
