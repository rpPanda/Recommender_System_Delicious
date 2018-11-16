import networkx as nx
from sklearn.neighbors import KDTree
import numpy as np
import time

landmarks = [] #list of all landmarks
dist = 5000.0/111.0
uq_id = 317
percent_landmarks = 0.1
percent_nodes = .75
cluster_id = 1
k = 2800
filename = 'social_main_sample_'+str(cluster_id) + '.txt'
f1 = open(filename, 'w')
f1.seek(0)
f1.truncate()
filename = 'spatial_main_sample_'+str(cluster_id) + '.txt'
f2 = open(filename, 'w')
f2.seek(0)
f2.truncate()
filename = 'main_sample_landmarks_'+str(cluster_id) + '.txt'
f3 = open(filename, 'w')
f3.seek(0)
f3.truncate()

print('Reading social file...')
social = []
filename = 'fs_cluster_social.txt'
with open(filename, 'r') as f:
	for line in f:
		words = line.split()
		social.append((int(words[0]), int(words[1])))

print('Reading spatial file...')
spatial = []
i = 0
filename = 'fs_cluster_spatial.txt'
with open(filename, 'r') as f:
	for line in f:
		words = line.split()
		spatial.append([int(words[0]) , float(words[1]), float(words[2])])
		if spatial[i][0] == uq_id:
			uq_index = i
		i+=1

print(spatial[uq_index][0])

features = []
for user in spatial:
	features.append([user[1], user[2]])
print(len(features))
#print('Total number of users in sample: %s' %(len(final_spatial)))
X = np.array(features)
kdt = KDTree(X ,leaf_size=100 , metric = 'euclidean')
result = kdt.query(X , k = k , return_distance = False)

final_spatial = {}
for u in result[uq_index]:
	final_spatial[spatial[u][0]] = (spatial[u][1] , spatial[u][2])
if uq_id not in final_spatial:
	print("not in final_spatial")
	final_spatial[uq_id] = (spatial[uq_index][1] , spatial[uq_index][2]) 
final_social = []
for u in social:
	if u[0] in final_spatial and u[1] in final_spatial:
		final_social.append((u[0], u[1]))


print('Total number of edges in sample: %s' %(int(len(final_social)/2)))

print('Generating social graph...')
G = nx.Graph()

for user in final_spatial:
	G.add_node(user, x = final_spatial[user][0] , y = final_spatial[user][1])

for edges in final_social:
	G.add_edge(edges[0], edges[1])

print('Filtering out users with zero degree...')
temp_dict = G.degree(G)
remove_user = []
for user in temp_dict:
	if temp_dict[user] == 0:
		remove_user.append(user)

for user in remove_user:
	if user == uq_id:
		print("zero degree user")
	del final_spatial[user]
	G.nodes().remove(user)

print('After filtering out, users left: %s' %(len(final_spatial)))

print('Assigning edge weights...')
temp_dict = G.degree(G)
f = max(temp_dict, key=temp_dict.get)
max_deg = temp_dict[f]
print(max_deg)
for edge in G.edges():
	deg1 = float(temp_dict[edge[0]])
	deg2 = float(temp_dict[edge[1]])
	weight = (deg1*deg2)/(max_deg)**2
	#print('(%s %s %s)' %(deg1 , deg2 , weight))
	G[edge[0]][edge[1]]['weight'] = weight

print('Generating social and spatial files...')
for edge in G.edges():
	s = str(edge[0]) + '\t' + str(edge[1]) + '\t' + str(G[edge[0]][edge[1]]['weight']) + '\n'
	f1.write(s)

for user in final_spatial:
	s = str(user) + '\t' + str(final_spatial[user][0]) + '\t' + str(final_spatial[user][1]) + '\n'
	f2.write(s)

print('Calculating betweenness_centrality...')
k = int((percent_nodes/100)*(len(final_spatial)))
l = nx.betweenness_centrality(G, k = k, normalized = False, weight = 'weight')

print('Generating landmarks file...')
for u in l:
	landmarks.append((u, l[u]))
landmarks.sort(key = lambda x:(-x[1], x[0]))
k = int((percent_landmarks/100)*(len(spatial)))
i = 0
for user in landmarks:
	if i < k:
		s = str(user[0]) + '\n'
		f3.write(s)
		i += 1
	else:
		break
	
f1.close()
f2.close()
f3.close()

print('Done.')