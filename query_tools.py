"""
Query Tools
Version: 1.0

By: Todd Karr,
    Katie Hoffer,
    Heather Moore,
    Tom Stark

This script retrieves data from the various APIs
and outputs the results to MongoDB. Note that most
of the data sources are built on top of the initial
query from Google.
"""
import os
# import logging
# import sys
import json
import codecs
import configparser
import requests
from fuzzywuzzy import fuzz
import pymongo
from pymongo import MongoClient

if 'IS_HEROKU' in os.environ:
    is_heroku = True
else:
    is_heroku = False

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

def query_guide(lat='38.890762', lon='-77.084755:', radius='400'):
    """
    This queries the Michelin Guide and returns the results to
    the MongoDB
    """
    location = f"{lon}:{lat}"
    try:
        auth_key = michelin_api_key
        url = f"https://secure-apir.viamichelin.com/apir/2/findPoi.json2/RESTAURANT/eng?center={location}&nb=100&dist={radius}&source=RESGR&filter=AGG.provider%20eq%20RESGR&charset=UTF-8&ie=UTF-8&authKey={auth_key}"
        response = requests.get(url).json()["poiList"]
        db.get_collection("michelin_guide").insert_many(response)
        # logging.info("MongoDB Updated: Database - food_fighters, Collection - michelin_guide")
    except Exception as e:
        print(e)
        raise

def query_google(lat='38.890762',
                 lon='-77.084755',
                 radius='400',
                 keywords=['coffee', 'cafe', 'brunch']):
    """
    This queries Google based on user inputs. All other functions
    build on the results from this query.
    """
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    location = f"{lat}, {lon}"
    try:
        for kw in keywords:
            params = {
                "key": google_api_key,
                "type": 'food',
                "rankby": 'prominence',
                "location": location,
                "radius": radius,
                "keyword": kw
            }

            response = requests.get(base_url, params=params).json()

            key_results_list = response['results']

            if "next_page_token" in response:
                params = {
                    "key": google_api_key,
                    "type": 'food',
                    "rankby": 'prominence',
                    "location": location,
                    "radius": radius,
                    "keyword": kw,
                    "pagetoken": response["next_page_token"]
                }

                response_next_page = requests.get(base_url, params=params).json()
                key_results_list = key_results_list + response_next_page['results']

            else:
                print("no next page")

            for kr in key_results_list:
                kr["keyword"] = kw

            db.get_collection("google_places").insert_many(key_results_list)
    except Exception as e:
        print(e)


def query_yelp(lat='38.89076', lon='-77.084755', radius='400'):
    """
    This function queries Yelp based on the outputs of the Google
    places API call.
    """
    yelp_key = yelp_api_key
    try:
        for docs in db.get_collection("google_places").find({}):

            base_url = f"https://api.yelp.com/v3/businesses/search"
            header = {'Authorization': 'Bearer {}'.format(yelp_key)}
            params = {
                "latitude": lat,
                "longitude": lon,
                "radius": radius,
                "sort_by": 'rating',
                "limit": 50,
                "term": docs["name"]
                }
            response = requests.get(base_url,
                                    headers=header,
                                    params=params).json()
            results = response['businesses']

            db.get_collection("Yelp").insert_many(results)
            # logging.info("MongoDB Updated: Database - food_fighters, Collection - yelp")

    except Exception as e:
        print(e)
        raise


def query_zomato(lat='38.89076', lon='-77.084755', radius='400'):
    """
    This function queries Zomato based on the entries added via
    the Google Places API.
    """
    user_key = zomato_api_key
    try:
        headers = {'Accept': 'application/json', 'user-key': user_key}
        for docs in db.get_collection("google_places").find({}):
            search_url = "https://developers.zomato.com/api/v2.1/search?"
            parameters = f'lat={lat}&lon={lon}&radius={radius}&count=10&q={docs["name"]}'
            search_response = requests.get(f'{search_url}{parameters}', headers=headers)
            search_results = search_response.json()
            db.get_collection("zomato").insert_many([search_results])
            # logging.info("MongoDB Updated: Database - food_fighters, Collection - zomato")
    except Exception as e:
        print(e)
        raise

