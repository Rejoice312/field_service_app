import pandas as pd
from typing import Literal

def calc_bible_studies(conversations: pd.DataFrame, by = Literal['month', 'year']) -> int | pd.DataFrame:
    '''
    Calculates the number of bible studies in the current month or service year
    Args:
        conversations: a pandas.DataFrame object of conversations
        by: determins if the calcualtion is for the current month or service year
    Return:
        an integer number of bible studies conducted during the month or a pd.Series 
        object of bible studies for each month of the service year (Sep - Aug)
    ''' 
    conversations['date'] = pd.to_datetime(conversations.date)
    if by == 'month':
        this_month = pd.Timestamp.now().to_period('M')
        this_month_conv = conversations[conversations.date.dt.to_period('M') == this_month]
        return this_month_conv.person_id.nunique()
    elif by == 'year':
        this_year = pd.Timestamp.now().to_period('Y-AUG')
        is_within_this_year = (this_year.start_time <= conversations.date) & (conversations.date <= this_year.end_time)
        this_year_conv = conversations[is_within_this_year]
        report = this_year_conv.groupby(pd.Grouper(key = 'date', freq = 'ME')).person_id.nunique()
        report = report.to_frame(name = 'bible_studies')
        report.index = report.index.to_period(freq = 'M')
        report.index.name = 'month'
        return report


def calc_student_study_freq(conversations: pd.DataFrame, students: pd.Series, period: Literal['month', 'week']) -> pd.Series:
    '''
    Calculates visit frequency for each student for the current month or week
    '''
    conversations['date'] = pd.to_datetime(conversations.date)
    if period == 'month':
        freq = 'M'
    elif period == 'week':
        freq = 'W'

    this_period = pd.Timestamp.now().to_period(freq = freq)
    this_period_conv = conversations[conversations.date.dt.to_period(freq = freq) == this_period]
    is_student = this_period_conv.person_id.isin(students.person_id)
    is_a_study = this_period_conv['type'].str.lower() == 'bible study'
    this_period_studies = this_period_conv[is_student & is_a_study]
    this_period_studies_freq = this_period_studies.groupby('person_id').size()
    return this_period_studies_freq

def calc_new_conversations(conversations: pd.DataFrame, period = Literal['this_month', 'this_week']) -> int:
    conversations['date'] = pd.to_datetime(conversations.date)
    if period == 'this_month':
        this_period = pd.Timestamp.now().to_period('M')
    elif period == 'this_week':
        this_period = pd.Timestamp.now().to_period('W')

    is_within_period = (this_period.start_time <= conversations.date) & (conversations.date <= this_period.end_time)
    conversations = conversations[is_within_period]
    new_conversations = conversations[conversations['type'].str.lower() == 'initial call'].shape[0]
    return new_conversations
