"""Pydantic data models for the field service application.

These schemas define the request and response contracts used throughout the API.
They are also used for validation when records are created or changed in the
backend.
"""

import datetime as dt
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, model_validator


#==============
#   USER
#==============
class UserBase(BaseModel):
    """Common fields shared by user request and response models."""

    name: str = Field(min_length=1, max_length=30)
    email: EmailStr


class LoginUser(BaseModel):
    """Credentials submitted during the login password-flow request."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=20)


class UserInput(UserBase):
    """User creation payload including a plain-text password."""

    password: str = Field(min_length=8, max_length=20)


class UserUpdate(BaseModel):
    """Partial update payload for an existing user account."""

    name: str = Field(min_length=1, max_length=30, default=None)
    email: EmailStr | None = None
    password: str = Field(min_length=8, max_length=20, default=None)

    @model_validator(mode='after')
    def not_all_null(self):
        """Ensure that an update request does not send an empty payload."""
        if all([
            self.name is None,
            self.email is None,
            self.password is None,
        ]):
            raise ValueError('All fields cannot be Empty')
        return self


class UserOutput(UserBase):
    """Publicly safe user response including database id."""

    id: int


class User(UserOutput):
    """Internal representation of a persisted user, including the hashed password."""

    password_hash: str


#================
#   PERSON
#================
class PersonInput(BaseModel):
    """Minimal fields required to create or update a person record."""

    name: str = Field(min_length=1, max_length=30)
    phone: str | None = Field(min_length=1, max_length=15, default=None)
    addr: str | None = Field(min_length=1, max_length=100, default=None)
    region: str | None = Field(min_length=1, max_length=30, default=None)


class Person(PersonInput):
    """Person record as stored in the database, including ownership metadata."""

    id: int
    user_id: int


#===================
#   CONVERSATION
#===================
class ConversationInput(BaseModel):
    """Payload used when creating or editing a conversation record."""

    date: dt.date
    topic: str = Field(max_length=200)
    next_topic: str | None = Field(max_length=200, default=None)
    type: Literal['Initial Call', 'Following Up', 'Bible Study']
    person_id: int


class Conversation(ConversationInput):
    """Conversation row returned from the database with a generated id."""

    id: int


#=================
#   STUDENT
#=================
class Student(BaseModel):
    """Represents a person who has become a student in the field service process."""

    person_id: int
    std_date: dt.date
    handover_date: dt.date | None = None
    handover_teacher: str | None = Field(min_length=1, max_length=30, default=None)