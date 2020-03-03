import os

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


# ORM Classes
class Person(Model):
    class Meta:
        database = db
        table_name = settings.PERSON_TABLE + ('_TEST' if os.environ.get('TEST') else '')

    first_name = TextField(column_name='first_name')
    last_name = TextField(column_name='last_name')
    partner = ForeignKeyField('self', null=True, backref='partners', column_name='partner')


class Pet(Model):
    class Meta:
        database = db
        table_name = settings.PET_TABLE + ('_TEST' if os.environ.get('TEST') else '')

    name = TextField(column_name='name')
    owner = ForeignKeyField(Person, null=True, backref='pets', column_name='owner')


# Custom Exceptions
class ConflictException(Exception):
    pass


class NotFoundException(Exception):
    pass


class InvalidRequestException(Exception):
    pass


class InternalServerErrorException(Exception):
    pass
