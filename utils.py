from models import db, Person, Pet


def _create_tables():
    with db:
        db.create_tables([
            Person,
            Pet
        ])


if __name__ == '__main__':
    _create_tables()
