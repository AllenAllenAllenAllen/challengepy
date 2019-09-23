from flask import Flask, request
from scraper import * # Web Scraping utility functions for Online Clubs with Penn.
from flask_pymongo import PyMongo
import json
from user import *

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/club_app"
mongo = PyMongo(app)


@app.route('/')
def main():
    return "Welcome to Penn Club Review!"

@app.route('/api')
def api():
    apis = ["GET /api/clubs", "POST /api/clubs", "GET /api/user/:username", "POST /api/favorite"]
    return json.dumps(apis)

@app.route("/api/clubs")
def clubs():
    resp = []
    for club in mongo.db.club.find({}, {"_id": 0}):
        resp.append(club)
    return json.dumps(resp)

@app.route("/api/clubs", methods=["POST"])
def create_club():
    form = request.get_json(force=True)
    if form is None:
        return "Invalid Club Info Format"
    try:
        assert("name" in form and isinstance(form["name"], str))
        assert("tags" in form and isinstance(form["tags"], list))
        assert("desc" in form and isinstance(form["desc"], str))
    except AssertionError:
        return "Invalid Club Info"
    mongo.db.club.update_one({"name": form["name"]}, {"$set": form}, upsert=True)
    return "OK"

@app.route("/api/user/")
def get_user_info():
    username = request.args.get("username")
    if username is None:
        return {}
    user_info = mongo.db.user.find_one({"username": username}, {"_id": 0})
    if user_info is None:
        return {}
    return user_info

@app.route("/api/favorite", methods=["POST"])
def favo_club():
    form = request.get_json(force=True)
    if form is None:
        return "Invalid Input Format"
    try:
        assert("username" in form and isinstance(form["username"], str))
        assert("club" in form and isinstance(form["club"], str))
    except AssertionError:
        return "Invalid Input Info"
    user_info = mongo.db.user.find_one({"username": form["username"]}, {"_id": 0})
    if user_info is None:
        return "Invalid Username"
    user = User(**user_info)
    if user.add_favorites(form["club"]):
        mongo.db.user.update_one({"username": form["username"]}, {"$set": user.__dict__})
        mongo.db.club.update_one({"name": form["club"]}, {"$inc": {"favo_counts": 1}})
        return "Successfully Favorite"
    return "Already Favorited"

@app.route("/api/comment", methods=["POST"])
def comment():
    form = request.get_json(force=True)
    if form is None:
        return "Invalid Comment Format"
    try:
        assert("username" in form and isinstance(form["username"], str))
        assert("comment" in form and isinstance(form["comment"], str))
        assert("club" in form and isinstance(form["club"], str))
    except AssertionError:
        return "Invalid Comment Info"
    if not mongo.db.user.find_one({"username": form["username"]}):
        return "Invalid Username"
    if not mongo.db.club.find_one({"name": form["club"]}):
        return "Invalid Club"
    mongo.db.comment.insert_one(form)
    return "OK"


if __name__ == '__main__':
    for col in mongo.db.list_collection_names():
        mongo.db[col].drop()
    save_club_col(mongo.db.club)
    user = User("jen", "Jennifer", "jen@seas.upenn.edu", [])
    mongo.db.user.insert_one(user.__dict__)

    app.run()
