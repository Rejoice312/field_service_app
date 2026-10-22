"""Database access layer for users, persons, conversations, and students.

This module contains the persistence logic that sits between API routes and the
PostgreSQL database. Each function is responsible for a single repository-style
operation such as creating, updating, deleting, or retrieving a model instance.
"""

from typing import Literal

from pwdlib import PasswordHash
from psycopg import errors as pg_errors

import models
from logic import errors
from logic.db import sql

password_hasher = PasswordHash.recommended()


#======================
#   USERS
#======================
def add_user(user: models.UserInput) -> models.User:
    """Create a new user record with a securely hashed password.

    Args:
        user: Registration payload containing the name, email, and plain text password.

    Returns:
        The saved user record.

    Raises:
        AuthenticationError: If a user with the same email already exists.
    """
    password_hash = password_hasher.hash(user.password)
    query = '''
        insert into users(name, password_hash, email)
        values(%s, %s, %s)
        returning *
    '''

    try:
        user_data = sql(
            query,
            params=(user.name, password_hash, user.email),
            fetch_one=True,
        )
        return models.User(**user_data)
    except pg_errors.UniqueViolation as exc:
        raise errors.AuthenticationError('User exists') from exc


def delete_user(user_id: int) -> bool:
    """Delete a user by their database id.

    Args:
        user_id: The id of the user to remove.
    """
    query = 'delete from users where id = %s'
    sql(query, params=(user_id,))


def update_user(user: models.UserUpdate, user_id: int) -> models.User | None:
    """Update one or more user fields while preserving password hashing rules.

    Args:
        user: A partial user update payload.
        user_id: The target user id.

    Returns:
        The updated user record.
    """
    fields = []
    params = []

    for field, value in user.model_dump().items():
        if value is None:
            continue
        if field == 'password':
            value = password_hasher.hash(value)
        fields.append(f'{field} = %s')
        params.append(value)

    if not fields:
        raise ValueError('At least one field is required to update')

    query = 'update users set ' + ', '.join(fields) + ' where id = %s'
    params.append(user_id)
    sql(query, params=params, fetch_one=True)
    return get_user(id=user_id)


def get_user(email: str | None = None, id: int | None = None) -> models.User | None:
    """Fetch a user record by either email or id.

    Args:
        email: Optional email lookup.
        id: Optional numeric user id.

    Returns:
        The matching user record.

    Raises:
        ValueError: If neither identifier is supplied.
        DoesNotExistError: If no user matches the supplied criteria.
    """
    if email is not None:
        query = 'select * from users where email = %s'
        params = (email,)
    elif id is not None:
        query = 'select * from users where id = %s'
        params = (id,)
    else:
        raise ValueError('Either email or user_id is required')

    user_data = sql(query, params=params, fetch_one=True)
    if user_data is None:
        raise errors.DoesNotExistError('User does not exist')
    return models.User(**user_data)


#========================
#   PERSONS
#========================
def add_persons(persons: list[models.PersonInput], user_id: int) -> list[models.Person]:
    """Insert one or more person records for a specific user.

    Args:
        persons: Person payloads to store.
        user_id: The logged-in user who owns the records.

    Returns:
        A list of created person records.
    """
    query = '''
        insert into persons(name, phone, addr, region, user_id)
        values(%(name)s, %(phone)s, %(addr)s, %(region)s, %(user_id)s)
        returning *
    '''
    created_rows = []
    for person in persons:
        row = sql(query, params={**person.model_dump(), 'user_id': user_id}, fetch_one=True)
        created_rows.append(models.Person(**row))
    return created_rows


def get_persons(user_id: int, limit: int | None = None) -> list[models.Person] | None:
    """Return all persons associated with a user, optionally limited.

    Args:
        user_id: The owning user id.
        limit: Maximum number of rows to return.

    Returns:
        A list of person records for the user.
    """
    query = 'select * from persons where user_id = %s '
    params = [user_id]
    if limit is not None:
        query += 'limit %s'
        params.append(limit)
    persons = sql(query, params=params)
    return [models.Person(**person) for person in persons]


