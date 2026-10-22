"""FastAPI application for the field service backend.

This module exposes the public HTTP endpoints used by clients to manage users,
people, conversations, and training records. All state-changing routes are
protected by JWT authentication, and the login route follows the OAuth2 password
flow pattern.
"""

from typing import Annotated
from logic.db import sql
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pathlib import Path
import models
from logic import auth, crud, errors
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse





app = FastAPI(title='Field Service App API')
FRONTEND_DIR = Path(__file__).parent.parent / 'frontend'

app.mount(
    '/assets',
    StaticFiles(directory=FRONTEND_DIR / 'dist' / 'assets'),
    name='assets'
)




@app.get('/')
def homepage():
    return FileResponse(FRONTEND_DIR / 'dist' / 'index.html')

@app.get('/api/users/me', response_model=models.UserOutput)
def get_user_details(user: Annotated[models.User, Depends(auth.get_current_user)]):
    """Return the currently authenticated user's public profile.

    Args:
        user: Authenticated user resolved from the bearer token.

    Returns:
        The user's public response payload without the password hash.
    """
    return models.UserOutput(**user.model_dump())


@app.post('/api/auth/signup', response_model=models.UserOutput)
def signup(user: models.UserInput):
    """Register a new user account and return the created user summary.

    Args:
        user: Registration payload containing name, email, and password.

    Returns:
        Created user model without the password hash.
    """
    try:
        created_user = auth.signup(user)
        return models.UserOutput(**created_user.model_dump())
    except errors.AuthenticationError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Unable to create user') from e


