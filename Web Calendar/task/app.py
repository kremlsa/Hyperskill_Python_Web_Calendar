from flask_restful import Api , Resource
from flask_restful import reqparse
from flask_restful import inputs
import json
import datetime
from flask import request
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sys
from flask_restful import fields , marshal_with
from flask import abort

resource_fields = {
    'id': fields.Integer,
    'event':   fields.String,
    'date':    fields.DateTime(dt_format='iso8601')
}


class GetResource(Resource):
    @marshal_with(resource_fields)
    def get(self):
        return get_event()


class GetByIdResource(Resource):
    @marshal_with(resource_fields)
    def get(self, event_id):
        event_ = get_by_id(event_id)
        if event_ is None:
            abort(404, "The event doesn't exist!")
        return event_


class DeleteResource(Resource):
     def delete(self, event_id):
        event_ = get_by_id(event_id)
        if event_ is None:
            abort(404, "The event doesn't exist!")
        else:
            delete_event(event_)
            return { "message": "The event has been deleted!"}


class GetAllResource(Resource):
    @marshal_with(resource_fields)
    def get(self):
        start_ = request.args.get('start_time')
        end_ = request.args.get('end_time')
        if start_ is None:
            return get_all_events()
        return get_range_events(start_, end_)


class PostResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'event',
        type=str,
        help="The event name is required!",
        required=True
    )
    parser.add_argument(
        'date',
        type=inputs.date,
        help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
        required=True
    )

    def post(self):
        args = self.parser.parse_args()
        resp = {"message": "The event has been added!", "event": args['event'], "date": args['date'].strftime("%Y-%m-%d")}
        json_ = json.dumps(resp)
        json_resp = json.loads(json_)
        add_event(args['event'], args['date'])
        return json_resp

def delete_event(event_):
    db.session.delete(event_)
    db.session.commit()

def get_by_id(id_):
    id_ = int(id_)
    event_ = Event.query.filter(Event.id == id_).first()
    print(event_)
    return event_


def add_event(event_, date_):
    global db
    event = Event(event=event_, date=date_)
    db.session.add(event)
    db.session.commit()


def get_all_events():
    events_ = Event.query.all()
    return events_


def get_event():
    events_ = Event.query.filter(Event.date == datetime.date.today()).all()
    return events_

def get_range_events(start_, end_):
    events_ = Event.query.filter(Event.date.between(start_, end_)).all()
    return events_


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)


db.create_all()
api = Api(app)
api.add_resource(GetResource, '/event/today')
api.add_resource(GetByIdResource, '/event/<int:event_id>')
api.add_resource(GetAllResource, '/event')
api.add_resource(PostResource, '/event')
api.add_resource(DeleteResource, '/event/<int:event_id>')

# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
