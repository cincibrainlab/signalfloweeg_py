import logging
from rich.console import Console
from rich.table import Table

from signalfloweeg.portal.db_connection import get_session

import signalfloweeg.portal.models as models


def generate_database_summary():
    """
    Generates a summary of the database tables and records.

    Args:
        session (sqlalchemy.orm.Session): The database session.

    Returns:
        dict: A dictionary containing the table names and record counts.
    """
    with get_session() as session:
        base_tables = models.Base.metadata.tables

        # Get the number of records in each table
        record_counts = {}
        for table in base_tables.values():
            record_count = session.query(table).count()
            record_counts[table.name] = record_count

        console = Console()
        table = Table(title="Database Summary")
        table.add_column("Table", style="cyan", no_wrap=True)
        table.add_column("Records", style="green", justify="right")

        for table_name, record_count in record_counts.items():
            table.add_row(table_name, str(record_count))

        console.print(table)



def drop_all_tables():
    success = False
    try:
        with get_session() as session:
            # disable foreign key constraint
            session.execute("SET CONSTRAINTS ALL DEFERRED;")
            session.commit()

            logging.info("Dropping all tables...")
            models.Base.metadata.drop_all(bind=session.get_bind())

            # enable foreign key constraint
            session.execute("SET CONSTRAINTS ALL IMMEDIATE;")
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
