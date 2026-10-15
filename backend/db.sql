-- drop existing tables
drop table if exists field_sessions;
drop table if exists students;
drop table if exists conversations;
drop table if exists persons;
drop table if exists users;


create table users(
    id serial primary key,
    name varchar(30) not null,
    password_hash text not null,
    email varchar(100) not null unique
);

-- persons conversed with
create table persons(
    id	serial primary key, 
    name varchar(30) not null,
    phone varchar(15), 	
    addr varchar(100),
    region	varchar(30),
    user_id integer not null references users(id)
        on delete cascade
);

-- conversations held
create table conversations(
    id serial primary key,
    date date not null,	
    topic varchar(200) not null,
    next_topic	varchar(200) not null,
    type varchar(15) check(type in ('Initial Call', 'Following Up', 'Bible Study')),
    person_id integer not null references persons(id)
        on delete cascade
);

-- persons that became students
create table students(
    person_id integer primary key references persons(id)
        on delete cascade,	
    std_date date not null,	
    handover_date date,	
    handover_teacher varchar(30)
);

-- For field service sessions 
create table field_sessions(
    id serial primary key,
    date date not null,
    start time not null,
    stop time,
    user_id integer not null references users(id) 
        on delete cascade
);