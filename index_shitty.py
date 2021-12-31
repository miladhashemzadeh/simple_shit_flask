from flask import Flask
from flask_restful import Resource, Api, abort, reqparse, marshal_with, fields
from flask_sqlalchemy import Model, SQLAlchemy, orm


def postAddToilet(toilet_post_args):
    toilet_post_args.add_argument("owner_id", type=int, help="owner_id is required", required=True)
    toilet_post_args.add_argument("lat", type=float, help="latitude is required", required=True)
    toilet_post_args.add_argument("lat", type=float, help="longitude is required", required=True)
    toilet_post_args.add_argument("city", type=str, help="city is required", required=True)
    toilet_post_args.add_argument("has_cost", type=bool, help="city is required", required=True)


def updateToilet(toilet_update_args):
    toilet_update_args.add_argument("owner_id", type=int)
    toilet_update_args.add_argument("lat", type=float)
    toilet_update_args.add_argument("lat", type=float)
    toilet_update_args.add_argument("city", type=str)
    toilet_update_args.add_argument("has_cost", type=bool)


def postAddOwner(owner_post_args):
    owner_post_args.add_argument("name", type=str, help="name is required", required=True)
    owner_post_args.add_argument("city", type=str, help="city is required", required=True)
    owner_post_args.add_argument("toilets", type=bool, help="toilets is not required", required=False)


def updateOwner(owner_update_args):
    owner_update_args.add_argument("name", type=str)
    owner_update_args.add_argument("city", type=str)
    owner_update_args.add_argument("toilets", type=str)


if __name__ == "__main__":
    SQLALCHEMY_CONFIG_KEY = "SQLALCHEMY_DATABASE_URI"
    DB_LOCATION = "sqlite:///shit.db"

    shitty_app = Flask(__name__)
    shitty_api = Api(shitty_app)
    shitty_app.config[SQLALCHEMY_CONFIG_KEY] = DB_LOCATION
    db = SQLAlchemy(shitty_app)


    # XXXModel are same tables in db
    class ToiletModel(db.Model):
        id = db.Column(db.INTEGER, primary_key=True)
        owner_id = db.Column(db.String(200), db.ForeignKey("owner_model.id"), nullable=False)
        lat = db.Column(db.REAL(30), nullable=False)
        lon = db.Column(db.REAL(30), nullable=False)
        city = db.Column(db.String(50), nullable=False)
        hasCost = db.Column(db.Boolean, nullable=False)


    class OwnerModel(db.Model):
        id = db.Column(db.INTEGER, primary_key=True)
        name = db.Column(db.String(200), nullable=True)
        city = db.Column(db.String(50), nullable=True)
        toilets = db.relationship('ToiletModel', uselist=True, backref="ToiletModel")


    # db.create_all()
    # --------------------------------
    toilet_post_args = reqparse.RequestParser()
    toilet_update_args = reqparse.RequestParser()
    postAddToilet(toilet_post_args)
    updateToilet(toilet_update_args)

    owner_post_args = reqparse.RequestParser()
    owner_update_args = reqparse.RequestParser()
    postAddOwner(owner_post_args)
    updateOwner(owner_update_args)
    # ----------------------------------
    toilet_fields = {
        'id': fields.Integer,
        'owner_id': fields.Integer,
        'lat': fields.Float,
        'lon': fields.Float,
        'city': fields.String,
        'has_cost': fields.Boolean,
    }
    owner_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'city': fields.String,
        'lat': fields.Float,
        'lon': fields.Float,
        'toilets': fields.String
    }


    # -----------------------toilet api
    class ToiletListApi(Resource):
        def get(self):
            tasks = ToiletModel.query.all()
            toilets = {}
            for task in tasks:
                toilets[task.id] = {"id": task.id, "owner_id": task.owner_id, "lat": task.lat, "lon": task.lon,
                                    "city": task.city, "has_cost": task.hasCost}
            return toilets


    class ToiletApi(Resource):

        @marshal_with(toilet_fields)
        def get(self, toilet_id):
            task = ToiletModel.query.filter_by(id=toilet_id).first()
            if not task:
                abort(404, message="there is no toilet by this id " + toilet_id)
            return {"id": task.id, "owner_id": task.owner_id, "lat": task.lat, "lon": task.lon,
                    "city": task.city, "has_cost": task.hasCost}

        @marshal_with(toilet_fields)
        def post(self, toilet_id):
            args = toilet_post_args.parse_args()
            task = ToiletModel.query.filter_by(id=toilet_id)
            if task:
                abort(409, message="id was taken before")
            toilet = ToiletModel(id=toilet_id, owner_id=args['owner_id'], lat=args['lat'], lon=args['lon'],
                                 city=args['city'], hasCost=args['has_cost'])
            db.session.add(toilet)
            db.session.commit()

        @marshal_with(toilet_fields)
        def update(self, toilet_id):
            # args = toilet_update_args.parse_args()
            task = ToiletModel.query.filter_by(id=toilet_id).first()
            if not task:
                abort(404, message="id was taken before")
            # better way is args check changed then update it

            db.session.commit()

        @marshal_with(toilet_fields)
        def delete(self, toilet_id):
            task = ToiletModel.query.filter_by(id=toilet_id).first()
            db.session.delete(task)
            db.session.commit()

    #-----------------------owner api
    class OwnerApi(Resource):
        @marshal_with(owner_fields)
        def get(self, owner_id):
            task = OwnerModel.query.filter_by(id=owner_id).first()
            if not task:
                abort(404, message="there is no owner by this id " + owner_id)
            return {"id": task.id, "owner_id": task.name, "city": task.city, "toilets": task.toilets}

        @marshal_with(owner_fields)
        def post(self, owner_id):
            args = owner_post_args.parse_args()
            task = OwnerModel.query.filter_by(id=owner_id)
            if task:
                abort(409, message="id was taken before")
            owner = OwnerModel(id=owner_id, name=args['name'], city=args['city'], toilets=args['toilets'])
            db.session.add(owner)
            db.session.commit()

        @marshal_with(owner_fields)
        def update(self, owner_id):
            # args = owner_update_args.parse_args()
            task = OwnerModel.query.filter_by(id=owner_id)
            if not task:
                abort(404, message="id was taken before")
            db.session.commit()

        @marshal_with(owner_fields)
        def delete(self, owner_id):
            task = OwnerModel.query.filter_by(id=owner_id).first()
            if not task:
                abort(404, message="owner was not found")
            db.session.delete(task)
            db.session.commit()

shitty_api.add_resource(ToiletApi, '/v1/toilets/<int:toilet_id>')
shitty_api.add_resource(ToiletListApi, '/v1/toilets/')
shitty_api.add_resource(OwnerApi, '/v1/owners/<int:owner_id>')
shitty_app.run(debug=True)
