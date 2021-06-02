import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct
from flask_cors import CORS

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite 
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")
conn = engine.connect()

# reflect an existing database into a new model
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)
# Print all of the classes mapped to the Base
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
cors = CORS(app)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


@app.route("/api/v1.0/precipitation")
def get_precipitation():
    retval = {}

    for row in session.query(Measurement).all():
        retval[row.date] = row.prcp
        
    return jsonify(retval)


@app.route("/api/v1.0/stations")
def get_stations():
    retval = []

    for row in session.query(Station).all():
        station = {
            "id": row.id,
            "station": row.station,
            "name": row.name,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "elevation": row.elevation,
        }
        retval.append(station)

    return jsonify({ "stations": retval })


@app.route("/api/v1.0/tobs")
def get_tobs():
    retval = []

    records = session.query(
        Station,
        Measurement,
        func.sum(Measurement.tobs)
    ).join(
        Measurement,
        Measurement.station == Station.station
    ).group_by(Measurement.station).all()

    for row in records:
        station = {
            "id": row.station.id,
            "station": row.station.station,
            "name": row.station.name,
            "latitude": row.station.latitude,
            "longitude": row.station.longitude,
            "elevation": row.station.elevation,
            "tobs": row[2],
        }
        retval.append(station)

    return jsonify({ "result": retval })


@app.route("/api/v1.0/<start>/<end>")
def get_temp_full(start, end):
    retval = []

    records = session.query(
        Station,
        Measurement,
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs),
    ).join(
        Measurement,
        Measurement.station == Station.station
    ).group_by(Measurement.station).all()

    for row in records:
        station = {
            "id": row.station.id,
            "station": row.station.station,
            "name": row.station.name,
            "latitude": row.station.latitude,
            "longitude": row.station.longitude,
            "elevation": row.station.elevation,
            "min": row[2],
            "max": row[3],
            "avg": row[4],
        }
        retval.append(station)

    return jsonify({ "result": retval })


@app.route("/api/v1.0/<start>")
def get_temp(start):
    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True, port=5001)
