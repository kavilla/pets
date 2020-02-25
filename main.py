# import utils
# if __name__ == '__main__':
# utils._create_tables()
from flask import Flask, jsonify, request
from models import Person, InvalidRequestException
from playhouse.shortcuts import model_to_dict

app = Flask(__name__)


@app.route('/person', methods=['GET'])
def person_list():
    results = Person.select().execute()
    return jsonify({'data': [person for person in results]})


@app.route('/person', methods=['POST'])
def create_person():
    data = request.get_json(force=True)
    first_name = data['first_name']
    last_name = data['last_name']

    if first_name is None or last_name is None:
        raise InvalidRequestException

    person = Person(first_name=first_name, last_name=last_name)
    person.save()

    return jsonify(model_to_dict(person))


app.run()
