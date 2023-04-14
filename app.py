# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify,abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
class Show(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'))
    start_time = db.Column(db.DateTime,nullable=False)


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))

    genres = db.Column(db.String(), nullable=False)
    website_link = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(240))

    show_id = db.relationship('Show',backref="venue",lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    facebook_link = db.Column(db.String(120))

    website_link = db.Column(db.String(240))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(240))

    show_id = db.relationship('Show',backref="artist")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    list_of_venues = Venue.query.all()
    data = []

    for venue in list_of_venues:
        shows = Show.query.filter_by(venue_id=venue.id).all()
        new_venue = {'id': venue.id, 'name': venue.name, 'num_upcoming_shows': len(shows)}
        is_found = False
        for item in data:
            if item['city'] == venue.city and item['state'] == venue.state:
                item['venues'].append(new_venue)
                is_found = True

        if not is_found:
            data.append(
                {'city': venue.city, 'state': venue.state, 'venues': [new_venue]})

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    results = Venue.query.filter(Venue.name.like(
        f"%{request.form.get('search_term', '').lower()}%")).all()
    print(results)
    for i in range(len(results)):
        item = results[i]
        item = {'id': item.id, 'name': item.name, 'num_upcoming_shows': 0}

    response = {
        'count': len(results),
        'data': results
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()
    data = {'id':venue.id,'name':venue.name,'genres': [venue.genres.strip('{}')],'address': venue.address,'city':venue.city,'state': venue.state,'phone':venue.phone,'website': venue.website_link,'seeking_talent':venue.seeking_talent,'seeking_description': venue.seeking_description,'image_link': venue.image_link,'past_shows': [],'upcoming_shows':[],'past_shows_count': 0,'upcoming_shows_count': 0}

    shows = Show.query.filter_by(venue_id=venue_id).all()
    artist = Artist.query.filter_by()

    upcoming_shows = 0
    past_shows = 0
    for show in shows:
        artist = Artist.query.filter_by(id=show.artist_id).first()
        if show.start_time > datetime.now():
            upcoming_shows += 1
            data['upcoming_shows'].append({'artist_id': artist.id,'artist_name':artist.name,'artist_image_link': artist.image_link,'start_time': str(show.start_time)})
        else:
            past_shows += 1
            data['past_shows'].append({'artist_id': artist.id,'artist_name':artist.name,'artist_image_link': artist.image_link,'start_time': str(show.start_time)})

    data['past_shows_count'] = past_shows
    data['upcoming_shows_count'] = upcoming_shows

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()

    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    try:
        new_venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data, phone=form.phone.data, image_link=form.image_link.data,
                          facebook_link=form.facebook_link.data, genres=form.genres.data, website_link=form.website_link.data, seeking_talent=form.seeking_talent.data, seeking_description=form.seeking_description.data)
        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + form.name.data + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              form.name.data + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        show = Show.query.filter_by(venue_id=venue_id).first()
        venue = Venue.query.filter_by(id=venue_id).first()
        db.session.delete(venue)
        db.session.delete(show)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if not error:
        return jsonify({
            'deleted': True
        })
    else:
        abort(500)
#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = Artist.query.all()

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    results = Artist.query.filter(Artist.name.like(
        f"%{request.form.get('search_term')}%")).all()
    print(results)
    for i in range(len(results)):
        item = results[i]
        item = {'id': item.id, 'name': item.name, 'num_upcoming_shows': 0}

    print(results)
    response = {
        'count': len(results),
        'data': results
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first()
    data = {'id': artist_id,'name': artist.name,'genres': [artist.genres.strip('{}')],'city': artist.city,'state': artist.state,'phone': artist.phone,'seeking_venue': artist.seeking_venue,'image_link': artist.image_link,'upcoming_shows': [],'past_shows': [],'past_shows_count':0,'upcoming_shows_count':0}

    shows = Show.query.filter_by(artist_id=artist_id).all()

    upcoming_shows = 0
    past_shows = 0
    for show in shows:
        venue = Venue.query.filter_by(id=show.venue_id).first()
        if show.start_time > datetime.now():
            upcoming_shows += 1
            data['upcoming_shows'].append({'venue_id': venue.id,'venue_name':venue.name,'venue_image_link': venue.image_link,'start_time': str(show.start_time)})
        else:
            past_shows += 1
            data['past_shows'].append({'venue_id': venue.id,'venue_name':venue.name,'venue_image_link': venue.image_link,'start_time': str(show.start_time)})

    data['past_shows_count'] = past_shows
    data['upcoming_shows_count'] = upcoming_shows
    

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm(request.form)
    artist = Artist.query.filter_by(id=artist_id).first()
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    try:
        item = Artist.query.filter_by(id=artist_id).first()
        item.name = form.name.data
        item.city = form.city.data
        item.state = form.state.data
        item.phone = form.phone.data
        item.image_link = form.image_link.data
        item.genres = form.genres.data
        item.facebook_link = form.facebook_link.data
        item.website_link = form.website_link.data
        item.seeking_venue = form.seeking_venue.data
        item.seeking_description = form.seeking_description.data

        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).first()
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    try:
        venue = Venue.query.filter_by(id=venue_id).first()
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.image_link = form.image_link.data
        venue.facebook_link = form.facebook_link.data
        venue.genres = form.genres.data
        venue.website_link = form.website_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data

        db.session.commit()
    except:
        db.session.rollback()
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
    form = ArtistForm(request.form)

    try:
        new_artist = Artist(name=form.name.data, city=form.city.data, state=form.state.data, phone=form.phone.data, image_link=form.image_link.data, genres=form.genres.data,
                            facebook_link=form.facebook_link.data, website_link=form.website_link.data, seeking_venue=form.seeking_venue.data, seeking_description=form.seeking_description.data)
        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + form.name.data + ' was successfully listed!')
    except Exception as e:
        print(e)
        db.session.rollback()
        flash('An error occurred. Artist ' +
              form.name.data + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    all_shows = Show.query.all()
    data = []
    for item in all_shows:
        artist = Artist.query.filter_by(id=item.artist_id).first()
        venue = Venue.query.filter_by(id=item.venue_id).first()
        data.append({'venue_id': item.venue_id,'artist_id': item.artist_id,'artist_name': artist.name,'artist_image_link': artist.image_link,'start_time': str(item.start_time),'venue_name': venue.name})
        item.start_time = str(item.start_time)
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    print(form.start_time.data)
    try:
        new_show = Show(artist_id=int(form.artist_id.data),venue_id=int(form.venue_id.data),start_time=form.start_time.data)
        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')
    except Exception as e:
        print(e)
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
