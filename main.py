from flask import Flask, jsonify, request, abort
from playhouse.shortcuts import model_to_dict

from models import Person, Pet, InvalidRequestException, NotFoundException, ConflictException

app = Flask(__name__)


@app.route('/person', methods=['GET'])
def person_list():
    results = Person.select().execute()
    return jsonify({'data': [model_to_dict(result) for result in results]})


@app.route('/person/<int:id>', methods=['GET'])
def person(id):
    result = Person.get(Person.id == id)
    # TODO: handle not found
    return jsonify(model_to_dict(result))


@app.route('/person', methods=['POST'])
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

        return jsonify(model_to_dict(result))
    except InvalidRequestException as e:
        app.logger.error(e)
        abort(400)
    except NotFoundException as e:
        app.logger.error(e)
        abort(404)
    except ConflictException as e:
        app.logger.error(e)
        abort(409)


@app.route('/person/<int:id>', methods=['PUT'])
def update_person(id):
    try:
        result = Person.get_or_none(Person.id == id)
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
                if partner.partner is not None:
                    raise ConflictException

        result.first_name = first_name
        result.last_name = last_name
        result.partner = partner
        result.save()

        if partner is not None:
            partner.partner = result
            partner.save()

        return jsonify(model_to_dict(result))
    except InvalidRequestException as e:
        app.logger.error(e)
        abort(400)
    except NotFoundException as e:
        app.logger.error(e)
        abort(404)
    except ConflictException as e:
        app.logger.error(e)
        abort(409)


@app.route('/person/<int:id>', methods=['DELETE'])
def remove_person(id):
    result = Person.get_or_none(Person.id == id)
    partner = result.partner
    Pet.update(owner=partner).where(Pet.owner == result).execute()

    if partner is not None:
        partner.partner = None
        partner.save()

    return jsonify(result.delete_instance())


@app.route('/person/<int:person_id>/pet/<int:id>', methods=['GET'])
def pet(person_id, id):
    # TODO: handle person_id not found and id not found
    result = Pet.get(Pet.owner == person_id, Pet.id == id)
    return jsonify(model_to_dict(result))


@app.route('/person/pet', methods=['GET'])
def pet_list_null_owner():
    results = Pet.select().where(Pet.owner.is_null()).execute()
    return jsonify({'data': [model_to_dict(result) for result in results]})


@app.route('/person/<int:person_id>/pet', methods=['GET'])
def pet_list(person_id):
    # TODO: handle person_id not found
    results = Pet.select().join(Person).where(Person.id == person_id).execute()
    return jsonify({'data': [model_to_dict(result) for result in results]})


@app.route('/person/<int:person_id>/pet', methods=['POST'])
def create_pet(person_id):
    try:
        owner = Person.get(Person.id == person_id)
        data = request.get_json(force=True)
        name = data['name']

        if name is None:
            raise InvalidRequestException

        result = Pet(name=name, owner=owner)
        result.save()

        return jsonify(model_to_dict(result))
    except InvalidRequestException as e:
        app.logger.error(e)
        abort(400)


app.run()
