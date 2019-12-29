data_csv_fname = "../data/bzfd_data.csv"
bzfd_df = pd.read_csv(data_csv_fname, sep=',')
# Turn Tags Into Dummy Variables
bzfd_df['processedTags'] = bzfd_df['processedTags'].apply(lambda x: literal_eval(x))
bzfd_tags_batch_1 = pd.get_dummies(bzfd_df['processedTags'][:1500].apply(pd.Series).stack()).sum(level=0)
bzfd_tags_batch_2 = pd.get_dummies(bzfd_df['processedTags'][1500:3000].apply(pd.Series).stack()).sum(level=0)
bzfd_tags_batch_3 = pd.get_dummies(bzfd_df['processedTags'][3000:4500].apply(pd.Series).stack()).sum(level=0)
bzfd_tags_batch_4 = pd.get_dummies(bzfd_df['processedTags'][4500:].apply(pd.Series).stack()).sum(level=0)

batch_1 = [bzfd_df[['videoId','viewCount','logViewCount']][:1500], bzfd_tags_batch_1]
batch_2 = [bzfd_df[['videoId','viewCount','logViewCount']][1500:3000], bzfd_tags_batch_2]
batch_3 = [bzfd_df[['videoId','viewCount','logViewCount']][3000:4500], bzfd_tags_batch_3]
batch_4 = [bzfd_df[['videoId','viewCount','logViewCount']][4500:], bzfd_tags_batch_4]

dummies_batch_1 = pd.concat(batch_1,  axis=1, ignore_index=False, sort=False)
dummies_batch_2 = pd.concat(batch_2,  axis=1, ignore_index=False, sort=False)
dummies_batch_3 = pd.concat(batch_3,  axis=1, ignore_index=False, sort=False)
dummies_batch_4 = pd.concat(batch_4,  axis=1, ignore_index=False, sort=False)

dummies_batches = [dummies_batch_1,dummies_batch_2,dummies_batch_3,dummies_batch_4]
dummies = pd.concat(dummies_batches, axis=0, sort=False, verify_integrity=True)
dummy_cols = [col for col in dummies.columns if col not in ['videoId','viewCount','logViewCount']]
dummies[dummy_cols ] = dummies[dummy_cols].fillna(value=0)

dummies.to_csv(directory + 'data/tags_as_dummies_comma.csv', sep=',')
