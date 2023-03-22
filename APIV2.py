import requests
import xmltodict
from pprint import pprint
from notion_client import Client
from fuzzywuzzy import fuzz

# Takes boardgame name and a list of items
# Fuzzy matches the name with the names of the other items and returns the id that best matches
def fuzzyMatch(bg_name, items):
    for item in items:
        best_match_id = None
        best_match_score = 0
        name = item["name"]["@value"]
        #pprint(name)
        match_score = fuzz.token_sort_ratio(bg_name, name)
        if name == bg_name:
            best_match_id = item["@id"]
            return best_match_id

        elif match_score > best_match_score:
            best_match_score = match_score
            best_match_id = item["@id"]
        return best_match_id

# Connect to Notion API
notion = Client(auth="secret_wkHmezRHUYMn3cKFJyFqS0434IH1XBU2BzyiuoLECtr")
bg_database_id = "168933707099481d9064fa5c04b4dbb5"

# Obtains all data in the database
results = notion.databases.query(database_id=bg_database_id)

# Loop through the whole database and find Pages with Integration Status that are empty BAD and OK are excluded
list_empty_pages = []
for page in results["results"]:
    if (page["properties"]["Name"]["title"] != []) and (page["properties"]["Integration Status"]["rich_text"] == []):
        list_empty_pages.append(page)
#pprint(len(list_empty_pages))

# Set up Boardgamegeek API parameters
base_url = "https://www.boardgamegeek.com/xmlapi2/"
search_path = "search?type=boardgame&query="
thing_path = "thing?type=boardgame&stats=1&id="

# Search for BGG Data on each page
for page in list_empty_pages:
    error = ""
    #Search for board game information using the Boardgamegeek API. Uses Name and ID of the Notion page and searches in BGG to find number of results
    bg_name = page["properties"]["Name"]["title"][0]["plain_text"]
    page_id = page["id"]

    pprint("")
    pprint(bg_name)
    pprint(page_id)

    # search BGG API
    response = requests.get(base_url + search_path + bg_name)
    xml_data = response.content
    json_data = xmltodict.parse(xml_data)
    total = int(json_data.get("items", {}).get("@total", 0))
    items = json_data.get("items", {}).get("item", [])

    # Only Fuzzy match if there are more than 1 item (4 indicates more than 4 fields in the json)
    pprint(f"Search Results: {total}")
    best_match_id = -1

    try:
        # BGG found 0 results
        if total == 0:
            #report error that BGG can not find that item
            integration_status = "BAD"
            error = "No Results Found on BGG. Try being more accurate with your name. It is also possible that BGG does not have data on your game"
            pprint("no results")

        # BGG found multiple results
        elif total > 1:
            best_match_id = fuzzyMatch(bg_name, items)
            pprint(f"Best match ID: {best_match_id}")

        #BGG only found 1 result
        else:
            best_match_id = items["@id"]
            pprint(f"Best match ID: {best_match_id}")

        #if an ID was found populate all fields with new data and update Notion DB
        if best_match_id != -1:
            game_info_response = requests.get(base_url + thing_path + str(best_match_id))
            game_info_data = game_info_response.content
            game_info = xmltodict.parse(game_info_data)['items']['item']

            #Store Json values as Variables
            image_url = {
                "name": "Image.png",
                "external":{
                    "url": game_info["image"]
                } 
            }

            min_players = game_info["minplayers"]["@value"]
            max_players = game_info["maxplayers"]["@value"]
            min_time = game_info["minplaytime"]["@value"]
            max_time = game_info["maxplaytime"]["@value"]

            genre = {
                "name": game_info["link"][0]["@value"]
            }

            ratings = game_info["statistics"]["ratings"]

            geek_rating = game_info["statistics"]["ratings"]["bayesaverage"]["@value"]
            avg_rating = game_info["statistics"]["ratings"]["average"]["@value"]
            num_votes = game_info["statistics"]["ratings"]["usersrated"]["@value"]

            integration_status = "OK"
            pprint(integration_status)
            #pprint(game_info)

            notion.pages.update(page_id= page_id, properties={
                "Image": {"files": [image_url]},
                "Min. Players": {"number": int(min_players)},
                "Max. Players": {"number": int(max_players)},
                "Min. Time": {"number": int(min_time)},
                "Max. Time": {"number": int(max_time)},
                "Genre": {"multi_select": [genre]},
                "Geek Rating": {"number": round(float(geek_rating),2)},
                "Avg. Rating": {"number": round(float(avg_rating),2)},
                "Num Votes": {"number": int(num_votes)},
                "Integration Status": {"rich_text": [{"text": {"content": integration_status}}]},
                "Error": {"rich_text": [{"text": {"content": error}}]},
            })

    except:
        integration_status = "BAD"
        error= "There were issues searching for results!"
        pprint("There was an error with the results")        

    # Update Notion DB that could not be searched or had errors
    notion.pages.update(page_id= page_id, properties={
        "Integration Status": {"rich_text": [{"text": {"content": integration_status}}]},
        "Error": {"rich_text": [{"text": {"content": error}}]},
    })