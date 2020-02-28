## Project Requirements
Provided files:
- models.py: Contains the ORM data models mapping to tables in the database using the peewee package. Use this to query the database.
- settings.py: Contains configuration objects. Add to this file as you see fit.
- utils.py: Contains a function for creating the PostgreSQL tables according to the models defined in models.py.
- requirements.txt: Contains the package dependencies.
- main.py: Add your code to this file. Create any other files as you see fit.

Objectives:
1. Set up your environment. Install the required Python packages and set up a local PostgreSQL database. Initialize the database with four Person objects.
2. Create a Flask app that has REST API endpoints to handle the following scenarios:
	3. A couple gets married
	4. A person gets pets
	5. A person passes away, and their pets go to their partner, or to null owner if they have no partner
6. A front end view isn't required, but if you'd like to add one, we'd be more than happy to use it!

Support:
- Contact Chad Becker at chad@meetyogi.com if you have any questions or discover any problems
- We're looking to see how you approach the problem, document your assumptions, design your solution, and communicate the results.

## Getting started

* Clone this repo

`How to run the API:`

* [Setup PostgreSQL](https://www.postgresqltutorial.com/install-postgresql/)
* Update the settings.py DATABASE config appropriately
* Create the tables:
```
python utils.py _create_tables
```
* [Install python, create and run a virtual environment](https://www.twilio.com/docs/usage/tutorials/how-to-set-up-your-python-and-flask-development-environment)
  * Here's my virtual environment name:
    ```
    python -m venv env
    source env/Scripts/activate
    ```
* Install the dependencies by running:
  ```
  pip install -r requirements.txt
  ```
* Run the API by running:
  ```
  python main.py
  ```
* Make requests to [http://localhost:5000](http://localhost:5000), 
	* Or use the swagger page here: [http://localhost:5000/apidocs/](http://localhost:5000/apidocs/)

## API

- GET http://localhost:5000/persons
	- Successful : 200 (returns person list)
- GET http://localhost:5000/persons/{person_id}
	- Successful: 200 (returns person with person_id is id)
	- Not Found: 404 (person with person_id does not exist)
- POST http://localhost:5000/persons
	- Create a person with a body:
	```
	{
		"first_name": "required",
		"last_name": "required",
		"partner_id" "optional"
	}
	```
	- Successful : 201 (returns created person)
	- Invalid request: 400 (missing first_name or last_name)
	- Not Found: 404 (person with partner_id does not exist)
	- Conflict: 409 (person with partner_id has a partner already)
- PUT http://localhost:5000/persons/{person_id}
	- Updates a person with a body:
	```
	{
		"first_name": "required",
		"last_name": "required",
		"partner_id" "optional"
	}
	```
	- Successful : 200 (returns updated person)
	- Invalid request: 400 (missing first_name or last_name or if person is already married if the partner_id is not the existing partner's id)
	- Not Found: 404 (person with id does not exist)
	- Conflict: 409 (person with partner_id has a partner already)
- DELETE http://localhost:5000/persons/{person_id}
	- Successful : 200 (returns row delete)
- GET http://localhost:5000/persons/{person_id}/pets
	- Successful : 200 (returns pet list for person)
	- Not Found: 404 (person with person_id does not exist)
- GET http://localhost:5000/persons/pets
	- Successful : 200 (returns pet list for null owner)
- GET http://localhost:5000/persons/{person_id}/pets/{pet_id}
	- Successful : 200 (returns pet with id and person_id)
	- Not Found: 404 (person with person_id does not exist or pet with pet_id does not exist)
- POST http://localhost:5000/persons/{person_id}/pets
	- Create a pet with a body:
	```
	{
		"name": "required"
	}
	```
	- Successful : 201 (returns created pet with owner with id that equals person_id)
	- Invalid request: 400 (missing name)
	- Not Found: 404 (person with person_id does not exist)

### Solution

- Passing a partner_id in a POST person will successfully marry partners if the partner_id exists and if the partner is not already married.
- Passing a partner_id in a PUT person will successfully marry partners if the partner_id exists, if the person isn't already married, and if the partner is not already married.
- POST pet for an person is a person getting a pet.
- DELETE a person is a person dying if they exist. If the person had a partner, then the pets get transferred to the partner and the partner no longer is married to the person. If the person did not have a partner, the pets owner is null.

### Assumptions

- People can't get remarried if currently married.
- People are married until a person dies, even if try to PUT person and if you don't pass the partner_id and the person is married they won't get divorced.
- People can have multiple pets.
- Pets LIVE FOREVER.
- Pets names are written in stone but a person first name and last name can change.

## TODO
- Cleanup conditionals related to marriage
- Add function comments for reusability
- Update PUT person to a PATCH
	- The partner_id being optional on a PUT is not correct if the behavior changes if you do pass it will try to modify it but if person is married. and you don't pass partner_id it won't divorce a person. This is bad for  PUT.
- Create UI