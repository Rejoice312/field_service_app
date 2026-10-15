import pandas as pd
from backend import api
from streamlit_local_storage import LocalStorage



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
def load_data():
    user = api.get_user_details(token = access_token)
    persons = api.get_persons(token = access_token)
    conversations = api.get_conversations(by = 'users', id = user.id)
    students = api.get_students(token = access_token)

    return {
        'user': user,
        'data': [
            pd.DataFrame([data.model_dump() for data in model_object])
            for model_object in (persons, conversations, students)
        ]
    }
