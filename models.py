from peewee import ForeignKeyField
from peewee import Model
from peewee import PostgresqlDatabase
from peewee import TextField

import settings

db = PostgresqlDatabase(
    settings.DATABASE['db_name'],
    user=settings.DATABASE['user'],
    password=settings.DATABASE['password'],
    host=settings.DATABASE['host'],
    port=settings.DATABASE['port'],
    autorollback=settings.DATABASE['autorollback']
)


# Custom Exception
class NotFoundException(Exception):
    pass


class InvalidRequestException(Exception):
    pass


class InternalServerErrorException(Exception):
    pass


# ORM Classes
class Person(Model):
    class Meta:
        database = db
        table_name = settings.PERSON_TABLE

    first_name = TextField(column_name='first_name')
    last_name = TextField(column_name='last_name')
    partner = ForeignKeyField('self', null=True, backref='partners', column_name='partner')


class Pet(Model):
    class Meta:
        database = db
        table_name = settings.PET_TABLE

    name = TextField(column_name='name')
    owner = ForeignKeyField(Person, null=True, backref='pets', column_name='owner')
