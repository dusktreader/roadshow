import os

from roadshow import RoadshowError


api_url = os.getenv("API_URL")
RoadshowError.require_condition(bool(api_url), "Set API_URL before running this demo")
