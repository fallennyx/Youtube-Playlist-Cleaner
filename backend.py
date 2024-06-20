import os
import random
import time
import json


import google.auth.transport.requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from dotenv import load_dotenv
load_dotenv()


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secrets.json"
client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
# This OAuth 2.0 access scope allows for full access to the authenticated user's account.
SCOPES = ["https://www.googleapis.com/auth/youtube"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"


# Create a client secrets dictionary
credentials = {
    "web": {
        "client_id": os.getenv('CLIENT_ID'),
        "project_id": os.getenv('PROJECT_ID'),
        "auth_uri":  os.getenv('AUTH_URI'),
        "token_uri":  os.getenv('TOKEN_URI'),
        "auth_provider_x509_cert_url":  os.getenv('AUTH_PROVIDER_X509_CERT_URL'),
        "client_secret": os.getenv('CLIENT_SECRET')
    }
}


# Write the client secrets to a JSON file
with open('client_secrets.json', 'w') as outfile:
    json.dump(credentials, outfile)





def get_authenticated_service():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')

    # Print the authorization URL
    print(f'Please go to this URL and authorize access: {authorization_url}')

    # Prompt the user to enter the authorization code
    code = input('Enter the authorization code: ')
    flow.fetch_token(code=code)

    credentials = flow.credentials
    return googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def get_playlist_title(youtube,playlist_id):
    # Call the playlists.list method to retrieve the playlist data
    playlist_response = youtube.playlists().list(
        part='snippet',
        id=playlist_id
    ).execute()

    # Extract the playlist title from the response
    if 'items' in playlist_response:
        playlist_title = playlist_response['items'][0]['snippet']['title']
        return playlist_title
    else:
        return None

def get_playlist_items(youtube,playlist_id, max_results=50):
    playlist_items = []

    # Initial request to fetch the first page of playlist items
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=max_results
    )
    response = request.execute()

    # Add the items from the first page to the playlist_items list
    if 'items' in response:
        playlist_items.extend(response['items'])

    # Check if there are more pages of results
    while 'nextPageToken' in response:
        next_page_token = response['nextPageToken']

        # Make a new request to fetch the next page of playlist items
        request = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=max_results,
            pageToken=next_page_token
        )
        response = request.execute()

        # Add the items from the next page to the playlist_items list
        if 'items' in response:
            playlist_items.extend(response['items'])

    return playlist_items
def search_videos(youtube, query):
    """Searches for videos on YouTube."""
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=5  # Get the top result
    )
    response = request.execute()
    return response.get('items', [])

def create_playlist(youtube, title, description):
    """Creates a new YouTube playlist."""
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": "Clean Version of "+ title,
                "description": description
            },
            "status": {
                "privacyStatus": "private"  # or "public" / "unlisted"
            }
        }
    )
    response = request.execute()
    return response["id"]
def add_video_to_playlist(youtube, playlist_id, video_id):
    """Adds a video to a YouTube playlist."""
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    request.execute()

def add_video_to_playlist_with_retry(youtube, playlist_id, video_id, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            add_video_to_playlist(youtube, playlist_id, video_id)
            print(f'Added video to the playlist.')
            return
        except googleapiclient.errors.HttpError as e:
            print(f'HttpError: {e}')
            if e.resp.status == 409:  # Conflict error
                print('Retrying...')
                retries += 1
                time.sleep(random.uniform(1, 3))  # Add a random delay before retrying
            else:
                raise  # Raise the exception if it's not a conflict error
    print(f'Failed to add video after {max_retries} retries.')

def final(id):
    youtube = get_authenticated_service()
    original_playlist_id = id  # Replace with your original playlist ID
    new_playlist_description = 'A playlist of clean versions of the original videos.'

    #get og playlist title
    playlisttitle=get_playlist_title(youtube,original_playlist_id)
    new_playlist_title = 'Clean Version of '+ playlisttitle
    new_playlist_description = 'A playlist of clean versions of the'+ new_playlist_title + 'playlist.'



    # Step 1: Retrieve original playlist items
    playlist_items = get_playlist_items(youtube, original_playlist_id)

    # Step 2: Create a new playlist
    new_playlist_id = create_playlist(youtube, new_playlist_title, new_playlist_description)

    for item in playlist_items:
        video_title = item['snippet']['title']
        search_query = "CLEAN "+ video_title + " clean version"

        # Step 3: Search for "clean" version of the video
        search_results = search_videos(youtube, search_query)


        if search_results:
            title=search_results[0]['snippet']['title']
            if "clean" in title.lower():
                clean_video_id = search_results[0]['id']['videoId']
            else:
                clean_video_id = search_results[1]['id']['videoId']


            # Step 4: Add the clean video to the new playlist
            add_video_to_playlist(youtube, new_playlist_id, clean_video_id)
            print(f'Added "{search_query}" to the new playlist.')

if __name__ == '__main__':
    final(id)

