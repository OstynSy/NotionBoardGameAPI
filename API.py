import requests
import xmltodict
from pprint import pprint
from notion_client import Client
from dotenv import load_dotenv
import os
from fuzzywuzzy import fuzz

# Load environment variables from .env file
load_dotenv()

# Connect to Notion API
notion = Client(auth=os.environ["NOTION_KEY"])
board_game_id = os.getenv("NOTION_DATABASE_ID")

# working retrieves the title of last element in db===========================================================================================================================

results = notion.databases.query(
    database_id=board_game_id,
    sort=[
        {
            "property": "last_edited_time",
            "direction": "descending"
        }
    ]
).get("results")

#pprint(results)
# Get the last element of the database
last_title = results[0]["properties"]["Name"]["title"][0]["plain_text"]
last_page_id = results[0]["id"]
pprint(last_page_id)

# Print the last element's ID and properties
pprint(last_title)
#===========================================================================================================================

# Set up Boardgamegeek API parameters
base_url = "https://www.boardgamegeek.com/xmlapi2/"
search_path = "search?type=boardgame&query="
thing_path = "thing?type=boardgame&stats=1&id="


last_title = "Tether"

# Search for board game information using the Boardgamegeek API
response = requests.get(base_url + search_path + last_title)
xml_data = response.content
json_data = xmltodict.parse(xml_data)
items = json_data.get("items", {}).get("item", [])

#pprint(items)

# Fuzzy match title to find ID of multiple results===========================================================================================================================
best_match_id = None
best_match_score = 0

for item in items:
    name = item["name"]["@value"]
    #pprint(name)
    match_score = fuzz.token_sort_ratio(last_title, name)
    if match_score > best_match_score:
        best_match_score = match_score
        best_match_id = item["@id"]

#pprint(f"Best match ID: {best_match_id}")

#===========================================================================================================================


game_info_response = requests.get(base_url + thing_path + str(best_match_id))
game_info_data = game_info_response.content
game_info = game_info = xmltodict.parse(game_info_data)['items']['item']

#pprint(game_info)

min_players = game_info["minplayers"]["@value"]
max_players = game_info["maxplayers"]["@value"]
min_time = game_info["minplaytime"]["@value"]
max_time = game_info["maxplaytime"]["@value"]
genre = game_info["link"][0]["@value"]

#Update the Notion database with board game information
notion.pages.update(page_id= last_page_id, properties={
    "Minimum Players": {"rich_text": [{"text": {"content": min_players}}]},
    "Maximum Players": {"rich_text": [{"text": {"content": max_players}}]},
    "Minimum Time": {"rich_text": [{"text": {"content": min_time}}]},
    "Maximum Time": {"rich_text": [{"text": {"content": max_time}}]},
    "Genre": {"rich_text": [{"text": {"content": genre}}]},
})
