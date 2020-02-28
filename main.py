from flask import Flask, request, abort
from playhouse.shortcuts import model_to_dict
from utils import generate_response

from models import Person, Pet, InvalidRequestException, NotFoundException, ConflictException

app = Flask(__name__)


@app.route('/persons', methods=['GET'])
def person_list():
    results = Person.select().execute()
    response = generate_response({'data': [model_to_dict(result) for result in results]}, 200)
    return response


@app.route('/persons/<int:person_id>', methods=['GET'])
def person(person_id):
    try:
        result = Person.get_or_none(Person.id == person_id)
        if result is None:
            raise NotFoundException

        response = generate_response(model_to_dict(result), 200)
    except NotFoundException as e:
        app.logger.error(e)
        response = generate_response({'Message': 'Person not found'}, 404)

    return response


@app.route('/persons', methods=['POST'])
def create_person():
    try:
        data = request.get_json(force=True)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        partner_id = data.get('partner_id')
        partner = None

        if first_name is None or last_name is None:
            raise InvalidRequestException

        if partner_id is not None:
            partner = Person.get_or_none(Person.id == partner_id)
            if partner is None:
                raise NotFoundException
            if partner.partner is not None:
                raise ConflictException

        result = Person(first_name=first_name, last_name=last_name, partner=partner)
        result.save()

        if partner is not None:
            partner.partner = result
            partner.save()

        response = generate_response(model_to_dict(result), 201)
    except InvalidRequestException as e:
        app.logger.error(e)
        response = generate_response({'Message': 'Invalid request'}, 400)
    except NotFoundException as e:
        app.logger.error(e)
        response = generate_response({'Message': 'Partner not found'}, 404)
    except ConflictException as e:
        app.logger.error(e)
        response = generate_response({'Message': 'Partner already married'}, 409)

    return response


@app.route('/persons/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    try:
        result = Person.get_or_none(Person.id == person_id)
        if result is None:
            raise NotFoundException

        data = request.get_json(force=True)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        partner_id = data.get('partner_id')
        partner = result.partner

        if first_name is None or last_name is None:
            raise InvalidRequestException

        if partner_id is not None:
            if partner is not None and partner_id != partner.id:
                raise InvalidRequestException
            if partner is None:
                partner = Person.get_or_none(Person.id == partner_id)
                if partner is not None and partner.partner is not None:
                    raise ConflictException

        result.first_name = first_name
        result.last_name = last_name
        result.partner = partner
        result.save()

        if partner is not None:
            partner.partner = result
            partner.save()

        response = generate_response(model_to_dict(result), 200)
    except InvalidRequestException as e:
        app.logger.error(e)
        response = generate_response({'Message': 'Invalid request'}, 400)
    except NotFoundException as e:
        app.logger.error(e)
        response = generate_response({'Message': 'Person not found'}, 404)
    except ConflictException as e:
        app.logger.error(e)
        response = generate_response({'Message': 'Partner already married'}, 409)

    return response


@app.route('/persons/<int:person_id>', methods=['DELETE'])
def remove_person(person_id):
    result = Person.get_or_none(Person.id == person_id)
    if result is None:
        return generate_response({'Message': 'No rows were removed.'}, 200)

    partner = result.partner
    Pet.update(owner=partner).where(Pet.owner == result).execute()

    if partner is not None:
        partner.partner = None
        partner.save()

    return generate_response({'Message': f'{result.delete_instance()} rows were removed.'}, 200)


@app.route('/persons/<int:person_id>/pets/<int:pet_id>', methods=['GET'])
def pet(person_id, pet_id):
    try:
        result = Pet.get_or_none(Pet.owner == person_id, Pet.id == pet_id)
        if result is None:
            raise NotFoundException

        response = generate_response(model_to_dict(result), 200)
    except NotFoundException as e:
        app.logger.error(e)
        response = generate_response({'Message': 'Person or pet not found'}, 404)

    return response


@app.route('/persons/pets', methods=['GET'])
def pet_list_null_owner():
    results = Pet.select().where(Pet.owner.is_null()).execute()
    response = generate_response({'data': [model_to_dict(result) for result in results]}, 200)
    return response


@app.route('/persons/<int:person_id>/pets', methods=['GET'])
def pet_list(person_id):
    try:
        owner = Person.get_or_none(Person.id == person_id)
        if owner is None:
            raise NotFoundException

        results = Pet.select().where(Pet.owner == person_id)
        response = generate_response({'data': [model_to_dict(result) for result in results]}, 200)
    except NotFoundException as e:
        app.logger.error(e)
        response = generate_response({'Message': 'Owner not found'}, 404)

    return response


@app.route('/persons/<int:person_id>/pets', methods=['POST'])
def create_pet(person_id):
    try:
        owner = Person.get_or_none(Person.id == person_id)
        if owner is None:
            raise NotFoundException

        data = request.get_json(force=True)
        name = data['name']

        if name is None:
            raise InvalidRequestException

        result = Pet(name=name, owner=owner)
        result.save()

        response = generate_response(model_to_dict(result), 201)
    except NotFoundException as e:
        app.logger.error(e)
        response = generate_response({'Message': 'Partner not found'}, 404)
    except InvalidRequestException as e:
        app.logger.error(e)
        response = generate_response({'Message': 'Invalid request'}, 400)

    return response


app.run()
