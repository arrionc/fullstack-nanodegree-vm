from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Region, Wine, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Connect to the Database to create sessions
engine = create_engine('sqlite:///winecatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Show all regions
@app.route('/')
@app.route('/regions')
def showAllRegions():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    regions = session.query(Region).order_by(asc(Region.name))
    return render_template('allRegions.html', regions=regions)

# Show wines in region
@app.route('/region/<int:region_id>/')
@app.route('/region/<int:region_id>/wines')
def showWines(region_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    region = session.query(Region).filter_by(id=region_id).one()
    wines = session.query(Wine).filter_by(region_id=region_id).all()
    return render_template('allWines.html', wines=wines)

# Show wine description
@app.route('/region/<int:region_id>/wine/<int:wine_id>/info/')
def showInfo(region_id, wine_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    region = session.query(Region).filter_by(id=region_id).one()
    wine = session.query(Wine).filter_by(id=wine_id).one()
    print (wine.name)
    return render_template('showInfo.html', wine=wine)


    



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)