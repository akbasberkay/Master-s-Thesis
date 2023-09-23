import pandas as pd
file_url = "E-commerce original data.csv"
data = pd.read_csv(file_url)
features = data[['latitude', 'longitude']]
print(features)

from sklearn.cluster import KMeans

kmeans = KMeans(
    init="random",
    n_clusters=50,
    n_init=10,
    max_iter=300,
    random_state=42
)

kmeans.fit(features)

labels = kmeans.labels_

data['cluster'] = labels

print(data)
print(type(data))

data.to_excel("clustered.xlsx")