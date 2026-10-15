import plotly.express as px
import pandas as pd
from logic import calculations as calc
from typing import Literal


def student_study_freq_chart(
        conversations: pd.DataFrame, 
        students: pd.DataFrame,
        persons: pd.DataFrame,
        period: Literal['month', 'week']
    ):
    student_study_freq = calc.calc_student_study_freq(conversations, students, period)
    student_study_freq = student_study_freq.reset_index(name = 'freq')
    student_study_freq['name'] = student_study_freq['person_id'].map(persons.set_index('id').name)
    chart = px.bar(
        student_study_freq,
        x = 'person_id',
        y = 'freq',
        title = f'Studies Conducted per Student this {period.title()}',
        labels = {
            'person_id': 'Student',
            'freq': 'Number of Studies'
        }
    )

    chart.update_xaxes(
        tickvals = student_study_freq['person_id'],
        ticktext = student_study_freq['name'],
        tickangle = -30
    )
    chart.update_yaxes(
        dtick = 1
    )
    return chart