def update_person(person: models.PersonInput, person_id) -> models.Person:
    """Update an existing person record and return the new version.

    Args:
        person: Updated person payload.
        person_id: Identifying id of the person record.

    Returns:
        The updated person model.
    """
    query = '''
        update persons
        set name = %s,
            phone = %s,
            addr = %s,
            region = %s
        where id = %s
        returning *
    '''
    updated = sql(query, params=[person.name, person.phone, person.addr, person.region, person_id], fetch_one=True)
    return models.Person(**updated)


#========================
#   CONVERSATIONS
#========================
def get_conversations(
    by: Literal['conversations', 'persons', 'users'],
    id: int,
    limit: int | None = None,
) -> list[models.Conversation] | None:
    """Fetch conversations by parent entity type and id.

    Args:
        by: The relationship type to use: conversation, person, or user.
        id: The id of the parent record.
        limit: Optional maximum row count.

    Returns:
        Matching conversation records.
    """
    aliases = {
        'conversations': 'c',
        'persons': 'p',
        'users': 'u',
    }
    alias = aliases[by]
    query = f'''
        select c.*
        from conversations c
        left join persons p on c.person_id = p.id
        left join users u on p.user_id = u.id
        where {alias}.id = %s
    '''
    params = [id]
    if limit is not None:
        query += ' limit %s'
        params.append(limit)
    conversations = sql(query, params=params)
    return [models.Conversation(**conversation) for conversation in conversations]


def add_conversation(conversation: models.ConversationInput) -> models.Conversation:
    """Insert a conversation record for a person.

    Args:
        conversation: Conversation payload to save.

    Returns:
        The freshly created conversation record.
    """
    query = '''
        insert into conversations(date, topic, next_topic, type, person_id)
        values(%(date)s, %(topic)s, %(next_topic)s, %(type)s, %(person_id)s)
        returning *
    '''
    row = sql(query, params=conversation.model_dump(), fetch_one=True)
    return models.Conversation(**row)


def update_conversation(conversation_id: int, conversation: models.ConversationInput) -> models.Conversation:
    """Update a conversation while keeping the record identity fixed.

    Args:
        conversation_id: Conversation row id.
        conversation: Updated conversation payload.

    Returns:
        The updated conversation model.
    """
    query = '''
        update conversations
        set date = %(date)s,
            topic = %(topic)s,
            next_topic = %(next_topic)s,
            type = %(type)s,
            person_id = %(person_id)s
        where id = %(id)s
        returning *
    '''
    payload = conversation.model_dump()
    payload['id'] = conversation_id
    row = sql(query, params=payload, fetch_one=True)
    return models.Conversation(**row)


def delete_conversation(conversation_id: int) -> bool:
    """Delete a conversation by id.

    Args:
        conversation_id: Conversation row id to remove.
    """
    query = 'delete from conversations where id = %s'
    sql(query, params=(conversation_id,))


#==================
#   STUDENTS
#==================
def add_student(student: models.Student) -> models.Student:
    """Add a person to the students table.

    Args:
        student: Student payload containing the person relationship and dates.

    Returns:
        The created student record.

    Raises:
        AlreadyExistsError: If the person is already marked as a student.
    """
    query = '''
        insert into students(person_id, std_date, handover_date, handover_teacher)
        values(%(person_id)s, %(std_date)s, %(handover_date)s, %(handover_teacher)s)
        returning *
    '''
    try:
        row = sql(query, params=student.model_dump(), fetch_one=True)
        return models.Student(**row)
    except pg_errors.UniqueViolation as exc:
        raise errors.AlreadyExistsError('This person is already a student') from exc


def get_students(user_id: int, limit: int = None) -> list[models.Student]:
    """Fetch all students for a user, optionally limited by a row count.

    Args:
        user_id: The user owning the associated persons.
        limit: Maximum number of students to return.

    Returns:
        A list of student records for the user.
    """
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
        query += ' limit %s'
        params.append(limit)
    result = sql(query, params=params)
    students = [models.Student(**student_data) for student_data in result]
    return students


def delete_student(student_id: int) -> bool:
    """Remove a student entry based on the associated person id.

    Args:
        student_id: The person id that serves as the student key.
    """
    query = 'delete from students where person_id = %s'
    sql(query, params=(student_id,))
