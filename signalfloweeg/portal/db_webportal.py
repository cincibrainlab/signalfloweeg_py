from signalfloweeg.portal.db_connection import get_session
from signalfloweeg.portal.models import (
    EegFormat,
    EegParadigm,
    Users
    )

def get_eeg_formats():
    with get_session() as session:
        eeg_formats = session.query(EegFormat).all()
        return [
            {
                "id": eeg_format.id,
                "name": eeg_format.name,
                "description": eeg_format.description
            }
            for eeg_format in eeg_formats
        ]


def get_eeg_paradigms():
    with get_session() as session:
        eeg_paradigms = session.query(EegParadigm).all()
        return [
            {
                "id": eeg_paradigm.id,
                "name": eeg_paradigm.name,
                "description": eeg_paradigm.description
            }
            for eeg_paradigm in eeg_paradigms
        ]

def get_emails():
    with get_session() as session:
        users = session.query(Users).all()
        return [
            {
                "id": user.user_id,
                "name": user.email
            }
            for user in users
        ]

if __name__ == "__main__":
    print(get_eeg_formats())
    print(get_eeg_paradigms())