"""Demo database."""
from tmtrkr.models import Record, User, db_session
import random
import datetime
import string
import this

__all__ = ["create_demo_database"]
TODAY = datetime.date.today()
RECORDS_LIST = list(filter(None, this.s.split("\n")))


def generate_name():
    """Make a name part."""
    return "".join(random.choices(string.ascii_lowercase, k=random.randint(3, 10)))


def create_user(db):
    """Create a demo user."""
    username = " ".join([generate_name() for _ in ("first", "last")]).title()
    user = User(name=username)
    user.save(db)
    return user


def create_record(db, users, records_list=RECORDS_LIST):
    """Create a demo record."""
    name = random.choice(records_list)
    start = datetime.datetime(
        TODAY.year,
        random.randint(1, 12),
        random.randint(2, 28),
        random.randint(8, 17),
        random.randint(0, 3) * 15,
        0,
        tzinfo=datetime.timezone.utc,
    )
    end = start + datetime.timedelta(minutes=(10 * random.randint(1, 24)))
    user = random.choice(users)
    record = Record(user_id=user.id, name=name, start=start.timestamp(), end=end.timestamp())
    record.save(db)
    return record


def create_demo_database(n_users=8, n_records=2**10):
    """Generate users and records."""
    db = next(db_session())
    users = []
    for _ in range(n_users):
        user = create_user(db)
        print(user)
        users.append(user)
    records = []
    for _ in range(n_records):
        record = create_record(db=db, users=users)
        print(record)
        records.append(record)


if __name__ == "__main__":
    create_demo_database()
