"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""
import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config
import os
import logging
from pymongo import MongoClient
from flask_restful import Resource, Api

###
# Globals
###

app = flask.Flask(__name__)
CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY
api = Api(app)


# Step 1: create a client object
# The environment variable DB_PORT_27017_TCP_ADDR is the IP of a linked docker
# container (IP of the database). Generally "DB_PORT_27017_TCP_ADDR" can be set
# to "localhost" or "127.0.0.1". This will not work when you run directly in
# your laptop.
#
client = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017)


# Step 2: connect to the DB
db = client.brevetsdb


class Times(Resource):
    def get(self):
        app.logger.debug("Times request")
        top = request.args.get('top')
        _items = db.brevetsdb.find()
        items = [item for item in _items]
        json = {'open_times': [], 'close_times': []}
        if top is None or top is "":
            top = len(items)
        else:
            top = int(top)
        for elem in items:
            json['open_times'].append(str(elem['open_times']))
            json['close_times'].append(str(elem['close_times']))
            top -= 1
            if top == 0:
                break
        return json


api.add_resource(Times, "/listAll", "/listAll/json")


class TimesCSV(Resource):
    def get(self):
        app.logger.debug("TimesCSV request")
        top = request.args.get('top')
        _items = db.brevetsdb.find()
        items = [item for item in _items]
        csv = ""
        if top is None or top is "":
            top = len(items)
        else:
            top = int(top)
        for elem in items:
            csv += str(elem['open_times']) + "," + (elem['close_times']) + "\n"
            top -= 1
            if top == 0:
                break
        return csv


api.add_resource(TimesCSV, "/listAll/csv")


class TimesOpen(Resource):
    def get(self):
        app.logger.debug("TimesOpen request")
        top = request.args.get('top')
        _items = db.brevetsdb.find()
        items = [item for item in _items]
        json = {'open_times': []}
        if top is None or top is "":
            top = len(items)
        else:
            top = int(top)
        for elem in items:
            json['open_times'].append(str(elem['open_times']))
            top -= 1
            if top == 0:
                break
        return json


api.add_resource(TimesOpen, "/listOpenOnly", "/listOpenOnly/json")


class TimesOpenCSV(Resource):
    def get(self):
        app.logger.debug("TimesOpenCSV request")
        top = request.args.get('top')
        _items = db.brevetsdb.find()
        items = [item for item in _items]
        csv = ""
        if top is None or top is "":
            top = len(items)
        else:
            top = int(top)
        for elem in items:
            csv += str(elem['open_times']) + ","
            top -= 1
            if top == 0:
                break
        return csv


api.add_resource(TimesOpenCSV, "/listOpenOnly/csv")


class TimesClose(Resource):
    def get(self):
        app.logger.debug("TimesClose request")
        top = request.args.get('top')
        _items = db.brevetsdb.find()
        items = [item for item in _items]
        json = {'close_times': []}
        if top is None or top is "":
            top = len(items)
        else:
            top = int(top)
        for elem in items:
            json['close_times'].append(str(elem['close_times']))
            top -= 1
            if top == 0:
                break
        return json


api.add_resource(TimesClose, "/listCloseOnly", "/listCloseOnly/json")


class TimesCloseCSV(Resource):
    def get(self):
        app.logger.debug("TimesCloseCSV request")
        top = request.args.get('top')
        _items = db.brevetsdb.find()
        items = [item for item in _items]
        csv = ""
        if top is None or top is "":
            top = len(items)
        else:
            top = int(top)
        for elem in items:
            csv += str(elem['close_times']) + ","
            top -= 1
            if top == 0:
                break
        return csv


api.add_resource(TimesCloseCSV, "/listCloseOnly/csv")


###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.route("/asdf")
def asdf():
    return flask.render_template(Times)


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404


@app.route("/button", methods=['POST'])
def _submit():
    app.logger.debug("Got button press")
    # app.logger.debug(request.form)
    _items = db.brevetsdb.find()
    items = [item for item in _items]
    try:
        request.form['submit']
        listvalues = list(request.form.listvalues())
        km_list = list(listvalues[4])
        names = list(listvalues[5])
        open_times = list(listvalues[6])
        close_times = list(listvalues[7])
        insert = False

        for i in range(len(km_list)):
            if km_list[i] != "":
                insert = True
                to_insert = {
                    'km': km_list[i],
                    'names': names[i],
                    'open_times': open_times[i],
                    'close_times': close_times[i]
                }
                db.brevetsdb.insert_one(to_insert)
        if not insert:
            flask.flash(u"ERROR: Please enter a distance", "error")
        return flask.redirect("/")

    except KeyError:
        if len(items) == 0:
            flask.flash(u"ERROR: Please submit a distance", "error")
            return flask.redirect("/")
        return flask.render_template('display.html', items=items)

    return flask.redirect("/")


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############


@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    km = request.args.get('km', 999, type=float)
    date = request.args.get('date')
    time = request.args.get('time')
    ar = arrow.get(date + ' ' + time + ':00')
    brevet = request.args.get('brevet')
    open_time = acp_times.open_time(km, int(brevet), ar)
    close_time = acp_times.close_time(km, int(brevet), ar)
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)

#############


app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0", debug=True)
