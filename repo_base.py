from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app import db
from exceptions import DatabaseError, DuplicateError


def commit_or_raise(duplicate_msg: str = None):
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise DuplicateError(duplicate_msg or str(e)) from e
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(str(e)) from e
