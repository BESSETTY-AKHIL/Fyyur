#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import Venue, Artist, Show, db
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format = "EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format = "EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)


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
  locations = Venue.query.distinct(Venue.city, Venue.state).all()
  data = [dict(city=location.city,
                state=location.state,
                venues=[dict(id=venue.id,
                              name=venue.name
                              ) for venue in Venue.query.filter(Venue.city == location.city, Venue.state == location.state).all()]
                	) for location in locations]
  return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  response = {
    'count': len(venues),
    'data': [dict(name=venue.name, id=venue.id) for venue in venues]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()
    shows = Show.query.filter_by(venue_id=venue_id).all()
    past_shows = Show.query.filter(
        Show.start_time < datetime.now(), Show.venue_id == venue_id).all()
    upcoming_shows = Show.query.filter(
        Show.start_time > datetime.now(), Show.venue_id == venue_id).all()

    if upcoming_shows:
      upcoming_show = [dict(
      artist_id=show.artist_id,
      artist_name=Artist.query.filter_by(id=show.artist_id).first().name,
      artist_image_link=Artist.query.filter_by(
          id=show.artist_id).first().image_link,
      start_time=format_datetime(str(show.start_time))
    ) for show in shows]
    else:
      upcoming_show = []

    if past_shows:
      past_show = [dict(
      artist_id=show.artist_id,
      artist_name=Artist.query.filter_by(id=show.artist_id).first().name,
      artist_image_link=Artist.query.filter_by(
          id=show.artist_id).first().image_link,
      start_time=format_datetime(str(show.start_time))
    ) for show in shows]
    else:
      past_show = []

    # data for given venue
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "address": venue.address,
        "facebook_link": venue.facebook_link,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_show,
        "upcoming_shows": upcoming_show,
        "past_shows_count": len(past_show),
        "upcoming_shows_count": len(upcoming_show),
    }
    return render_template('pages/show_venue.html', venue=data)
#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  facebook_link = request.form['facebook_link']
  image_link = request.form['image_link']

  try:
    venue = Venue(
      name=name,
      city=city,
      state=state,
      address=address,
      phone=phone,
      image_link=image_link,
      facebook_link=facebook_link,
      genres=genres
    )
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' +
          request.form['name'] + ' could not be listed.')

  finally:
    db.session.close()
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  response={
    'count': len(artists),
    'data':[dict(name=artist.name, id=artist.id) for artist in artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first()
    shows = Show.query.filter_by(artist_id=artist_id).all()
    past_shows =  Show.query.filter(Show.start_time < datetime.now(),Show.artist_id == artist_id).all()
    upcoming_shows = Show.query.filter(Show.start_time > datetime.now(),Show.artist_id == artist_id).all()

    if upcoming_shows:
      upcoming_show = [dict(
      venue_id = show.venue_id,
      venue_name= Venue.query.filter_by(id=show.venue_id).first().name,
      venue_image_link= Venue.query.filter_by(id=show.venue_id).first().image_link,
      start_time= format_datetime(str(show.start_time))
    ) for show in shows]
    else:
      upcoming_show = []

    if past_shows:
      past_show = [dict(
      venue_id = show.venue_id,
      venue_name= Venue.query.filter_by(id=show.venue_id).first().name,
      venue_image_link= Venue.query.filter_by(id=show.venue_id).first().image_link,
      start_time= format_datetime(str(show.start_time))
    ) for show in shows]
    else:
      past_show = []
    
    # data for given artist
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_show,
        "upcoming_shows": upcoming_show,
        "past_shows_count": len(past_show),
        "upcoming_shows_count": len(upcoming_show),
    }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.process_data(artist.name)
  form.city.process_data(artist.city)
  form.state.process_data(artist.state)
  form.phone.process_data(artist.phone)
  artist = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }
  
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)
  
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)

  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.facebook_link =  request.form['facebook_link']
    artist.image_link =  request.form['image_link']
    artist.website =  request.form['website']
    artist.seeking_description =  request.form['seeking_description']
    artist.seeking_venue = True if request.form['seeking_venue'] == 'Yes' else False 

    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')

  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.process_data(venue.name)
  form.city.process_data(venue.city)
  form.state.process_data(venue.state)
  form.phone.process_data(venue.phone)
  venue = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "address":venue.address,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)

  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres') 
    venue.address = request.form.getlist('address')
    venue.facebook_link =  request.form['facebook_link']
    venue.image_link =  request.form['image_link']
    venue.website =  request.form['website']
    venue.seeking_description =  request.form['seeking_description']
    venue.seeking_talent = True if request.form['seeking_talent'] == 'Yes' else False 

    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')

  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  facebook_link =  request.form['facebook_link']
  image_link =  request.form['image_link']

  try:
    artist = Artist(
      name=name,
      city=city,
      state=state,
      phone=phone,
      genres=genres,
      image_link=image_link,
      facebook_link=facebook_link,
    )
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

  finally:
    db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  get_shows = Show.query.all()
  data = [dict(venue_id = show.venue_id,
  venue_name= Venue.query.get(show.venue_id).name,
  artist_name= Artist.query.get(show.artist_id).name,
  artist_image_link= Artist.query.get(show.artist_id).image_link,
  artist_id = show.artist_id,
  start_time =format_datetime(str(show.start_time))
   ) for show in get_shows]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']
  try:
    show = Show(
      artist_id=artist_id,
      venue_id=venue_id,
      start_time=start_time
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
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
