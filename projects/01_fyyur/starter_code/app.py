#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import config
from flask_migrate import Migrate
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String)

    children = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))

    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String())

    children = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'Show'

    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)

    id = db.Column(db.Integer, primary_key=True)
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  local = []
  venues = Venue.query.all()                                            #get data from database
  locale = Venue.query.distinct(Venue.city, Venue.state).all()          #get unique city and state
  for location in locale:
    local.append({
      "city": location.city,
      "state": location.state,
      "venues": [{
        "id": venue.id,
        "name": venue.name,
      } for venue in venues if
        venue.city == location.city and venue.state == location.state]  #allocate venue to their city and state
    })
  
  return render_template('pages/venues.html', areas=local);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  data = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()           #get the data that match the seach_term
  count = len(data)                                                                       #count the amount of result get by the query
  result={
    "count": count,
    "data": data,
  }

  return render_template('pages/search_venues.html', results=result, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  real_data = Venue.query.get(venue_id)                                                 #real_data is the information from the database corresponding to the venue_id 
  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).filter(
    Show.venue_id == venue_id,
    Show.artist_id == Artist.id,
    Show.start_time < datetime.now()
  ).all()
  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).filter(        #get the show information and seperate it into past and upcoming by datetime
    Show.venue_id == venue_id,
    Show.artist_id == Artist.id,
    Show.start_time > datetime.now()
  ).all()

  real_venue = {
    "id": real_data.id,
    "name": real_data.name,
    "genres": real_data.genres,
    "address": real_data.address,
    "city": real_data.city,
    "state": real_data.state,
    "phone": real_data.phone,
    "website": real_data.website,
    "facebook_link": real_data.facebook_link,
    "seeking_talent": real_data.seeking_talent,
    "seeking_description": real_data.seeking_description,
    "image_link": real_data.image_link,
    "past_shows": [{
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time
    } for artist, show in past_shows],
    "upcoming_shows": [{
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time
    } for artist, show in upcoming_shows],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  return render_template('pages/show_venue.html', venue=real_venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      new_venue = Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        genres = form.genres.data,
        facebook_link = form.facebook_link.data,
        image_link = form.image_link.data,
        website = form.website_link.data,
        seeking_talent = form.seeking_talent.data,
        seeking_description = form.seeking_description.data
      )
      db.session.add(new_venue)
      db.session.commit()
      flash('Venue ' + form.name.data + ' was successfully listed!')
    except ValueError as e:
      print(e)
      db.session.rollback()
      flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
    finally:
      db.session.close()
  else:
    message = []
    for field, errors in form.errors.items():
      message.append(field + ': (' + '|'.join(errors) + ')')
      flash(message)
  return redirect(url_for('index'))

  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('The Venue has been successfully deleted!')
    return redirect(url_for('index'))
  except ValueError as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Venue ' + form.name.data + ' was not deleted.')
  finally:
    db.session.close
    
  return none
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  real_artists = Artist.query.all()

  return render_template('pages/artists.html', artists=real_artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  data = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  count = len(data)
  result={
    "count": count,
    "data": data,
  }
  
  return render_template('pages/search_artists.html', results=result, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  real_data = Artist.query.get(artist_id)                                                #real_data is the information from the database corresponding to the venue_id 
  
  past_shows = db.session.query(Venue, Show).join(Show).join(Artist).filter(
    Show.venue_id == Venue.id,
    Show.artist_id == artist_id,
    Show.start_time < datetime.now()
  ).all()
  past_shows_count = len(past_shows)

  upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).filter(
    Show.venue_id == Venue.id,
    Show.artist_id == artist_id,
    Show.start_time > datetime.now()
  ).all()
  upcoming_shows_count = len(upcoming_shows)

  real_artist = {
    "id": real_data.id,
    "name": real_data.name,
    "genres": real_data.genres,
    "city": real_data.city,
    "state": real_data.state,
    "phone": real_data.phone,
    "facebook_link": real_data.facebook_link,
    "website": real_data.website_link,
    "seeking_venue": real_data.seeking_venue,
    "seeking_description": real_data.seeking_description,
    "image_link": real_data.image_link,
    "past_shows": [{
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time
    } for venue, show in past_shows],
    "upcoming_shows": [{
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time
    } for venue, show in upcoming_shows],
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  return render_template('pages/show_artist.html', artist=real_artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  real_data = Artist.query.get(artist_id)   
  form = ArtistForm(obj=real_data)

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=real_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      update_artist = Artist.query.get(artist_id)             

      update_artist.name = form.name.data,
      update_artist.city = form.city.data,
      update_artist.state = form.state.data,
      update_artist.phone = form.phone.data,

      for genre in range(len(form.genres.data)):
        update_artist.genres = form.genres.data

      update_artist.facebook_link = form.facebook_link.data,
      update_artist.website_link = form.website_link.data,
      update_artist.image_link = form.image_link.data,
      update_artist.seeking_venue = form.seeking_venue.data
      update_artist.seeking_description = form.seeking_description.data

      db.session.commit()
      flash('Artist ' + form.name.data +' updated!')
    except ValueError as e:
      print(e)
      db.session.rollback()
      flash('An error occur, please try again')
    finally:
      db.session.close()
  else:
    message = []
    for field, errors in form.errors.items():
      message.append(field + ': (' + '|'.join(errors) + ')')
      flash(message)
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  real_data = Venue.query.get(venue_id)   
  form = VenueForm(obj=real_data)                                             

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=real_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      update_venue = Venue.query.get(venue_id)  
  
      update_venue.name = form.name.data
      update_venue.city = form.city.data
      update_venue.state = form.state.data
      update_venue.address = form.address.data
      update_venue.phone = form.phone.data

      for genre in range(len(form.genres.data)):
        update_venue.genres = form.genres.data

      update_venue.facebook_link = form.facebook_link.data
      update_venue.image_link = form.image_link.data
      update_venue.website = form.website_link.data
      update_venue.seeking_talent = form.seeking_talent.data
      update_venue.seeking_description = form.seeking_description.data

      db.session.commit()
      flash('Venue ' + form.name.data +' updated!')
    except ValueError as e:
      print(e)
      db.session.rollback()
      flash('An error occur, please try again')
    finally:
      db.session.close()
  else:
    message = []
    for field, errors in form.errors.items():
      message.append(field + ': (' + '|'.join(errors) + ')')
      flash(message)

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form, meta={'csrf': False})
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  if form.validate():
    try:
      new_artist = Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        genres = form.genres.data,
        facebook_link = form.facebook_link.data,
        image_link = form.image_link.data,
        seeking_venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data
      )
      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + form.name.data + ' was successfully listed!')
    except ValueError as e:
      print(e)
      db.session.rollback()
      flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    finally:
      db.session.close()
  else:
    message = []
    for field, errors in form.errors.items():
      message.append(field + ': (' + '|'.join(errors) + ')')
      flash(message)
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  all_show = []
  real_show = Show.query.join(Venue, Show.venue_id == Venue.id).join(Artist, Artist.id == Show.artist_id).all()
  for show in real_show:
    i_shows = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    }
    all_show.append(i_shows)
  
  return render_template('pages/shows.html', shows=all_show)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      new_show = Show(
        start_time = form.start_time.data,
        artist_id = form.artist_id.data,
        venue_id = form.venue_id.data
      )
      db.session.add(new_show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
    except ValueError as e:
      print(e)
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()
  else:
    message = []
    for field, errors in form.errors.items():
      message.append(field + ': (' + '|'.join(errors) + ')')
      flash(message)
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
