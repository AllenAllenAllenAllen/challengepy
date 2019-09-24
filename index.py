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
    """
    Get all available APIs
    :return: APIs in JSON string
    """
    apis = ["GET /api/clubs", "POST /api/clubs", "GET /api/user/:username", "POST /api/favorite", "POST /api/comment"]
    return json.dumps(apis)

@app.route("/api/clubs")
def clubs():
    """
    Get all clubs information, including name, tags, desc, favorite_counts
    :return: clubs info in JSON string
    """
    resp = []
    for club in mongo.db.club.find({}, {"_id": 0}):
        resp.append(club)
    return json.dumps(resp)

@app.route("/api/clubs", methods=["POST"])
def create_club():
    """
    Create a new club or update the club info if it already exists
    :return: status string
    """
    form = request.get_json(force=True)
    if form is None:
        return "Invalid Club Info Format"
    try:
        assert("name" in form and isinstance(form["name"], str))
        assert("tags" in form and isinstance(form["tags"], list))
        assert("desc" in form and isinstance(form["desc"], str))
        if len(form) != 3:
            return "Incorrect Number of Parameters"
    except AssertionError:
        return "Invalid Club Info"
    form["favo_counts"] = 0
    club = mongo.db.club.find_one({"name": form["name"]})
    if club is not None:
        form["favo_counts"] = club["favo_counts"]
    mongo.db.club.update_one({"name": form["name"]}, {"$set": form}, upsert=True)
    return "OK"

@app.route("/api/user/")
def get_user_info():
    """
    Get a user profile
    :return: user info in JSON string
    """
    username = request.args.get("username")
    if username is None:
        return {}
    user_info = mongo.db.user.find_one({"username": username}, {"_id": 0})
    if user_info is None:
        return {}
    return user_info

@app.route("/api/favorite", methods=["POST"])
def favo_club():
    """
    Allow a user to favorite a club
    :return: status string
    """
    form = request.get_json(force=True)
    if form is None:
        return "Invalid Input Format"
    try:
        assert("username" in form and isinstance(form["username"], str))
        assert("club" in form and isinstance(form["club"], str))
        if len(form) != 2:
            return "Incorrect Number of Parameters"
    except AssertionError:
        return "Invalid Input Info"
    user_info = mongo.db.user.find_one({"username": form["username"]}, {"_id": 0})
    if user_info is None:
        return "Invalid Username"
    club = mongo.db.club.find_one({"name": form["club"]})
    if club is None:
        return "Invalid Club"
    user = User(**user_info)
    if user.add_favorites(form["club"]):
        mongo.db.user.update_one({"username": form["username"]}, {"$set": user.__dict__})
        mongo.db.club.update_one({"name": form["club"]}, {"$inc": {"favo_counts": 1}})
        return "Successfully Favorite"
    return "Already Favorited"

@app.route("/api/comment", methods=["POST"])
def comment():
    """
    Allow a user to post comment for a club
    :return: status string
    """
    form = request.get_json(force=True)
    if form is None:
        return "Invalid Comment Format"
    try:
        assert("username" in form and isinstance(form["username"], str))
        assert("comment" in form and isinstance(form["comment"], str))
        assert("club" in form and isinstance(form["club"], str))
        if len(form) != 3:
            return "Incorrect Number of Parameters"
    except AssertionError:
        return "Invalid Comment Info"
    if not mongo.db.user.find_one({"username": form["username"]}):
        return "Invalid Username"
    if not mongo.db.club.find_one({"name": form["club"]}):
        return "Invalid Club"
    mongo.db.comment.insert_one(form)
    return "OK"


if __name__ == '__main__':
    # MongoDB Setup
    for col in mongo.db.list_collection_names():
        mongo.db[col].drop()
    save_club_col(mongo.db.club)
    user = User("jen", "Jennifer", "jen@seas.upenn.edu", [])
    mongo.db.user.insert_one(user.__dict__)

    app.run()
