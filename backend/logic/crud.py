from backend import models
from backend.logic.db import sql
from pwdlib import PasswordHash
from psycopg import errors as pg_errors
from backend.logic import errors
from typing import Literal

password_hasher = PasswordHash.recommended()

#=============
#   USERS
#=============
def add_user(user: models.UserInput) -> models.User:
    ''' Returns None if adding user fails, else the user'''

    password_hash = password_hasher.hash(user.password)
    query = '''
        insert into users(name, password_hash, email)
        values(%s, %s, %s)
        returning *
    '''

    try:
        user_data = sql(
            query, 
            params = (user.name, password_hash, user.email),
            fetch_one = True,
        )
        return models.User(**user_data)
    except pg_errors.UniqueViolation as e: 
        print(e)
        raise errors.AuthenticationError('User exists')


def delete_user(user_id: int) -> bool :
    query = 'delete from users where id = %s'
    sql(query, params = (user_id,))


def update_user(user: models.UserUpdate, user_id: int) -> models.User | None:
    if user.password is not None:
        password_hash = password_hasher.hash(user.password)

    query = 'update users set '
    params = []
    for field, value in user:
        if value is None:
            continue
        query += f'{field}' 
        query += ' = %s '
        params.append(value)
    query += 'where id = %s'
    params.append(user_id)
    
    sql(query, params = params, fetch_one = True)

def get_user(email: str | None = None, id: int | None = None) -> models.User | None:
    if email is not None:
        query = 'select * from users where email = %s'
        params = (email,)
    elif id is not None:
        query = 'select * from users where id = %s'
        params = (id,)
    else:
        raise ValueError('Either email or user_id is required')
    user_data = sql(query, params = params, fetch_one = True)
    if user_data is None:
        raise errors.DoesNotExistError('User does not exist')
    return models.User(**user_data)


#==============
#   PERSONS
#==============
def add_persons(persons: list[models.PersonInput], user_id: int) -> bool:
    '''Returns False if operation Fails, else True'''
    query = '''
        insert into persons(name, phone, addr, region, user_id)
        values(%(name)s, %(phone)s, %(addr)s, %(region)s, %(user_id)s)
    '''
    sql(
        query, 
        params = [
            {**person.model_dump(), 'user_id': user_id} 
            for person in persons
        ],
        execute_many = True
    )


def get_persons(user_id: int, limit: int | None = None) -> list[models.Person] | None:
    query = 'select * from persons where user_id = %s '
    params = [user_id]
    if limit is not None:
        query += 'limit %s'
        params.append(limit)
    persons = sql(query, params = params)
    return [models.Person(**person) for person in persons]


def update_person(person: models.PersonInput, person_id) -> bool:
    query = '''
        update persons
        set name = %s,
            phone = %s,
            addr = %s,
            region = %s
        where id = %s
    '''
    sql(query, params = [person.name, person.phone, person.addr, person.region, person_id])



#========================
#   CONVERSATIONS
#========================
def get_conversations(
        by: Literal['conversations', 'persons', 'users'],
        id: int,
        limit: int | None = None
    ) -> list[models.Conversation] | None:

    query = f'''
        select c.*
        from conversations c 
        left join persons p
            on c.person_id = p.id
        left join users u 
            on p.user_id = u.id
        where {by[0]}.id = %s
    '''
    conversations = sql(query, params = (id,))
    return [models.Conversation(**conversation) for conversation in conversations]


def add_conversation(conversation: models.ConversationInput) -> bool:
    query = '''
        insert into conversations(date, topic, next_topic, type, person_id)
        values(%(date)s, %(topic)s, %(next_topic)s, %(type)s, %(person_id)s)
    '''
    sql(query, params = conversation.model_dump())



def update_conversation(conversation: models.ConversationInput) -> bool:
    query = '''
        update conversations 
        set date = %(date)s,
            topic = %(topic)s,
            next_topic = %(next_topic)s,
            type = %(type)s,
            person_id = %(person_id)s
        where id = %(id)s
    '''
    sql(query, params = conversation.model_dump())
  


def delete_conversation(conversation_id: int) -> bool:
    query = 'delete from conversations where id = %s'
    sql(query, params = (conversation_id,))



#==================
#   STUDENTS
#==================
def add_student(student: models.Student) -> bool:
    query = '''
        insert into students(person_id, std_date, handover_date, handover_teacher)
        values(%(person_id)s, %(std_date)s, %(handover_date)s, %(handover_teacher)s)
    '''
    sql(query, params = student.model_dump())


def get_students(user_id: int, limit: int = None) -> list[models.Student]:
    query = '''
        select * 
        from students 
        where person_id in (
            select id
            from persons
            where user_id = %s
        )
    '''
    params = [user_id]
    if limit is not None:
        query += 'limit %s'
        params.append(limit)
    result = sql(query, params = params)
    students = [models.Student(**student_data) for student_data in result]
    return students


def delete_student(student_id: int) -> bool:
    query = 'delete from students where id = %s'
    sql(query, params = (student_id,))
