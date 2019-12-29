import pandas as pd
import pickle
import datetime as dt
import operator
from ast import literal_eval

directory = '/Users/chuamelia/Google Drive/Fall 2019/\
Introduction to Data Science/Term Project/\
Group Term Project/YouTube Video View Analysis/'


def load_obj(fname):
    # This loads the pickled object.
    with open(directory + fname + '.pkl', 'rb') as f:
        return pickle.load(f)


def save_obj(obj, fname):
    # This writes out a python object as a pickle.
    with open(directory + fname + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def trimTagList(s):
    # This UDF takes list(str) as input and
    # returns a unique list of strings with whitespace removed.
    return list(set([i.lower().replace(" ", "") for i in s]))


# Get the Frequency of Each Tag
processed_data_fname = "data/bzfd_processed_data_20191031-1233"
processed_data = load_obj(processed_data_fname)

processed_tag_list = [trimTagList(s) for s in processed_data['tags']]

flatten = [i for s in processed_tag_list for i in s]

freq = {}
for items in flatten:
    freq[items] = flatten.count(items)

ts = dt.datetime.now().strftime("%Y%m%d-%M%S")
tag_freq_fname = 'bzfd_tag_freq_' + ts
print(tag_freq_fname)
save_obj(freq, tag_freq_fname)

# Get a Dummy Dataframe with all the tags
data_csv_fname = "../data/bzfd_data.csv"
bzfd_df = pd.read_csv(data_csv_fname, sep=',')
bzfd_df['processedTags'] = bzfd_df['processedTags'].apply(lambda x: literal_eval(x))

# Turn Tags Into Dummy Variables

bzfd_tags_batch_1 = pd.get_dummies(bzfd_df['processedTags'][:1500]
                                   .apply(pd.Series).stack()).sum(level=0)
bzfd_tags_batch_2 = pd.get_dummies(bzfd_df['processedTags'][1500:3000]
                                   .apply(pd.Series).stack()).sum(level=0)
bzfd_tags_batch_3 = pd.get_dummies(bzfd_df['processedTags'][3000:4500]
                                   .apply(pd.Series).stack()).sum(level=0)
bzfd_tags_batch_4 = pd.get_dummies(bzfd_df['processedTags'][4500:]
                                   .apply(pd.Series).stack()).sum(level=0)

batch_1 = [bzfd_df[['videoId','viewCount','logViewCount']][:1500], bzfd_tags_batch_1]
batch_2 = [bzfd_df[['videoId','viewCount','logViewCount']][1500:3000], bzfd_tags_batch_2]
batch_3 = [bzfd_df[['videoId','viewCount','logViewCount']][3000:4500], bzfd_tags_batch_3]
batch_4 = [bzfd_df[['videoId','viewCount','logViewCount']][4500:], bzfd_tags_batch_4]

dummies_batch_1 = pd.concat(batch_1,  axis=1, ignore_index=False)
dummies_batch_2 = pd.concat(batch_2,  axis=1, ignore_index=False)
dummies_batch_3 = pd.concat(batch_3,  axis=1, ignore_index=False)
dummies_batch_4 = pd.concat(batch_4,  axis=1, ignore_index=False)

dummies = pd.concat(dummies_batches, axis=0, sort=False, verify_integrity=True)
dummy_cols = [col for col in dummies.columns if col not in ['videoId','viewCount','logViewCount']]
dummies[dummy_cols ] = dummies[dummy_cols].fillna(value=0)
# dummies.to_csv(directory + 'data/tags_as_dummies.csv', sep='\t')
dummies.to_csv(directory + 'data/tags_as_dummies_comma.csv', sep=',')
# we can do this in batches if it's too intense for local computer.
# Should try
# Throw tags into Random Forest
