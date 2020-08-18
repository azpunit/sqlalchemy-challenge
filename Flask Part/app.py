import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

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
        f"/api/v1.0/start%20date<br/>"
        f"/api/v1.0/start%20date/end%20date"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of measurement data including the date and the precipitation"""
    # Query all dates and precipitation values
    results = session.query(Measurement.date, Measurement.prcp).\
                           filter(Measurement.prcp != " ").\
                           filter(Measurement.date >= '2016-08-23').\
                           order_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of dates and precipitaiton values
    dates_and_precipitation_values = []
    for date, precipitation in results:
        measurement_dict = {}
        measurement_dict[date] = precipitation
        dates_and_precipitation_values.append(measurement_dict)

    return jsonify(dates_and_precipitation_values)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    station_query = session.query(Measurement.station).\
                    group_by(Measurement.station).\
                    order_by(func.count(Measurement.station).desc()).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station_query))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def temperature_observations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all temperatures observations"""
    # Query all temperature observations
    temperature_observations_query = session.query(Measurement.tobs).\
                                     filter(Measurement.station == "USC00519281").\
                                     filter(Measurement.date >= '2016-08-23').\
                                     order_by(Measurement.date).all()

    session.close()

    # Convert list of tuples into normal list
    all_temperature_observations = list(np.ravel(temperature_observations_query))

    return jsonify(all_temperature_observations)


# Create our session (link) from Python to the DB
session = Session(engine)

# Query all temperature parameters
temperature_parameters = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
results = session.query(*temperature_parameters).\
                        group_by(Measurement.date).\
                        order_by(Measurement.date).all()

session.close()

temperature_parameters_list = []
for date, temperature_minimum, temperature_average, temperature_maximum in results:
    temperature_parameters_dict = {}
    temperature_parameters_dict["date"] = date
    temperature_parameters_dict["minimum temperature"] = temperature_minimum
    temperature_parameters_dict["average temperature"] = temperature_average
    temperature_parameters_dict["maximum temperature"] = temperature_maximum
    temperature_parameters_list.append(temperature_parameters_dict)

@app.route("/api/v1.0/<start>")
def from_start_date_to_august_2017(start):
    """Start date until 2017-08-23 or a 404 if not."""

    canonicalized = start.replace(" ", "").lower()
    for start_date in temperature_parameters_list:
        search_date = start_date["date"].replace(" ", "").lower()

        all_dates_after_start_date = [multiple_dates for multiple_dates in temperature_parameters_list if multiple_dates["date"] >= search_date]

        if search_date == canonicalized:
            return jsonify(all_dates_after_start_date)

    return jsonify({"error": f"{start} not found."}), 404

@app.route("/api/v1.0/<start>/<end>")
def from_start_date_to_end_date(start, end):
    """Start date until end date or a 404 if not."""

    first_canonicalized = start.replace(" ", "").lower()
    second_canonicalized = end.replace(" ", "").lower()
    first_search_date = start.replace(" ", "").lower()
    second_search_date = end.replace(" ", "").lower() 
    all_dates_between_start_date_and_end_date = [multiple_dates for multiple_dates in temperature_parameters_list if multiple_dates["date"
                                                ] >= first_search_date and multiple_dates["date"] <= second_search_date]
        
    if first_search_date == first_canonicalized and second_search_date == second_canonicalized:
        return jsonify(all_dates_between_start_date_and_end_date)

    return jsonify({"error": f"{start} and {end} not found."}), 404

if __name__ == '__main__':
    app.run(debug=True)

# TO RUN MY APP.PY FILE
# 1. cd to the "Flask Part" Folder
# 2. conda activate PythonData 
# 3. run in terminal: export FLASK_ENV=developement
# 4. run in terminal: export FLASK_DEBUG=1
# 5. run in terminal: python3 -m flask run
