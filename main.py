# import utils
# if __name__ == '__main__':
# utils._create_tables()
from flask import Flask, jsonify, request
from models import Person, Pet, InvalidRequestException
from playhouse.shortcuts import model_to_dict

app = Flask(__name__)


@app.route('/person', methods=['GET'])
def person_list():
    results = Person.select().execute()
    return jsonify({'data': [model_to_dict(result) for result in results]})


@app.route('/person/<int:id>', methods=['GET'])
def person(id):
    result = Person.get(Person.id == id)
    return jsonify(model_to_dict(result))


@app.route('/person', methods=['POST'])
def create_person():
    data = request.get_json(force=True)
    first_name = data['first_name']
    last_name = data['last_name']

    if first_name is None or last_name is None:
        raise InvalidRequestException

    result = Person(first_name=first_name, last_name=last_name)
    result.save()

    return jsonify(model_to_dict(result))


@app.route('/person/<int:person_id>/pet/<int:id>', methods=['GET'])
def pet(person_id, id):
    result = Pet.get(Pet.owner == person_id, Pet.id == id)
    return jsonify(model_to_dict(result))


@app.route('/person/<int:person_id>/pet', methods=['GET'])
def pet_list(person_id):
    results = Pet.select().join(Person).where(Person.id == person_id).execute()
    return jsonify({'data': [model_to_dict(result) for result in results]})


@app.route('/person/<int:person_id>/pet', methods=['POST'])
def create_pet(person_id):
    owner = Person.get(Person.id == person_id)
    data = request.get_json(force=True)
    name = data['name']

    if name is None:
        raise InvalidRequestException

    result = Pet(name=name, owner=owner)
    result.save()

    return jsonify(model_to_dict(result))


app.run()
