from signalfloweeg.portal.sessionmaker import get_db
from signalfloweeg.portal.models import (
    DatasetCatalog
)

def clear_dataset_info():
    with get_db() as session:
        session.query(DatasetCatalog).delete()
        session.commit()

def delete_dataset_info(dataset_id):
    with get_db() as session:
        session.query(DatasetCatalog).filter(DatasetCatalog.dataset_id == dataset_id).delete()
        session.commit()

def get_dataset_info():
    with get_db() as session:
        datasets = session.query(DatasetCatalog).all()
        return [
            {
                "id": dataset.dataset_id,
                "name": dataset.dataset_name,
                "description": dataset.description,
                "eeg_format": dataset.eeg_format.name if dataset.eeg_format else None,
                "eeg_paradigm": dataset.eeg_paradigm.name if dataset.eeg_paradigm else None
            }
            for dataset in datasets
        ]
