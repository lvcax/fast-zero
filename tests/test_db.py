from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    new_user = User(
        username='alice', password='senhatop', email='alice@example.com'
    )
    session.add(new_user)
    session.commit()

    user = session.scalar(select(User).where(User.username == 'alice'))

    assert user.username == 'alice'
