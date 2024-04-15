import logging
from signalfloweeg.portal.models import Base
import signalfloweeg.portal.models as models
from signalfloweeg.portal.sessionmaker import (
    get_engine_and_session,
    generate_database_summary
)
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
