
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine)
measurement_table = Base.classes.measurement
station_table = Base.classes.station
session = Session(bind=engine)


app = Flask(__name__)


@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    recent_date = session.query(measurement_table.date).order_by(measurement_table.date.desc()).first()
    latest_date = dt.datetime.strptime(str(recent_date), "('%Y-%m-%d',)").date()
    query_date = latest_date - dt.timedelta(days=365)
    precipitation = session.query(measurement_table.date, measurement_table.prcp).filter(measurement_table.date >= query_date).all()
    session.close()
    return jsonify([{date: prcp} for date, prcp in precipitation])

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_q = session.query(
        station_table.id, station_table.station, station_table.name, station_table.latitude,
        station_table.longitude, station_table.elevation
    ).all()
    session.close()
    return jsonify([{
        "id": id,
        "station": station,
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "elevation": elevation
    } for id, station, name, latitude, longitude, elevation in station_q])

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    recent_date = session.query(measurement_table.date).order_by(measurement_table.date.desc()).first()
    latest_date = dt.datetime.strptime(str(recent_date), "('%Y-%m-%d',)").date()
    query_date = latest_date - dt.timedelta(days=365)
    most_active = session.query(
        measurement_table.station, measurement_table.date, measurement_table.prcp, measurement_table.tobs
    ).filter(measurement_table.station == 'USC00519281', measurement_table.date >= query_date).all()
    session.close()
    return jsonify([{
        "station": station,
        "date": date,
        "prcp": prcp,
        "tobs": tobs
    } for station, date, prcp, tobs in most_active])

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    start_query = session.query(
        func.min(measurement_table.tobs), func.max(measurement_table.tobs), func.avg(measurement_table.tobs)
    ).filter(measurement_table.date >= start).all()
    session.close()
    return jsonify([{
        "start_date": start,
        "min": min,
        "max": max,
        "avg": avg
    } for min, max, avg in start_query])

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)
    start_query = session.query(
        func.min(measurement_table.tobs), func.max(measurement_table.tobs), func.avg(measurement_table.tobs)
    ).filter(measurement_table.date >= start, measurement_table.date <= end).all()
    session.close()
    return jsonify([{
        "start_date": start,
        "end_date": end,
        "min": min,
        "max": max,
        "avg": avg
    } for min, max, avg in start_query])

if __name__ == '__main__':
    app.run(debug=True)
