import json
import unittest

from playhouse.shortcuts import model_to_dict

from main import app
from models import Person, Pet
from .test_base import create_test_client, destroy_test_client


class BasicTests(unittest.TestCase):
    def setUp(self):
        self.app = create_test_client(app)
        self.assertEqual(app.debug, False)

        self.app.NOT_FOUND_ID = 100
        person1_unmarried = Person(first_name='A', last_name='First')
        person1_unmarried.save()
        person2 = Person(first_name='B', last_name='Second')
        person2.save()
        person3_married = Person(first_name='Y', last_name='Zeta')
        person3_married.save()
        person4_married = Person(first_name='Z', last_name='Zeta', partner=person3_married)
        person4_married.save()
        person3_married.partner = person4_married
        person3_married.save()
        self.app.persons = [person1_unmarried, person2, person3_married, person4_married]
        self.app.persons_desc = self.app.persons[::-1]

        pet1 = Pet(name='PetA', owner=person1_unmarried)
        pet1.save()
        pet2 = Pet(name='PetB', owner=person3_married)
        pet2.save()
        pet3 = Pet(name='PetC', owner=person4_married)
        pet3.save()
        pet4 = Pet(name='PetD', owner=person4_married)
        pet4.save()
        pet5 = Pet(name='PetE')
        pet5.save()
        self.app.pets = [pet1, pet2, pet3, pet4, pet5]
        self.app.pets_desc = self.app.pets[::-1]

        self.app.persons_with_pets = [person1_unmarried, person3_married, person4_married]

    def tearDown(self):
        destroy_test_client()

    # person_list tests
    def test_person_list_happy_path(self):
        response = self.app.get('/persons')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'data': [model_to_dict(person) for person in self.app.persons_desc]})
        self.assertEqual(response.status_code, 200)

    # person tests
    def test_person_happy_path(self):
        person = self.app.persons[0]
        response = self.app.get(f'/persons/{person.id}')
        data = json.loads(response.data)
        self.assertDictEqual(data, model_to_dict(person))
        self.assertEqual(response.status_code, 200)

    def test_person_not_found(self):
        response = self.app.get(f'/persons/{self.app.NOT_FOUND_ID}')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'Person not found'})
        self.assertEqual(response.status_code, 404)

    # create_person tests
    def test_create_person_happy_path(self):
        body = dict(first_name='C', last_name='Third')
        response = self.app.post('/persons',
                                 data=json.dumps(body),
                                 content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(data['first_name'], body['first_name'])
        self.assertEqual(data['last_name'], body['last_name'])
        self.assertIsNone(data['partner'])
        self.assertEqual(response.status_code, 201)

    def test_create_person_married_happy_path(self):
        partner = next((person for person in self.app.persons if person.partner is None), None)
        body = dict(first_name='D', last_name='Second', partner_id=partner.id)
        response = self.app.post('/persons',
                                 data=json.dumps(body),
                                 content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(data['first_name'], body['first_name'])
        self.assertEqual(data['last_name'], body['last_name'])
        self.assertIsNotNone(data['partner'])
        self.assertEqual(data['partner']['id'], body['partner_id'])
        self.assertEqual(response.status_code, 201)

    def test_create_person_missing_first_name_invalid(self):
        body = dict(last_name='Third')
        response = self.app.post('/persons',
                                 data=json.dumps(body),
                                 content_type='application/json')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'First name is required'})
        self.assertEqual(response.status_code, 400)

    def test_create_person_missing_last_name_invalid(self):
        body = dict(first_name='D')
        response = self.app.post('/persons',
                                 data=json.dumps(body),
                                 content_type='application/json')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'Last name is required'})
        self.assertEqual(response.status_code, 400)

    def test_create_person_partner_not_found(self):
        body = dict(first_name='E', last_name='Fourth', partner_id=self.app.NOT_FOUND_ID)
        response = self.app.post('/persons',
                                 data=json.dumps(body),
                                 content_type='application/json')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'Partner not found'})
        self.assertEqual(response.status_code, 404)

    def test_create_person_partner_married_conflict(self):
        partner = next((person for person in self.app.persons if person.partner is not None), None)
        body = dict(first_name='D', last_name='Second', partner_id=partner.id)
        response = self.app.post('/persons',
                                 data=json.dumps(body),
                                 content_type='application/json')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'Partner already married'})
        self.assertEqual(response.status_code, 409)

    # update_person tests
    def test_update_person_happy_path(self):
        person = next((person for person in self.app.persons if person.partner is None), None)
        partner = next((partner for partner in self.app.persons if partner.partner is None and person.id != partner.id),
                       None)
        body = dict(first_name='Ab', last_name='Second', partner_id=partner.id)
        response = self.app.patch(f'/persons/{person.id}',
                                  data=json.dumps(body),
                                  content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(data['first_name'], body['first_name'])
        self.assertEqual(data['last_name'], body['last_name'])
        self.assertIsNotNone(data['partner'])
        self.assertEqual(data['partner']['id'], body['partner_id'])
        self.assertEqual(response.status_code, 200)

    def test_update_person_first_name_happy_path(self):
        person = next((person for person in self.app.persons if person.partner is None), None)
        body = dict(first_name='Ab')
        response = self.app.patch(f'/persons/{person.id}',
                                  data=json.dumps(body),
                                  content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(data['first_name'], body['first_name'])
        self.assertEqual(data['last_name'], person.last_name)
        self.assertIsNone(data['partner'])
        self.assertEqual(response.status_code, 200)

    def test_update_person_last_name_happy_path(self):
        person = next((person for person in self.app.persons if person.partner is None), None)
        body = dict(last_name='Seconds')
        response = self.app.patch(f'/persons/{person.id}',
                                  data=json.dumps(body),
                                  content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(data['first_name'], person.first_name)
        self.assertEqual(data['last_name'], body['last_name'])
        self.assertIsNone(data['partner'])
        self.assertEqual(response.status_code, 200)

    def test_update_person_married_happy_path(self):
        person = next((person for person in self.app.persons if person.partner is None), None)
        partner = next((partner for partner in self.app.persons if partner.partner is None and person.id != partner.id),
                       None)
        body = dict(partner_id=partner.id)
        response = self.app.patch(f'/persons/{person.id}',
                                  data=json.dumps(body),
                                  content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(data['first_name'], person.first_name)
        self.assertEqual(data['last_name'], person.last_name)
        self.assertIsNotNone(data['partner'])
        self.assertEqual(data['partner']['id'], body['partner_id'])
        self.assertEqual(response.status_code, 200)

    def test_update_person_not_found(self):
        partner = next((person for person in self.app.persons if person.partner is None), None)
        body = dict(first_name='Ab', last_name='Second', partner_id=partner.id)
        response = self.app.patch(f'/persons/{self.app.NOT_FOUND_ID}',
                                  data=json.dumps(body),
                                  content_type='application/json')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'Person not found'})
        self.assertEqual(response.status_code, 404)

    def test_update_person_partner_not_found(self):
        person = next((person for person in self.app.persons if person.partner is None), None)
        body = dict(first_name='Ab', last_name='Second', partner_id=self.app.NOT_FOUND_ID)
        response = self.app.patch(f'/persons/{person.id}',
                                  data=json.dumps(body),
                                  content_type='application/json')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'Partner not found'})
        self.assertEqual(response.status_code, 404)

    def test_update_person_partner_married_conflict(self):
        person = next((person for person in self.app.persons if person.partner is None), None)
        partner = next((partner for partner in self.app.persons if partner.partner is not None), None)
        body = dict(first_name='Ab', last_name='Second', partner_id=partner.id)
        response = self.app.patch(f'/persons/{person.id}',
                                  data=json.dumps(body),
                                  content_type='application/json')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'Partner already married'})
        self.assertEqual(response.status_code, 409)

    def test_update_person_person_married_invalid(self):
        person = next((person for person in self.app.persons if person.partner is not None), None)
        partner = next((partner for partner in self.app.persons if partner.partner is None), None)
        body = dict(first_name='Ab', last_name='Second', partner_id=partner.id)
        response = self.app.patch(f'/persons/{person.id}',
                                  data=json.dumps(body),
                                  content_type='application/json')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'Partner does not match partner_id'})
        self.assertEqual(response.status_code, 400)

    # remove_person tests
    def test_remove_person_exists_happy_path(self):
        person = self.app.persons[0]
        response = self.app.delete(f'/persons/{person.id}')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'Number of rows removed: 1'})
        self.assertEqual(response.status_code, 200)

    def test_remove_person_exists_with_pets_no_partner_happy_path(self):
        person = next(
            (person for person in self.app.persons if person.partner is None and person in self.app.persons_with_pets),
            None)
        pet = next((pet for pet in self.app.pets if pet.owner == person), None)
        pet.owner = None
        null_owner_pets = [pet for pet in self.app.pets if pet.owner is None]
        response = self.app.delete(f'/persons/{person.id}')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'Number of rows removed: 1'})
        self.assertEqual(response.status_code, 200)
        pets_response = self.app.get('/persons/pets')
        pets_data = json.loads(pets_response.data)
        self.assertDictEqual(pets_data, {'data': [model_to_dict(pet) for pet in null_owner_pets[::-1]]})
        self.assertEqual(response.status_code, 200)

    def test_remove_person_exists_with_pets_with_partner_happy_path(self):
        person = next((person for person in self.app.persons if
                       person.partner is not None and person in self.app.persons_with_pets), None)
        partner = person.partner
        partner.partner = None
        partner_pets = [pet for pet in self.app.pets if pet.owner == partner]
        pet = next((pet for pet in self.app.pets if pet.owner == person), None)
        pet.owner = partner
        partner_pets.insert(0, pet)
        response = self.app.delete(f'/persons/{person.id}')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'Number of rows removed: 1'})
        self.assertEqual(response.status_code, 200)
        pets_response = self.app.get(f'/persons/{partner.id}/pets')
        pets_data = json.loads(pets_response.data)
        self.assertDictEqual(pets_data, {'data': [model_to_dict(pet) for pet in partner_pets[::-1]]})
        self.assertEqual(response.status_code, 200)

    def test_remove_person_does_not_exists_happy_path(self):
        response = self.app.delete(f'/persons/{self.app.NOT_FOUND_ID}')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'Number of rows removed: 0'})
        self.assertEqual(response.status_code, 200)

    # pet
    def test_pet_happy_path(self):
        person = next((person for person in self.app.persons_with_pets), None)
        pet = next((pet for pet in self.app.pets if pet.owner == person), None)
        response = self.app.get(f'/persons/{person.id}/pets/{pet.id}')
        data = json.loads(response.data)
        self.assertDictEqual(data, model_to_dict(pet))
        self.assertEqual(response.status_code, 200)

    def test_pet_not_found(self):
        person = next((person for person in self.app.persons_with_pets), None)
        response = self.app.get(f'/persons/{person.id}/pets/{self.app.NOT_FOUND_ID}')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'Person and/or pet not found'})
        self.assertEqual(response.status_code, 404)

    def test_pet_owner_not_found(self):
        pet = self.app.pets[0]
        response = self.app.get(f'/persons/{self.app.NOT_FOUND_ID}/pets/{pet.id}')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'Person and/or pet not found'})
        self.assertEqual(response.status_code, 404)

    def test_pet_and_owner_not_found(self):
        response = self.app.get(f'/persons/{self.app.NOT_FOUND_ID}/pets/{self.app.NOT_FOUND_ID}')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'Person and/or pet not found'})
        self.assertEqual(response.status_code, 404)

    # pet_list_null_owner
    def test_pet_list_null_owner_happy_path(self):
        null_owner_pets = [pet for pet in self.app.pets if pet.owner is None]
        response = self.app.get(f'/persons/pets')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'data': [model_to_dict(pet) for pet in null_owner_pets[::-1]]})
        self.assertEqual(response.status_code, 200)

    # pet_list
    def test_pet_list_happy_path(self):
        person = next((person for person in self.app.persons_with_pets), None)
        pets = [pet for pet in self.app.pets if pet.owner == person]
        response = self.app.get(f'/persons/{person.id}/pets')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'data': [model_to_dict(pet) for pet in pets[::-1]]})
        self.assertEqual(response.status_code, 200)

    def test_pet_list_owner_not_found(self):
        response = self.app.get(f'/persons/{self.app.NOT_FOUND_ID}/pets')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'Owner not found'})
        self.assertEqual(response.status_code, 404)

    # create_pet
    def test_create_pet_happy_path(self):
        person = self.app.persons[0]
        body = dict(name='PetF')
        response = self.app.post(f'/persons/{person.id}/pets',
                                 data=json.dumps(body),
                                 content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(data['name'], body['name'])
        self.assertIsNotNone(data['owner'])
        self.assertEqual(data['owner']['id'], person.id)
        self.assertEqual(response.status_code, 201)

    def test_create_pet_owner_not_found(self):
        body = dict(name='PetF')
        response = self.app.post(f'/persons/{self.app.NOT_FOUND_ID}/pets',
                                 data=json.dumps(body),
                                 content_type='application/json')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'Owner not found'})
        self.assertEqual(response.status_code, 404)

    def test_create_pet_missing_name_invalid(self):
        person = self.app.persons[0]
        body = dict()
        response = self.app.post(f'/persons/{person.id}/pets',
                                 data=json.dumps(body),
                                 content_type='application/json')
        data = json.loads(response.data)
        self.assertDictEqual(data, {'Message': 'Name is required'})
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
