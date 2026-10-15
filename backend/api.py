from backend.logic import crud, auth, errors
from backend import models
from typing import Literal

#==============
#   USERS
#==============

def get_user_details(token: str) -> models.User | None:
    user = auth.get_current_user(token)
    return models.UserOutput(**user.model_dump())


#================
#   PERSONS
#================

def add_persons(persons: list[models.PersonInput], token: str = None) -> bool:
    user = auth.get_current_user(token)
    return crud.add_persons(persons, user.id)

def get_persons(limit: int | None = None, token: str = None) -> list[models.Person] | None:
    user = auth.get_current_user(token)
    return crud.get_persons(user.id, limit)

def update_person(person: models.PersonInput, person_id: int, token: str = None) -> bool:
    user = auth.get_current_user(token)
    persons_for_user = crud.get_persons(user_id = user.id)
    if person_id not in [person.id for person in persons_for_user]:
        raise errors.DoesNotExistError('This person does not exist')
    return crud.update_person(person, person_id)


#================
#   CONVERSATIONS
#================

def add_conversation(conversation: models.ConversationInput, token: str = None) -> bool:
    user = auth.get_current_user(token)
    # verify the person_id of conversation belongs to user
    persons_for_user = crud.get_persons(user_id = user.id)
    if conversation.person_id not in [person.id for person in persons_for_user]:
        raise errors.DoesNotExistError('The person for this conversation does not exist. Add person first')
    return crud.add_conversation(conversation)

def get_conversations(by: Literal['conversations', 'persons', 'users'], id: int, limit: int | None = None) -> list[models.Conversation] | None:
    return crud.get_conversations(by = by, id = id, limit = limit)

def update_conversation(conversation: models.ConversationInput, token: str = None) -> bool:
    user = auth.get_current_user(token)
    # verify conversation belongs to the user
    persons_for_user = crud.get_persons(user_id = user.id)
    if conversation.person_id not in [person.id for person in persons_for_user]:
        raise errors.DoesNotExistError('The person for this conversation does not exist. Add person first')
    return crud.update_conversation(conversation)

def delete_conversation(conversation_id: int, token: str = None) -> bool:
    user = auth.get_current_user(token)
    # verify conversation belongs to the user
    persons_for_user = crud.get_persons(user_id = user.id)
    try:
        conversation = crud.get_conversations(by = 'conversations', id = conversation_id)[0]
    except IndexError:
        raise Exception('Conversation does not exist')
    if conversation.person_id not in [person.id for person in persons_for_user]:
        raise errors.DoesNotExistError('The person for this conversation does not exist. Add person first')

    return crud.delete_conversation(conversation_id)

#================
#   STUDENTS
#================
def add_student(student: models.Student, token: str = None) -> bool:
    user = auth.get_current_user(token)
    # verify student belongs to user
    persons_for_user = crud.get_persons(user_id = user.id)
    if not student.person_id in [person.id for person in persons_for_user]:
        raise Exception('This student does not exist or is not yours')
    return crud.add_student(student)

def get_students(limit: int | None = None, token: str = None) -> list[models.Student]:
    user = auth.get_current_user(token)
    return crud.get_students(user.id, limit)

def delete_student(student_id: int, token: str = None) -> bool:
    user = auth.get_current_user(token)
    # verify student belongs to user
    persons_for_user = crud.get_persons(user_id = user.id)
    if not student_id in [person.id for person in persons_for_user]:
        raise Exception('This student does not exist or is not yours')
    return crud.delete_student(student_id)


#=======================
#   AUTHENTICATION
#=======================
def signup(user: models.UserInput) -> str | None:
    return auth.signup(user)

def login(user: models.LoginUser) -> str | None:
    return auth.login(user)