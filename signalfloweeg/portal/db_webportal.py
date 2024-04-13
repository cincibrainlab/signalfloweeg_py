from signalfloweeg.portal.sessionmaker import get_db
from signalfloweeg.portal.models import (
    EegFormat, 
    EegParadigm
    )

def get_eeg_formats():
    with get_db() as session:
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
    with get_db() as session:
        eeg_paradigms = session.query(EegParadigm).all()
        return [
            {
                "id": eeg_paradigm.id,
                "name": eeg_paradigm.name,
                "description": eeg_paradigm.description
            }
            for eeg_paradigm in eeg_paradigms
        ]
