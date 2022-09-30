# Import Dependencies
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Set up the database

engine= create_engine("sqlite:///../Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Create classes

Measurement = Base.classes.measurement
Station = Base.classes.station

# Set up flask

app = Flask(__name__)

# Design app

@app.route("/")
def welcome():
    return(
        f"Available Routes:<br>"
        f"Precipitation: /api/v1.0/precipitation<br>"
        f"List of Stations: /api/v1.0/stations<br>"
        f"Temperature for previous year: /api/v1.0/tobs<br>"
        f"Temperature stat from start date: /api/v1.0/<start><br>"
        f"Temperature stat from start to end dates: /api/v1.0/<start>/<end><br>"
    )

# Design precipitation route in app

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    select = [Measurement.date, Measurement.prcp]
    result = session.query(*select).all()
    session.close()

    precipitation = []
    for date, prcp in result:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

# Design station route in app

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    select = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    result = session.query(*select).all()
    session.close()

    stations = []
    for station, name, lat, lon, el in result:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)
    
    return jsonify(stations)

# Design tobs route in app

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    recentdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    mostrecent = dt.datetime.strptime(recentdate, '%Y-%m-%d')
    querydate = dt.date(mostrecent.year -1, mostrecent.month, mostrecent.day)
    select = [Measurement.date, Measurement.tobs]
    result = session.query(*select).filter(Measurement.date >= querydate).all()
    session.close()

    tobsall = []
    for date, tobs in result:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobsall.append(tobs_dict)
    
    return jsonify(tobsall)

# Design route for a specific start date in app

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    tobsall = []
    for min, max, avg in result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Max"] = max
        tobs_dict["Average"] = avg
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

# Design rote for specific start-end dates in app

@app.route("/api/v1.0/<start>/<end>")
def start_end_dates(start, end):
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()

    tobsall = []
    for min, max, avg in result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Max"] = max
        tobs_dict["Average"] = avg
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

if __name__ == "__main__":
    app.run(debug=True)