@app.post('/api/auth/login')
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Issue a JWT access token using the OAuth2 password flow.

    This endpoint expects form fields named "username" and "password" as per the
    standard OAuth2 password flow and returns a Bearer token.

    Args:
        form_data: Username/password form payload submitted by the client.

    Returns:
        A JSON object containing the access token and token type.
    """
    try:
        return auth.login_for_access_token(form_data)
    except errors.AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid email or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Login Failed, try again later'
        ) from e


@app.post('/api/me/persons', response_model=list[models.Person])
def add_persons(
    persons: list[models.PersonInput],
    user: Annotated[models.User, Depends(auth.get_current_user)],
):
    """Create multiple person records owned by the authenticated user.

    Args:
        persons: The list of persons to persist.
        user: The authenticated user who owns the added records.

    Returns:
        The created person records.
    """
    try:
        return crud.add_persons(persons, user.id)
    except Exception as exc:
        print(exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to add persons. Try again later.',
        ) from exc


@app.get('/api/me/persons', response_model=list[models.Person])
def get_persons(
    user: Annotated[models.User, Depends(auth.get_current_user)],
    limit: int | None = None,
):
    """List all person records belonging to the authenticated user.

    Args:
        user: Authenticated user context.
        limit: Optional maximum number of rows to return.

    Returns:
        The person's list for the user.
    """
    try:
        return crud.get_persons(user.id, limit)
    except Exception as exc:
        print(exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to load persons. Try again later.',
        ) from exc


@app.patch('/api/me/persons', response_model=models.Person)
def update_person(
    person_id: int,
    person: models.PersonInput,
    user: Annotated[models.User, Depends(auth.get_current_user)],
):
    """Update one of the current user's person records.

    Args:
        person_id: The id of the person to update.
        person: The updated person data.
        user: Authenticated user used for ownership enforcement.

    Returns:
        The updated person record.
    """

    q = '''
        select user_id
        from persons 
        where id = %s
    '''
    try:
        id_of_true_user = sql(q, params = (person.id,), as_dict = False, fetch_one = True)[0]
    except TypeError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Unable to validate person ownership') 
    
    if user.id != id_of_true_user:  # person must belong to user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='This person does not exist or is not yours')

    try:
        return crud.update_person(person, person_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update person's details. Try again later.",
        ) from exc


@app.post('/api/me/conversations', response_model=models.Conversation)
def add_conversation(
    conversation: models.ConversationInput,
    user: Annotated[models.User, Depends(auth.get_current_user)],
):
    """Create a new conversation record under a person owned by the user.

    Args:
        conversation: Conversation details and its related person id.
        user: Authenticated user context.

    Returns:
        The created conversation record.
    """
    persons_for_user = crud.get_persons(user_id=user.id)
    if conversation.person_id not in [person.id for person in persons_for_user]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='The person for this conversation does not exist. Add person first')

    try:
        return crud.add_conversation(conversation)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to add conversation') from exc


@app.get('/api/me/conversations', response_model=list[models.Conversation])
def get_conversations(
    user: Annotated[models.User, Depends(auth.get_current_user)],
    limit: int | None = None,
):
    """Retrieve all conversations belonging to the authenticated user.

    Args:
        user: Authenticated user context.
        limit: Optional row limit.

    Returns:
        Conversation records associated with the user.
    """
    try:
        return crud.get_conversations(by='users', id=user.id, limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to load conversations') from exc


@app.patch('/api/me/conversations', response_model=models.Conversation)
def update_conversation(
    conversation_id: int,
    conversation: models.ConversationInput,
    user: Annotated[models.User, Depends(auth.get_current_user)],
):
    """Update an existing conversation record owned by the user.

    Args:
        conversation_id: The conversation id to update.
        conversation: The new conversation contents.
        user: Authenticated user context.

    Returns:
        The updated conversation record.
    """

    q = '''
        select user_id
        from persons
        where id = (
            select person_id
            from conversations
            where id = %s
        )

    '''
    try:
        id_of_true_user = sql(q, params = (conversation_id,), fetch_one=True)[0]
    except TypeError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Could not verify conversation ownership. Try again later' 
        )
    if id_of_true_user != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='The person for this conversation does not exist for you. Add person first'
        )

    try:
        return crud.update_conversation(conversation_id, conversation)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to update conversation') from exc


@app.delete('/api/me/conversations')
def delete_conversation(
    conversation_id: int,
    user: Annotated[models.User, Depends(auth.get_current_user)],
):
    """Delete a conversation after verifying it belongs to the authenticated user.

    Args:
        conversation_id: The conversation id to delete.
        user: Authenticated user context.

    Returns:
        A success payload when deletion succeeds.
    """
    persons_for_user = crud.get_persons(user_id=user.id)
    try:
        conversation = crud.get_conversations(by='conversations', id=conversation_id)[0]
    except TypeError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Conversation does not exist') from exc

    if conversation.person_id not in [person.id for person in persons_for_user]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='The person for this conversation does not exist. Add person first')

    try:
        crud.delete_conversation(conversation_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to delete conversation') from exc


@app.post('/api/me/students', response_model=models.Student)
def add_student(
    student: models.Student,
    user: Annotated[models.User, Depends(auth.get_current_user)],
):
    """Mark a person as a student for the authenticated user.

    Args:
        student: Student payload containing person and date information.
        user: Authenticated user context.

    Returns:
        The created student record.
    """
    persons_for_user = crud.get_persons(user_id=user.id)
    if student.person_id not in [person.id for person in persons_for_user]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='This student does not exist or is not yours')

    try:
        return crud.add_student(student)
    except errors.AlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to add student') from exc


@app.get('/api/me/students', response_model=list[models.Student])
def get_students(
    user: Annotated[models.User, Depends(auth.get_current_user)],
    limit: int | None = None,
):
    """Return all students linked to the authenticated user's persons.

    Args:
        user: Authenticated user context.
        limit: Optional row limit.

    Returns:
        Student records from the user's assigned person set.
    """
    try:
        return crud.get_students(user.id, limit)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to load students') from exc


@app.delete('/api/me/students/')
def delete_student(
    student_id: int,
    user: Annotated[models.User, Depends(auth.get_current_user)],
):
    """Delete a student entry after verifying ownership.

    Args:
        student_id: The person id mapped to the student record.
        user: Authenticated user context.

    Returns:
        Success payload on deletion.
    """
    persons_for_user = crud.get_persons(user_id=user.id)
    if student_id not in [person.id for person in persons_for_user]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='This student does not exist or is not yours')

    try:
        crud.delete_student(student_id)
        return {'success': True}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to delete student') from exc