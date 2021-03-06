import logging
from logging.handlers import TimedRotatingFileHandler
from flask import Flask
from flask_bootstrap import Bootstrap, StaticCDN
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension

from airbrake import Airbrake, AirbrakeHandler


app = Flask(__name__)
app.config.from_object('config.Configuration')
Bootstrap(app)

# use our own bootstrap theme
app.extensions['bootstrap']['cdns']['bootstrap'] = StaticCDN()

db = SQLAlchemy(app)

toolbar = DebugToolbarExtension(app)


if not app.debug:
    timedFileHandler = TimedRotatingFileHandler(app.config['LOGFILE'], when='midnight', backupCount=100)
    timedFileHandler.setLevel(logging.DEBUG)

    loglogger = logging.getLogger('werkzeug')
    loglogger.setLevel(logging.DEBUG)
    loglogger.addHandler(timedFileHandler)
    app.logger.addHandler(timedFileHandler)

    airbrakelogger = logging.getLogger('airbrake')

    # Airbrake
    airbrake = Airbrake(
        project_id=app.config['AIRBRAKE_ID'],
        api_key=app.config['AIRBRAKE_KEY']
    )
    # ugly hack to make this work for out errbit
    airbrake._api_url = "http://errbit.awesomepeople.tv/api/v3/projects/{}/notices".format(airbrake.project_id)

    airbrakelogger.addHandler(
        AirbrakeHandler(airbrake=airbrake)
    )
    app.logger.addHandler(
        AirbrakeHandler(airbrake=airbrake)
    )