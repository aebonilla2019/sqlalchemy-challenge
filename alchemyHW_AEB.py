import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from flask import Flask, jsonify
import numpy as np
import re
import datetime as dt



engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
app = Flask(__name__)



# Flask Routes


@app.route("/")
def welcome():
    """List all available API routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/date1/start-date(yyyyMMdd)<br/>"
        f"/api/v1.0/date2/start-date(yyyyMMdd)/end-date(yyyyMMdd)"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    prcp_session = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    prcp_data = {}
    for date, prcp in prcp_session:
        prcp_data.setdefault(date,[]).append(prcp)

    return jsonify(prcp_data)



@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    station_results = session.query(Station.name).all()

    session.close()

    station_names = list(np.ravel(station_results))

    return jsonify(station_names)    


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    one_year_ago_date = str(dt.date.fromisoformat(last_date) - dt.timedelta(days=365))

    tobs_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago_date).all()

    session.close()

    tobs_data = {}
    for date, tobs in tobs_results:
        tobs_data.setdefault(date,[]).append(tobs)

    return jsonify(tobs_data)


@app.route("/api/v1.0/date1/<start>")
def range1(start):
    start_date = '{0}-{1}-{2}'.format(*re.match(r"(....)(..)(..)", start).groups())

    session = Session(engine)

    tobs_stats = session.query(
                    func.min(Measurement.tobs), 
                    func.avg(Measurement.tobs), 
                    func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start_date).all()

    session.close()

    return jsonify(tobs_stats)


@app.route("/api/v1.0/date2/<start>/<end>")
def range2(start, end):
    start_date = '{0}-{1}-{2}'.format(*re.match(r"(....)(..)(..)", start).groups())
    end_date = '{0}-{1}-{2}'.format(*re.match(r"(....)(..)(..)", end).groups())

    session = Session(engine)

    tobs_range_stat = session.query(func.min(Measurement.tobs), 
                    func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start_date).\
                    filter(Measurement.date <= end_date).all()

    session.close()

    return jsonify(tobs_range_stat)



if __name__ == '__main__':
    app.run(debug=True)