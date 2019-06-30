from flask import Flask, render_template, request, redirect, jsonify
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
from flask import make_response, flash, url_for
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"

# Connect to the Database to create sessions
engine = create_engine('sqlite:///winecatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data.decode('utf-8')
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = ' '
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 300px; height: 300px;
                    border-radius: 150px;-webkit-border-radius: 150px;
                    -moz-border-radius: 150px;"> '''
    flash("You are now logged in as %s" % login_session['username'])
    return output

# User Helper Functions


def createUser(login_session):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
                           params={'token': access_token},
                           headers={'content-type':
                                    'application/x-www-form-urlencoded'})
    result = getattr(revoke, 'status_code')
    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Disconnected.'), 200)
        redirect('/regions')
        flash("You have successfully logged out")
        return redirect('/regions')
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Use to completely clear your login session if logging out does not work
@app.route('/clearSession')
def clear_session():
    login_session.clear()
    return "session cleared"

# Show all regions
@app.route('/')
@app.route('/regions')
def showAllRegions():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    regions = session.query(Region).order_by(asc(Region.name))
    if 'username' not in login_session:
        return render_template('publicAllRegions.html', regions=regions)
    else:
        return render_template('allRegions.html', regions=regions)

# Create a new Region
@app.route('/region/new/', methods=['GET', 'POST'])
def newRegion():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newRegion = Region(name=request.form['name'],
                           user_id=login_session['user_id'])
        session.add(newRegion)
        flash('New Region %s Succesfully Created!' % newRegion.name)
        session.commit()
        return redirect(url_for('showAllRegions'))
    else:
        return render_template('newRegion.html')

# Edit Region
@app.route('/region/<int:region_id>/edit/', methods=['GET', 'POST'])
def editRegion(region_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    editedRegion = session.query(Region).filter_by(id=region_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedRegion.user_id != login_session['user_id']:
        flash('''You are not allowed to edit this region.
              Create your own region in order to edit''')
        return redirect('/regions')
    if request.method == 'POST':
        if request.form['name']:
            editedRegion.name = request.form['name']
        session.add(editedRegion)
        session.commit()
        flash('Succesfully Edited %s Region!' % editedRegion.name)
        return redirect(url_for('showAllRegions'))
    else:
        return render_template('editRegion.html', region=editedRegion)

# Delete Region
@app.route('/region/<int:region_id>/delete/', methods=['GET', 'POST'])
def deleteRegion(region_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    deletedRegion = session.query(Region).filter_by(id=region_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if deletedRegion.user_id != login_session['user_id']:
        flash('''You are not allowed to delete this region.
              Create your own region in order to delete''')
        return redirect('/regions')
    if request.method == 'POST':
        session.delete(deletedRegion)
        flash('%s Succesfully Deleted!' % deletedRegion.name)
        session.commit()
        return redirect(url_for('showAllRegions'))
    else:
        return render_template('deleteRegion.html', region=deletedRegion)

# Show wines in region
@app.route('/region/<int:region_id>/')
@app.route('/region/<int:region_id>/wines')
def showWines(region_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    region = session.query(Region).filter_by(id=region_id).one()
    creator = getUserInfo(region.user_id)
    wines = session.query(Wine).filter_by(region_id=region_id).all()
    if 'username' not in login_session or \
            creator.id != login_session['user_id']:
        return render_template('publicAllWines.html',
                               wines=wines, region=region, creator=creator)
    else:
        return render_template('allWines.html',
                               wines=wines, region=region, creator=creator)

# Create new wine
@app.route('/region/<int:region_id>/wine/new/', methods=['GET', 'POST'])
def newWine(region_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    region = session.query(Region).filter_by(id=region_id).one()
    if login_session['user_id'] != region.user_id:
        flash('''You are not allowed to add a new wine
              Create your own region to add wines.''')
        return redirect(url_for('showWines', region_id=region_id))
    if request.method == 'POST':
        newWine = Wine(name=request.form['name'],
                       description=request.form['description'],
                       price=request.form['price'], region_id=region_id,
                       user_id=login_session['user_id'])
        session.add(newWine)
        session.commit()
        flash('New Wine %s Successfully Created!' % (newWine.name))
        return redirect(url_for('showWines', region_id=region_id))
    else:
        return render_template('newWine.html', region_id=region_id)

# Edit wine
@app.route('/region/<int:region_id>/wine/<int:wine_id>/edit/',
           methods=['GET', 'POST'])
def editWine(region_id, wine_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    region = session.query(Region).filter_by(id=region_id).one()
    editedWine = session.query(Wine).filter_by(id=wine_id).one()
    if login_session['user_id'] != region.user_id:
        flash('''You are not allowed to edit this wine
              Create your own region to edit wines.''')
        return redirect(url_for('showWines', region_id=region_id))
    if request.method == 'POST':
        if request.form['name']:
            editedWine.name = request.form['name']
        if request.form['description']:
            editedWine.description = request.form['description']
        if request.form['price']:
            editedWine.price = request.form['price']
        session.add(editedWine)
        session.commit()
        flash('Wine Succesfully Edited!')
        return redirect(url_for('showWines', region_id=region_id))
    else:
        return render_template('editWine.html',
                               region_id=region_id, wine_id=wine_id,
                               wine=editedWine)

# Delete Wine
@app.route('/region/<int:region_id>/wine/<int:wine_id>/delete/',
           methods=['GET', 'POST'])
def deleteWine(region_id, wine_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    region = session.query(Region).filter_by(id=region_id).one()
    wineToDelete = session.query(Wine).filter_by(id=wine_id).one()
    if login_session['user_id'] != region.user_id:
        flash('''You are not allowed to delete this wine
              Create your own region to delete wines.''')
        return redirect(url_for('showWines', region_id=region_id))
    if request.method == 'POST':
        session.delete(wineToDelete)
        session.commit()
        flash('Wine Succesfully Deleted!')
        return redirect(url_for('showWines', region_id=region_id))
    else:
        return render_template('deleteWine.html',
                               region_id=region_id, wine_id=wine_id,
                               wine=wineToDelete)


# Show wine description
@app.route('/region/<int:region_id>/wine/<int:wine_id>/info/')
def showInfo(region_id, wine_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    region = session.query(Region).filter_by(id=region_id).one()
    wine = session.query(Wine).filter_by(id=wine_id).one()
    return render_template('showInfo.html', wine=wine, region=region)


# JSON APIs to view Categories Information
@app.route('/regions/JSON')
def regionsJSON():
    regions = session.query(Region).all()
    return jsonify(regions=[r.serialize for r in regions])


@app.route('/region/<int:region_id>/wines/JSON')
def winesJSON(region_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    wines = session.query(Wine).filter_by(region_id=region_id).all()
    return jsonify(wines=[r.serialize for r in wines])


@app.route('/region/<int:region_id>/wine/<int:wine_id>/JSON')
def wineJSON(region_id, wine_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    wineInfo = session.query(Wine).filter_by(id=wine_id).one()
    return jsonify(wineInfo=wineInfo.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
