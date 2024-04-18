from signalfloweeg.portal.db_connection import get_session
from signalfloweeg.portal.models import (
    EegFormat,
    EegParadigm
    )
from signalfloweeg.portal.portal_config import get_eeg_formats_dict

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

if __name__ == "__main__":
    print(get_eeg_formats())
    print(get_eeg_paradigms())