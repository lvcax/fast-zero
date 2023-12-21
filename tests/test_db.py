from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.models import Todo, User


def test_create_user_without_todos(session):
    new_user = User(
        username='alice', password='senhatop', email='alice@example.com'
    )
    session.add(new_user)
    session.commit()

    user = session.scalar(select(User).where(User.username == 'alice'))

    assert user.username == 'alice'

def test_create_todo(session: Session, user: User):
    todo = Todo(
        title='Test todo',
        description='Test desc',
        state='draft',
        user_id=user.id
    )

    session.add(todo)
    session.commit()
    session.refresh(todo)

    user = session.scalar(select(User).where(User.id == user.id))

    assert todo in user.todos
