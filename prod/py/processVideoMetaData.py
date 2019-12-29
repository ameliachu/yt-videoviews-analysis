# -- Libraries --
# This py script requires further annotation
# what are the inputs?
import os
import datetime as dt
import pickle

from math import ceil, floor
import numpy as np
import pandas as pd


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

def trimTagList(s):
    return list(set([i.lower().replace(" ", "") for i in s]))


def getDurationInSeconds(duration):
    """
    This doesn't cover all possible cases, needs editing
    """
    if duration.endswith('S'):
        if 'H' in duration:
            t =  dt.datetime.strptime(duration,'PT%HH%MM%SS')
        if 'H' not in duration and 'M' in duration:
            t =  dt.datetime.strptime(duration,'PT%MM%SS')
        if 'H' not in duration and 'M' not in duration:
            t =  dt.datetime.strptime(duration,'PT%SS')
    else:
        t = dt.datetime.strptime(duration,'PT%MM')
    s = dt.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second).total_seconds()
    return s


raw_data_fname = 'data/bzfd_raw_data_20191029-0708'
raw_data = load_obj(raw_data_fname)


# Define the Raw Data Columns we want
snippet_columns = ['channelId', 'channelTitle','publishedAt','title',
'liveBroadcastContent', 'categoryId', 'description','tags']
# 'tags' must be the last item
statistics_columns = ['commentCount','dislikeCount','favoriteCount','likeCount','viewCount']


# Generating a template for our Dict of data
data = {'videoId':[],'duration':[]}

for col in snippet_columns:
    data[col] = []

for col in statistics_columns:
    data[col] = []

for row in raw_data:
    video_data = row
    # Grab the 'items' key
    items = video_data['items']
    for i in items:
        v_id = i['id']
        snippet = i['snippet']
        statistics = i['statistics']
        content = i['contentDetails']
        data['videoId'].append(v_id)
        data['duration'].append(content['duration'])

        snippet_cols = [s for s in snippet_columns if s in snippet.keys()]
        statistics_cols = [s for s in statistics_columns if s in statistics.keys()]

        #if 'duration' not in content.keys():
        #    print('derp.')
        if 'tags' not in snippet_cols:
            data['tags'].append([])

        missing_snippets = list(set(snippet_columns[:-1]) - set(snippet_cols))
        missing_statistics = list(set(statistics_columns) - set(statistics_cols))

        for col in snippet_cols:
            data[col].append(snippet[col])
        for col in statistics_cols:
            data[col].append(statistics[col])
        for col in missing_snippets:
            data[col].append("")
        for col in missing_statistics:
            data[col].append(np.nan)

data_pd = pd.DataFrame.from_dict(data)

data_pd.viewCount = data_pd.viewCount.astype(float)
# we have nans, should we convert nulls to 0? Should look into why 0
data_pd['publishedAt'] = pd.to_datetime(data_pd['publishedAt'])
data_pd['dayOfWeekPublishedAt'] = data_pd['publishedAt'].dt.day_name()
data_pd['titleLength'] = data_pd['title'].apply(lambda x: len(x))
data_pd['processedTags'] = data_pd['tags'].apply(lambda x: trimTagList(x))
# data_pd['retreivedAt'] = pd.Timestamp.today()
data_pd['retreivedAt'] = pd.Timestamp('2019-10-29 11:16:29.962579')
data_pd['secondsSincePublished'] = (data_pd['retreivedAt'] - data_pd['publishedAt']).dt.total_seconds()
data_pd['durationInSeconds'] = data_pd['duration'].apply(lambda x: getDurationInSeconds(x))
data_pd['logViewCount'] = data_pd['viewCount'].apply(lambda x: np.log(x))
data_pd['logSecondsSincePublished'] = data_pd['secondsSincePublished'].apply(lambda x: np.log(x))

cols = ['videoId', 'duration', 'publishedAt', 'title', 'liveBroadcastContent',
        'categoryId', 'commentCount', 'dislikeCount', 'favoriteCount',
        'likeCount', 'viewCount', 'logViewCount', 'dayOfWeekPublishedAt',
        'titleLength', 'processedTags', 'retreivedAt', 'secondsSincePublished',
        'logSecondsSincePublished', 'durationInSeconds']

data_pd[cols].to_csv("../data/bzfd_data.csv", index=False, index_label=False)
