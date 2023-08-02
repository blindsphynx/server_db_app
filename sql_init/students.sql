CREATE USER docker;
CREATE DATABASE docker;
GRANT ALL PRIVILEGES ON DATABASE docker TO docker;

create table if not exists students (
        id integer primary key,
        name varchar(255) NOT NULL,
        year integer,
	photo varchar(255),
	course integer,
	gruppa integer
);

insert into students(id, name, year, photo, course, gruppa)
values(1, 'Shavrina Magrarita', 2001, 'margarita.jpeg', 4, 191);

insert into students(id, name, year, photo, course, gruppa)
values(2, 'Kozlova Bella', 2001, NULL, 4, 192);

insert into students(id, name, year, photo, course, gruppa)
values(3, 'Vtorygina Delia', 2000, 'delia.jpeg', 4, 193);

insert into students(id, name, year, photo, course, gruppa)
values(4, 'Ivanov Ivan', 2002, 'ivan.jpg', 2, 211);

insert into students(id, name, year, photo, course, gruppa)
values(5, 'Petrov Petr', 2002, NULL, 3, 203);