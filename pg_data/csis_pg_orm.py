from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
import subprocess
from config.config import configs

Base = automap_base()

if configs['test']:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/scorecard')
else:
    try:
        database_url = subprocess.check_output(
            'heroku config:get DATABASE_URL -a zircoa-preweigh', shell=True).decode('utf-8')
    except:
        print("Heroku call failed. Check that Heroku toolbelt is installed")
    engine = create_engine(database_url)

Base.prepare(engine, reflect=True)

Batch = Base.classes.summary_report_batch
TestPass = Base.classes.summary_report_testpasspercent
MeasurementMean = Base.classes.summary_report_measurementmean
MeasurementCount = Base.classes.summary_report_measurementcount
PGSummary = Base.classes.summary_report_summary

PGSession = sessionmaker(bind=engine)