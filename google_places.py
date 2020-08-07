"""
Google Places API
Version: 1.0

By: Todd Karr,
    Katie Hoffer,
    Heather Moore,
    Tom Stark

This script retrieves data from the Google Places API
and outputs it to our MongoDB
"""

# Dependencies
import codecs
import os
import logging
import requests
import time
import pymongo

LOGPATH = os.path.join('foodie_app.log')
logging.basicConfig(format='%(asctime)s : %(lineno)d : %(levelname)s : %(message)s',
                    level=logging.DEBUG,
                    filename=LOGPATH)

CONN = "mongodb://ec2-18-224-51-189.us-east-2.compute.amazonaws.com:27017"
CLIENT = pymongo.MongoClient(CONN)
DB = CLIENT["food_fighters"]
GOOGLE_PLACES = DB.get_collection("google_places")

def query_google(location='38.890762, -77.084755',
                 radius='1000',
                 keywords=['coffee', 'cafe', 'brunch'],
                 gkey='key'):
    try:
        base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

        for keyword in keywords:
            print('----')
            print(keyword)

            params = {
                "key": gkey,
                "type": 'food',
                "rankby": 'prominence',
                "location": location,
                "radius": radius,
                "keyword" : keyword
                }
            response = requests.get(base_url, params=params).json()
            key_results_list = response['results']
            print(key_results_list)

            if "next_page_token" in response:
                time.sleep(1)
                params = {
                    "key": gkey,
                    "pagetoken": response["next_page_token"]
                    }
                response_next_page = requests.get(base_url, params=params).json()
                key_results_list = key_results_list + response_next_page['results']
                print(response_next_page)
            else: print("no next page")

            for key_result in key_results_list:
                key_result["keyword"] = keyword

            GOOGLE_PLACES.insert_many(key_results_list)
            logging.info("MongoDB Updated: Database - {}, Collection - {}".format("food_fighters", GOOGLE_PLACES))
            print(key_results_list)

    except Exception as error:
        logging.error(error)
        raise

query_google(location='38.896332, -77.023438',
             radius='100',
             keywords=['coffee', 'bar'],
             gkey=codecs.encode('NVmnFlOh9mq_Y3v5dToIEjgpam639rBVCcmIiB4', 'rot-13'))
