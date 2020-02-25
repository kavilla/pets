Provided files:
    - models.py: Contains the ORM data models mapping to tables in the database using the peewee package. Use this to query the database.
    - settings.py: Contains configuration objects. Add to this file as you see fit.
    - utils.py: Contains a function for creating the PostgreSQL tables according to the models defined in models.py.
    - requirements.txt: Contains the package dependencies.
    - main.py: Add your code to this file. Create any other files as you see fit.

Objectives:
    1) Set up your environment. Install the required Python packages and set up a local PostgreSQL database. Initialize the database with four Person objects.

    2) Create a Flask app that has REST API endpoints to handle the following scenarios:
        - A couple gets married
        - A person gets pets
        - A person passes away, and their pets go to their partner, or to null owner if they have no partner
       A front end view isn't required, but if you'd like to add one, we'd be more than happy to use it!

Support:
    - Contact Chad Becker at chad@meetyogi.com if you have any questions or discover any problems
    - We're looking to see how you approach the problem, document your assumptions, design your solution, and communicate the results.