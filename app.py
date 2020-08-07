"""
App.py
Version 1.0
By: Todd Karr,
    Katie Hoffer,
    Heather Moore,
    Tom Stark
This app is the core of our Food Score platform
which coordinates activities on the web with
API calls to our PostgreSQL DB
"""

import os
#import logging
import pymongo
#import TS_Query_Tools as tsq
import pandas as pd
import query_tools as tsq
from flask import Flask,\
                  render_template,\
                  jsonify,\
                  request,\
                  redirect    

#logPath = os.path.join('flask.log')
#logging.basicConfig(format='%(asctime)s : %(lineno)d : %(levelname)s : %(message)s',
                     #level=logging.DEBUG,
                    # filename=logPath)
        
if 'IS_HEROKU' in os.environ:
    is_heroku = True

# Import your config file(s) and variable(s)
if is_heroku == False:
    from config import michelin_key, google_key, zomato_key, yelp_key, CONN
else:
    google_api_key = os.environ.get('google_key')
    michelin_api_key = os.environ.get('michelin_key')
    yelp_api_key = os.environ.get('yelp_key')
    zomato_api_key = os.environ.get('zomato_key')
    CONN = os.environ.get('CONN')

## These need to be uncommented to enable the proxy in Heroku
os.environ['http_proxy'] = os.environ.get('FIXIE_URL', '')
os.environ['https_proxy'] = os.environ.get('FIXIE_URL', '')

client = pymongo.MongoClient(CONN)
db = client["food_fighters"]

app = Flask(__name__)

#CONN = "mongodb://ec2-18-224-51-189.us-east-2.compute.amazonaws.com:27017"
#CLIENT = pymongo.MongoClient(CONN)
#db = CLIENT["food_fighters"]
           
@app.route("/")
def home():
    return render_template('index.html')


#@app.route("/cdb")
#def cleardb():
   # db.get_collection("michelin_guide").delete_many({})
   # db.get_collection("google_places").delete_many({})
    #db.get_collection("Yelp").delete_many({})
    #db.get_collection("zomato").delete_many({})
   # db.get_collection("foodie_index").delete_many({})
    #db.get_collection("outputs").delete_many({})
    #return redirect("/", code=302)
  

@app.route("/send/<lat>/<lon>/<key>")#, methods=["GET"])
def send(lat,lon,key):
    #if request.method == "GET":
    
    # lat = request.form["lat"]
    # lon = request.form["lon"]
    #lat = request.args.get('lat') #38.896059
    #lon = request.args.get('lon') #-77.036679
    keywords = key#request.args.get('key')# request.form["key"]

    query_tools.query_google(lat, lon, [keywords])
    query_tools.query_guide(lat, lon)
    #query_tools.query_yelp(lat, lon)
    query_tools.query_zomato(lat, lon)
    query_tools.fetch_foodie_index(lat, lon)
    query_tools.develop_output(lat, lon)

    # point1 = {'lat': request.form["lat"],
    #           'long': request.form["long"],
    #           'cuisine': request.form["cuisine"]}

    return redirect("/", code=302)

@app.route("/output-data")
def output_data_points():  
    # CONN = "mongodb://ec2-18-224-51-189.us-east-2.compute.amazonaws.com:27017"
    # CLIENT = pymongo.MongoClient(CONN)
    # db = CLIENT["food_fighters"]
    output = db.get_collection("outputs")
    output_query = list(output.find())
    output_results_df = pd.DataFrame(output_query)
    output_results = output_results_df.to_json(default_handler=str, orient='records')
  
    return output_results

@app.route("/foodie-index")
def foodie_index():
    # CONN = "mongodb://ec2-18-224-51-189.us-east-2.compute.amazonaws.com:27017"
    # CLIENT = pymongo.MongoClient(CONN)
    # db = CLIENT["food_fighters"]
    foodie = db.get_collection("foodie_index")
    foodie_index_query = list(foodie.find())
    foodie_index_df = pd.DataFrame(foodie_index_query)
    foodie_index_results = foodie_index_df.to_json(default_handler=str, orient='records')
  
    return foodie_index_results

@app.route("/dj")
def dj():
    return render_template('dojomenu.html')


@app.route("/djf")
def djf():
    return render_template('dojofilt.html')


if __name__ == "__main__":
    app.run(debug=True)
