from models import db, Person, Pet
from flask import Response, json


def _create_tables():
    with db:
        db.create_tables([
            Person,
            Pet
        ])


def generate_response(json_object, code):
    """
    Return a Flask response with a JSON body.
    """
    return Response(json.dumps(json_object), status=code, mimetype='application/json')


if __name__ == '__main__':
    _create_tables()
