from pydantic import BaseModel, EmailStr, Field, model_validator
import datetime as dt
from typing import Literal

#==============
#   USER
#==============
class UserBase(BaseModel):
    name: str = Field(min_length = 1, max_length = 30)
    email: EmailStr 

class LoginUser(BaseModel):
    email: EmailStr
    password: str = Field(min_length = 8, max_length = 20)

class UserInput(UserBase):
    password: str = Field(min_length = 8, max_length = 20)

class UserUpdate(BaseModel):
    name: str = Field(min_length = 1, max_length = 30, default = None)
    email: EmailStr | None = None
    password: str = Field(min_length = 8, max_length = 20, default = None)

    @model_validator(mode = 'after')
    def not_all_null(self):
        if all([
            self.name is None,
            self.email is None,
            self.password is None
        ]):
            raise ValueError('All fields cannot be Empty')
        return self
    
class UserOutput(UserBase):
    id: int

class User(UserOutput):
    password_hash: str

#================
#   PERSON
#================
class PersonInput(BaseModel):
    name: str = Field(min_length = 1, max_length = 30)
    phone: str | None = Field(min_length = 1, max_length = 15, default = None)	
    addr: str | None = Field(min_length = 1, max_length = 100, default = None)
    region: str | None = Field(min_length = 1, max_length = 30, default = None)

class Person(PersonInput):
    id: int
    user_id: int

#===================
#   CONVERSATION
#===================
class ConversationInput(BaseModel):
    date: dt.date
    topic: str = Field(max_length = 200)
    next_topic: str | None = Field(max_length = 200, default = None) 
    type: str = Literal['Initial Call', 'Following Up', 'Bible Study']
    person_id: int	

class Conversation(ConversationInput):
    id: int


#=================
#   STUDENT
#=================
class Student(BaseModel):
    person_id: int
    std_date: dt.date
    handover_date: dt.date | None = None
    handover_teacher: str | None = Field(min_length = 1, max_length = 30, default = None)