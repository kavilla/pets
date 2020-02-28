from flasgger import Swagger, swag_from
from flask import Flask, request
from playhouse.shortcuts import model_to_dict

from models import Person, Pet, InvalidRequestException, NotFoundException, ConflictException
from utils import generate_response

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Yogi API',
    'description': 'Simple API for marrying partners and adopting pets.',
    "termsOfService": None,
    "version": "1.0.1"
}
swagger = Swagger(app)


@app.route('/persons', methods=['GET'])
@swag_from('.docs/person_list.yml')
def person_list():
    """
    Get a list of persons.
    """
    results = Person.select().execute()
    response = generate_response({'data': [model_to_dict(result) for result in results]}, 200)
    return response


@app.route('/persons/<int:person_id>', methods=['GET'])
@swag_from('.docs/person.yml')
def person(person_id):
    """
    Get an existing person.
    """
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
@swag_from('.docs/create_person.yml')
def create_person():
    """
    Create a person and marries partners if eligible.
    """
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


@app.route('/persons/<int:person_id>', methods=['PATCH'])
@swag_from('.docs/update_person.yml')
def update_person(person_id):
    """
    Update a person and marries partners if eligible.
    """
    try:
        result = Person.get_or_none(Person.id == person_id)
        if result is None:
            raise NotFoundException

        data = request.get_json(force=True)

        first_name = data.get('first_name')
        if first_name is not None:
            result.first_name = first_name

        last_name = data.get('last_name')
        if last_name is not None:
            result.last_name = last_name

        partner_id = data.get('partner_id')
        if partner_id is not None:
            partner = result.partner
            if partner is None:
                partner = Person.get_or_none(Person.id == partner_id)
                if partner is None:
                    raise NotFoundException
                if partner.partner is not None:
                    raise ConflictException

            if partner_id != partner.id:
                raise InvalidRequestException

            if partner is not None:
                partner.partner = result
                partner.save()

            result.partner = partner

        result.save()

        response = generate_response(model_to_dict(result), 200)
    except InvalidRequestException as e:
        app.logger.error(e)
        response = generate_response({'Message': 'Invalid request'}, 400)
    except NotFoundException as e:
        app.logger.error(e)
        response = generate_response({'Message': 'Person or partner not found'}, 404)
    except ConflictException as e:
        app.logger.error(e)
        response = generate_response({'Message': 'Partner already married'}, 409)

    return response


@app.route('/persons/<int:person_id>', methods=['DELETE'])
@swag_from('.docs/remove_person.yml')
def remove_person(person_id):
    """
    Remove a person and transfers pets to partner or null partner if not married.
    """
    result = Person.get_or_none(Person.id == person_id)
    if result is None:
        return generate_response({'Message': 'Number of rows removed: 0'}, 200)

    partner = result.partner
    Pet.update(owner=partner).where(Pet.owner == result).execute()

    if partner is not None:
        partner.partner = None
        partner.save()

    return generate_response({'Message': f'Number of rows removed: {result.delete_instance()}'}, 200)


@app.route('/persons/<int:person_id>/pets/<int:pet_id>', methods=['GET'])
@swag_from('.docs/pet.yml')
def pet(person_id, pet_id):
    """
    Get an existing pet from an existing owner.
    """
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
@swag_from('.docs/pet_list_null_owner.yml')
def pet_list_null_owner():
    """
    Get a list of pets from null owner.
    """
    results = Pet.select().where(Pet.owner.is_null()).execute()
    response = generate_response({'data': [model_to_dict(result) for result in results]}, 200)
    return response


@app.route('/persons/<int:person_id>/pets', methods=['GET'])
@swag_from('.docs/pet_list.yml')
def pet_list(person_id):
    """
    Get a list of pets from an existing owner.
    """
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
@swag_from('.docs/create_pet.yml')
def create_pet(person_id):
    """
    Create a pet for an existing owner.
    """
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
        response = generate_response({'Message': 'Owner not found'}, 404)
    except InvalidRequestException as e:
        app.logger.error(e)
        response = generate_response({'Message': 'Invalid request'}, 400)

    return response


app.run()
