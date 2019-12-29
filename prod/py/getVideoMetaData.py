# -- Libraries --
# Google API Libraries
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

# General-Purpose Libraries
import os
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


def getVideoMetaData(video_ids, raw_data, DEVELOPER_KEY):
    """
    This UDF takes in a list of YouTube Video Ids (video_ids),
    a list to place the output (raw_data),
    and a YouTube API token (DEVELOPER_KEY)).
    The UDF iterates through each of the provided videoIds,
    and appends the API result to the specified list (raw_data).
    The API request retreives the statistics, snippet, and contentDetails
    from the videos resource.
    """
    # Verify the key you are using.
    # print(DEVELOPER_KEY)
    for v_id in video_ids:
        # Get Data from YT API Cost 1+1+2+2 = 6 Units per call
        # 1 unit for overall call, 1 for the statistics,
        # 2 each for snippet and contentDetails
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                        developerKey=DEVELOPER_KEY)
        video_data = youtube.videos()\
                            .list(part='statistics, snippet, contentDetails',
                                  id=v_id)\
                            .execute()
        raw_data.append(video_data)

# -- RETREIVING CREDENTIALS --
KEY_CHAIN = load_obj('key_chain')

# -- LOADING VIDEO IDS --
# Retreives the video_ids_list file name with the latest date
video_ids_fname = sorted([f for f in os.listdir(directory)
                          if f.startswith('video_ids_list')])[-1]
video_ids = load_obj(video_ids_fname)

# -- PREP FOR QUERYING API --
# Creating a list to store the raw data from the videos resource
raw_data = []

# Calculating the number of videoIds we should request for in a single batch
# based on the number of team members (i.e. keys) we have
num_keys = len(KEY_CHAIN)
batch_num = ceil((len(video_ids) / len(KEY_CHAIN)))
batch_nums = [i * batch_num for i in range(num_keys + 1)]
print(batch_nums)

# -- RETREIVING DATA FROM VIDEO RESOURCE FOR ALL VIDEO IDs --
# Example of One Batch:
# getVideoMetaData(allVideosIds[batch_nums[0]:batch_nums[1]],data,KEY_CHAIN[4][1])

# for i in range(len(batch_nums)):
#   batch_of_videos = video_ids[batch_nums[i]:batch_nums[i+1]]
#   getVideoMetaData(batch_of_videos, raw_data, KEY_CHAIN[i][1])
#   print(KEY_CHAIN[i][0], len(raw_data))


ts = dt.datetime.now().strftime("%Y%m%d-%M%S")
raw_data_fname = 'bzfd_raw_data_' + ts
save_obj(raw_data, raw_data_fname)
