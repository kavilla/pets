from utils import _create_tables, _drop_tables


def create_test_client(app):
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['DEBUG'] = False
    _create_tables()
    return app.test_client()


def destroy_test_client():
    _drop_tables()
