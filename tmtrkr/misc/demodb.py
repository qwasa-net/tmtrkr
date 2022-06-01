"""Demo database."""
import argparse
import datetime
import logging
import random
import string

from tmtrkr.models import Record, User, db_session

__all__ = ["create_demo_database"]
TODAY = datetime.date.today()


def generate_word():
    """Make a name part."""
    return "".join(random.choices(string.ascii_lowercase, k=random.randint(3, 10)))


def create_user(db):
    """Create a demo user."""
    user_name = " ".join([generate_word() for _ in ("first", "last")]).title()
    user = User(name=user_name)
    user.save(db)
    return user


def create_record(db, users):
    """Create a demo record."""
    record_name = " ".join([generate_word() for _ in range(random.randint(3, 10))]).capitalize() + "."
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
    record = Record(user_id=user.id, name=record_name, start=start.timestamp(), end=end.timestamp())
    record.save(db)
    return record


def create_demo_database(n_users=8, n_records=2**10):
    """Generate users and records."""
    db = next(db_session())
    users = []
    for _ in range(n_users):
        user = create_user(db)
        logging.info(user)
        users.append(user)
    records = []
    for _ in range(n_records):
        record = create_record(db=db, users=users)
        logging.info(record)
        records.append(record)


def count_records():
    """Return number of records in the database."""
    db = next(db_session())
    return Record.query(db).count()


def main():
    """Read cli parameters and start mumbling."""
    logging.root.setLevel(logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--only-if-empty", action="store_true")
    parser.add_argument("--today", type=str)
    args = parser.parse_args()
    if args.only_if_empty and count_records() > 0:
        logging.warning("database is not empty -- no demo data")
        return 0
    if args.today:
        global TODAY
        TODAY = datetime.datetime.strptime(args.today, "%Y-%m-%d").date()
    create_demo_database()


if __name__ == "__main__":
    main()
