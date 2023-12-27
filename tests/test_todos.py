import factory.fuzzy

from fast_zero.models import User, Todo, TodoState


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo
    
    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo(client, token):
    response = client.post(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'test todo',
            'description': 'test todo description',
            'state': 'draft'
        }
    )

    assert response.json() == {
        'id': 1,
        'title': 'test todo',
        'description': 'test todo description',
        'state': 'draft'
    }


def test_list_todos(session, client, user, token):
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == 5


def test_list_todos_pagination(session, user, client, token):
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == 2


def test_list_todos_filter_title(session, user, client, token):
    session.bulk_save_objects(
        TodoFactory.create_batch(5, user_id=user.id, title='test todo 1')
    )
    session.commit()

    response = client.get(
        '/todos/?title=test todo 1',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == 5


def test_list_todos_filter_description(session, user, client, token):
    session.bulk_save_objects(
        TodoFactory.create_batch(4, user_id=user.id, description='description')
    )
    session.commit()

    response = client.get(
        '/todos/?description=desc',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == 4


def test_list_todos_filter_state(session, user, client, token):
    session.bulk_save_objects(
        TodoFactory.create_batch(5, user_id=user.id, state=TodoState.draft)
    )
    session.commit()

    response = client.get(
        '/todos/?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == 5


def test_list_todos_filter_combined(session, user, client, token):
    session.bulk_save_objects(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='test todo combined',
            description='combined description',
            state=TodoState.done
        )
    )

    session.bulk_save_objects(
        TodoFactory.create_batch(
            9,
            user_id=user.id,
            title='other title',
            description='other description',
            state=TodoState.todo
        )
    )

    session.commit()

    response = client.get(
        '/todos/?title=test todo combined&description=combined&state=done',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == 5


def test_patch_todo_error(client, token):
    response = client.patch(
        '/todos/10',
        json={},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 404
    assert response.json() == {'detail': 'task not found'}


def test_patch_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        json={'title': 'test!'},
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    assert response.json()['title'] == 'test!'


def test_delete_todo(session, client, user, token):
    todo = TodoFactory(id=1, user_id=user.id)

    session.add(todo)
    session.commit()

    response = client.delete(
        f'/todos/{todo.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    assert response.json() == {'detail': 'task has been deleted successfully'}


def test_delete_todo_error(client, token):
    response = client.delete(
        f'/todos/{10}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 404
    assert response.json() == {'detail': 'task not found'}
