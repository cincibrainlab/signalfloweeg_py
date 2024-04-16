import logging
from signalfloweeg.portal.models import Base
import signalfloweeg.portal.models as models
from signalfloweeg.portal.sessionmaker import (
    get_db,
    get_engine_and_session,
    generate_database_summary
)

def populate_support_tables():
    """
    Populates EEGFormat and EEGParadigm records from a YAML file.

    """
    # Assuming load_config, get_db and EegFormat are defined elsewhere
    Session = sessionmaker(bind=get_db())

    console = Console()

    with Session() as session:

        def process_items(items, model, title):
            table = Table(title=f"[bold]{title}[/bold]")
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Description", style="magenta")
            for item in items:
                if not session.query(model).filter_by(name=item["name"]).first():
                    session.add(
                        model(name=item["name"], description=item["description"])
                    )
                    session.commit()
                table.add_row(item["name"], item["description"])
            console.print(table)
            console.print()

        process_items(config["eeg_formats"], EegFormat, "EEG Formats")
        process_items(config["eeg_paradigms"], EegParadigm, "EEG Paradigms")

        # Assuming EEG Analyses are also to be processed in a similar fashion
        for analysis_data in config["eeg_analyses"]:
            if (
                not session.query(EegAnalyses)
                .filter_by(name=analysis_data["name"])
                .first()
            ):
                eeg_analysis = EegAnalyses(
                    name=analysis_data["name"],
                    category=analysis_data["category"],
                    description=analysis_data["description"],
                    valid_formats=json.dumps(analysis_data["valid_formats"]),
                    valid_paradigms=json.dumps(analysis_data["valid_paradigms"]),
                    parameters=json.dumps(analysis_data["parameters"]),
                )
                session.merge(eeg_analysis)
                session.commit()

            # Display analysis details
            analysis_table = Table(
                title=f"[bold]Analysis Name: {analysis_data['name']}[/bold]"
            )
            analysis_table.add_column("Category", style="cyan", no_wrap=True)
            analysis_table.add_column("Description", style="magenta")
            analysis_table.add_column("Valid Formats", style="green")
            analysis_table.add_column("Valid Paradigms", style="yellow")
            analysis_table.add_column("Parameters", style="blue")
            analysis_table.add_row(
                analysis_data["category"],
                analysis_data["description"],
                str(analysis_data["valid_formats"]),
                str(analysis_data["valid_paradigms"]),
                str(analysis_data["parameters"]),
            )
            console.print(analysis_table)
            console.print()


def drop_all_tables():
    success = False
    try:
        logging.warning("Initiating drop_all_tables function.")
        generate_database_summary()
        engine, session = get_engine_and_session()
        # disable foreign key constraint
        logging.info("Disabling foreign key constraint...")
        session.execute("SET CONSTRAINTS ALL DEFERRED;")
        session.commit()

        logging.info("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)

        # enable foreign key constraint
        logging.info("Enabling foreign key constraint...")
        session.execute("SET CONSTRAINTS ALL IMMEDIATE;")
        session.commit()

        session.close()

        logging.info("All tables dropped successfully.")
        success = True
    except Exception as e:
        logging.error(f"Failed to drop all tables: {e}")
    finally:
        logging.info("Disposing engine...")
        engine.dispose()
        return {"success": success, "message": "All tables dropped successfully." if success else "Failed to drop all tables."}

def drop_table(table_name):
    success = False
    try:
        logging.warning(f"Initiating drop_specific_table function for {table_name}.")
        generate_database_summary()
        engine, session = get_engine_and_session()
        # disable foreign key constraint
        logging.info("Disabling foreign key constraint...")
        session.execute("SET CONSTRAINTS ALL DEFERRED;")
        session.commit()

        logging.info(f"Dropping table {table_name}...")
        table_class = getattr(models, table_name)

        #table_class = getattr(Base.metadata.tables, table_name)
        table_class.drop(engine)

        # enable foreign key constraint
        logging.info("Enabling foreign key constraint...")
        session.execute("SET CONSTRAINTS ALL IMMEDIATE;")
        session.commit()

        session.close()

        logging.info(f"Table {table_name} dropped successfully.")
        success = True
    except Exception as e:
        logging.error(f"Failed to drop table {table_name}: {e}")
    finally:
        logging.info("Disposing engine...")
        engine.dispose()
        return {"success": success, "message": f"Table {table_name} dropped successfully." if success else f"Failed to drop table {table_name}."}
