from prefect import task, flow, get_run_logger

@task
def process_eeg_data(eeg_data):
    # Placeholder for processing EEG data
    print("Processing EEG data...")
    # Add actual processing logic here
    return "Processed EEG data"

@flow
def eeg_data_flow():
    eeg_data = "raw EEG data here"  # Placeholder for actual EEG data
    processed_data = process_eeg_data(eeg_data)
    logger = get_run_logger()
    logger.info(processed_data)
    print(processed_data)

eeg_data_flow()
