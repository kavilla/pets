from flask import Response, json

from models import db, Person, Pet, InvalidRequestException, NotFoundException, ConflictException

MODELS = [Person, Pet]


def _create_tables():
    with db:
        db.create_tables(MODELS)


def _drop_tables():
    with db:
        db.drop_tables(MODELS)


def generate_response(json_object, code):
    """
    Return a Flask response with a JSON body.
    """
    return Response(json.dumps(json_object), status=code, mimetype='application/json')


def generate_message_response(message, code):
    """
    Return a Flask response with a JSON body for message.
    """
    json_object = {'Message': message}
    return generate_response(json_object, code)


def generate_error_response(exception):
    """
    Return a Flask response with a JSON error body and code based on exception.
    """
    exception_type = type(exception)
    exception_message = str(exception)
    if exception_type is InvalidRequestException:
        response = generate_message_response(exception_message, 400)
    elif exception_type is NotFoundException:
        response = generate_message_response(exception_message, 404)
    elif exception_type is ConflictException:
        response = generate_message_response(exception_message, 409)
    else:
        response = generate_message_response(exception_message, 500)

    return response


if __name__ == '__main__':
    _create_tables()
