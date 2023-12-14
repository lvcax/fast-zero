from fast_zero.schemas import UserPublic


def test_root_must_return_200_and_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.json() == {'message': 'ola mundo'}


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@example.com',
        'id': 1,
    }


def test_create_user_when_user_already_exist(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'teste',
            'email': 'teste@test.com',
            'password': 'testest',
        },
    )

    assert response.status_code == 400
    assert response.json() == {'detail': 'username already registered'}


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == 200
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@example.com',
        'id': 1,
    }


# refactor test!
def test_update_user_that_not_exist(client, user, token):
    response = client.put(
        '/users/2',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == 400
    assert response.json() == {'detail': 'not enough permissions'}


def test_delete_user(client, user, token):
    response = client.delete(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'}
        )

    assert response.status_code == 200
    assert response.json() == {'detail': 'user deleted'}


# refactor test!
def test_delete_user_error(client, user, token):
    response = client.delete(
            '/users/2',
            headers={'Authorization': f'Bearer {token}'}
        )

    assert response.status_code == 400
    assert response.json() == {'detail': 'not enough permissions'}
