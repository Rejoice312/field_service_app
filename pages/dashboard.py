import streamlit as st 
from streamlit_local_storage import LocalStorage
import ui
from logic import calculations as calc
from ui import charts
from logic.utils import load_data
from backend.logic import errors


storage = LocalStorage()
access_token = storage.getItem('access_token')
if access_token is None:
    st.switch_page('app.py')

ui.show_logout_form()


try:
    conversations = load_data('conversations')
    students = load_data('students')
    persons = load_data('persons')
except errors.AuthenticationError:
    st.error('Login required')
    st.switch_page('app.py')
except Exception as e:
    print(e)
    st.error('Failed to load data, try again later')
    st.stop()

if persons.empty or conversations.empty:
    st.info('No data to display, make your records first')
    st.stop()

col1, col2, col3 = st.columns(3)

#=============
#   KPIs
#=============
with col1:
    st.metric(
        'Bible Studies', 
        value = calc.calc_bible_studies(conversations, by = 'month'),
        border = True
    )
with col2:
    st.metric(
        'New Conversations (This Month)',
        value = calc.calc_new_conversations(conversations, period = 'this_month'),
        border = True
    )
with col3:
    st.metric(
        'New Conversations (This Week)',
        value = calc.calc_new_conversations(conversations, period = 'this_week'),
        border = True
    )

#==========================
#   STUDIES PER STUDENT
#==========================
if not students.empty:
    st.plotly_chart(charts.student_study_freq_chart(
        conversations,
        students,
        persons,
        period = 'month'
    ))

    st.plotly_chart(charts.student_study_freq_chart(
            conversations,
            students,
            persons,
            period = 'week'
        ))


#==================================================
#   FIELD SERVICE REPORT FOR THE SERVICE YEAR
#===================================================
st.markdown('---')
st.subheader('Monthly Reports for this Service Year')
report = calc.calc_bible_studies(conversations,by = 'year')
st.dataframe(
    report,
    column_config = {
        'month': 'Month',
        'bible_studies': 'Bible Studies'
    }
)