def fetch_foodie_index(lat='38.89076', lon='-77.084755'):
    """
    Get regional foodie/nightlife score. This ought to be tied to the pin,
    not the actual location of the restaurants.
    """
    try:
        user_key = zomato_api_key

        headers = {'Accept': 'application/json', 'user-key': user_key}
        loc_details_data = requests.get(f'https://developers.zomato.com/api/v2.1/geocode?lat={lat}&lon={lon}',
                                        headers=headers).json()
        foodie_score = loc_details_data['popularity']['popularity']
        nightlife_score = loc_details_data['popularity']['nightlife_index']
        loc_details = {'lat': lat,
                       'lon': lon,
                       'foodie_score': foodie_score,
                       'nightlife_score': nightlife_score}
        # This needs to be moved into Flask to aggregate results
        # db.get_collection("foodie_index").delete_many({})
        db.get_collection("foodie_index").insert_one(loc_details)
        # logging.info("MongoDB Updated: Database - food_fighters, Collection - foodie_score")
    except Exception as e:
        print(e)
        raise


def develop_output():
    """
    This function develops the files for the output collection
    and uploads it into the output collection in Mongo. It
    uses the FuzzWuzzy library to conduct fuzzy string comparison.
    """
    output_array = []
    for docs in db.get_collection("google_places").find({}):
        docs["city"] = docs["vicinity"].split(",")[-1].strip()
        del docs['_id']

        for mg_doc in db.get_collection("michelin_guide").find({}):
            del mg_doc['_id']

            if (fuzz.token_set_ratio(docs["vicinity"], mg_doc["datasheets"][0]["address"]) > 80 and
                    fuzz.token_set_ratio(docs["name"], mg_doc["datasheets"][0]["name"]) > 80):
                docs["michelin_stars"] = mg_doc["datasheets"][0]["michelin_stars"]
                docs["michelin_mention"] = True
                docs["michelin_description"] = mg_doc["datasheets"][0]["description"]
                docs["michelin_url"] = mg_doc["datasheets"][0]["web"]
                break

            else:
                docs["michelin_stars"] = 0
                docs["michelin_mention"] = False
                docs["michelin_description"] = None
                docs["michelin_url"] = None

        for yelp_doc in db.get_collection("Yelp").find({}):
            del yelp_doc['_id']
            if (fuzz.token_set_ratio(docs["vicinity"], yelp_doc["location"]["address1"]) > 80 and
                    fuzz.token_set_ratio(docs["name"], yelp_doc["name"]) > 80):
                docs["yelp_stars"] = yelp_doc["rating"]
                docs["yelp_url"] = yelp_doc["url"]
                break

            else:
                docs["yelp_stars"] = None
                docs["yelp_url"] = None

        """ The results in Zomato are nested in one document,
        so this for loop breaks them up so the break logic
        works better."""
        clean_zomato_list = []
        for zom_doc in db.get_collection("zomato").find({}):
            del zom_doc['_id']
            for restaurant in zom_doc["restaurants"]:
                clean_zomato_list.append(restaurant)

        for restaurant in clean_zomato_list:
            if (fuzz.token_set_ratio(docs["vicinity"], restaurant['restaurant']["location"]["address"]) > 80 and
                    fuzz.token_set_ratio(docs["name"], restaurant['restaurant']["name"]) > 80):
                docs["zomato_stars"] = restaurant['restaurant']['user_rating']['aggregate_rating']
                docs["zomato_timings"] = restaurant['restaurant']['timings']
                docs["zomato_avg_for_two"] = restaurant['restaurant']['average_cost_for_two']
                docs["zomato_events"] = restaurant['restaurant']['events_url']
                break

            else:
                docs["zomato_stars"] = None
                docs["zomato_timings"] = None
                docs["zomato_avg_for_two"] = None
                docs["zomato_events"] = None

        if docs not in output_array:
            output_array.append(docs)

    # db.get_collection("outputs").delete_many({})
    db.get_collection("outputs").insert_many(output_array)
