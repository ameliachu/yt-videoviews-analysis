# -- Libraries --
# Google API Libraries
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

# General-Purpose Libraries
import datetime as dt
import pickle
from math import ceil, floor

# -- User-Defined Functions (UDFs) --


# Specifying the directory to write out pickles
directory = '/Users/chuamelia/Google Drive/Fall 2019/\
Introduction to Data Science/Term Project/\
Group Term Project/YouTube Video View Analysis/'


def save_obj(obj, fname):
    # This writes out a python object as a pickle.
    with open(directory + fname + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(fname):
    # This loads the pickled object.
    with open(directory + fname + '.pkl', 'rb') as f:
        return pickle.load(f)


def connectToYouTubeAPI(DEVELOPER_KEY):
    # Specifying API Service
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    # Creating connection to the Youtube Data API Service
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)
    return youtube


def getPlaylistItemsSnippet(uploads_playlist_id, page_token):
    """
    This UDF retreives all items from the playlistItems.snippet
    section of the YouTube Data API.
    """
    playlistItems = youtube.playlistItems().list(
        playlistId=uploads_playlist_id,
        pageToken=page_token,
        part="snippet",
        maxResults=50).execute()
    return playlistItems


def getVideoIdsAndTokens(playlist_result):
    """
    This UDF takes the result generated from getPlaylistItemsSnippet.
    It returns the videoIds and the nextPageToken needed
    to get the next batch of videoIds.
    """
    # Get List of Videos in Playlist
    playlist_items = playlist_result['items']
    num_items = len(playlist_items)
    videosIds = [playlist_items[i]['snippet']['resourceId']['videoId']
                 for i in range(num_items)]

    # Get the nextPageToken to find the next 50 Video Ids.
    # If it's the last page, there is no nextPageToken
    nextPageToken = None
    if 'nextPageToken' in playlist_result.keys():
        # Attempt to retreive the token, only if it exists
        nextPageToken = playlist_result['nextPageToken']
    return videosIds, nextPageToken


# -- RETREIVING CREDENTIALS --
KEY_CHAIN = load_obj('key_chain')

# -- CONNECTION TO YOUTUBE DATA API --
youtube = connectToYouTubeAPI(KEY_CHAIN[5][1])

# -- FIND UPLOADS PLAYLIST ID --
# This retreives the playlistId for the playlist of all uploads.
# Method learned from:
# https://stackoverflow.com/questions/50199490/youtube-api-v3-get-every-video-id-from-given-channel

# ChannelId for the BuzzFeedVideo YouTube Channel
CHANNEL_ID = 'UCpko_-a4wgz2u_DgDgd9fqA'

# Querying the channels.contentDetails resource
results = youtube.channels().list(
    id=CHANNEL_ID,
    pageToken=None,
    part="contentDetails",
    maxResults=50).execute()

# Pulling out the playlistId of the Uploads Playlist
channel_content_details = results['items'][0]['contentDetails']
uploads_playlist_id = channel_content_details['relatedPlaylists']['uploads']
# uploads_playlist_id = 'UUpko_-a4wgz2u_DgDgd9fqA'

# -- RETREIVING ALL VIDEO IDs IN UPLOADS PLAYLIST --
# This retreives all videoIds for the channel.

# Creating connection to the Youtube Data API Service
youtube = connectToYouTubeAPI(KEY_CHAIN[5][1])

# Create lists to store nextPageTokens and videoIds
page_tokens = []
video_ids = []

# Retreiving snippet part of the playlistItems resource
playlist_result = getPlaylistItemsSnippet(uploads_playlist_id, None)

# Getting the number of times we need to iterate through

# PlaylistItems.pageInfo.totalResults provides
# the number of videos in a playlist
total_videos = playlist_result['pageInfo']['totalResults']

# Dividing by 50 because we can retreive a maximum of 50 videos at a time
# Using floor because the first batch won't have a nextPageToken as input
num_batches = floor(total_videos / 50)
print(total_videos)

# Retreiving the first batch
videosIds, nextPageToken = getVideoIdsAndTokens(playlist_result)
video_ids += videosIds
page_tokens.append(nextPageToken)

# Retreiving subsequent batches
for batch_num in range(num_batches):
    playlist_result = getPlaylistItemsSnippet(uploads_playlist_id, nextPageToken)

    videosIds, nextPageToken = getVideoIdsAndTokens(playlist_result)

    video_ids += videosIds
    page_tokens.append(nextPageToken)

# Saving list of videoIds in case we need to refer back to it.
ts = dt.datetime.now().strftime("%Y%m%d-%M%S")
name = 'data/video_ids_list_' + ts
save_obj(video_ids, name)
