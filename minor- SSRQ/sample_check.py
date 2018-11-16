############################################################
#--------------------AIS implementation--------------------#
############################################################

#--------------------Prerequisites--------------------#
import sys
import math
import heapq
import time
import networkx as nx
from scipy.cluster.vq import vq, kmeans, whiten

#--------------------Globals--------------------#
clusters = {} #list to store all nodes
landmarks = [] #list of all landmarks
alpha = 0.5
fk = -1
fk_id = -1
k = 10
uq_id = 317
min_x = 1000
max_x = 0
min_y = 1000
max_y = 0
max_dist = 0
num_clusters = 80

#--------------------Class for Euclidean Space--------------------#
class Cluster:
	#constructor for a node
	def __init__(self, cluster_id, center_x, center_y):
		self.cluster_id = cluster_id
		self.center_x = center_x
		self.center_y = center_y
		self.radius = 0
		self.users = [] #all users inside the particular cluster
		self.pcap = 0
		self.dcap = 0
		self.MINF = 0 #MINF value for this node
		self.m_lower = {}
		self.m_higher = {} 
		
	#function to return minimum distance from a user to any point on cluster
	def set_dcap(self, x, y):
		d = math.sqrt((self.center_x - x)**2 + (self.center_y - y)**2) - self.radius
		if d < 0:
			self.dcap = 0
			return 0
		else:
			self.dcap = d
			return d

	#function to set MINF of a particular node
	def set_MINF(self, alpha, pcap, dcap):
		self.pcap = pcap
		self.dcap = dcap
		self.MINF = alpha*pcap + (1-alpha)*dcap/max_dist
		return

def findShortestAndLongest(G):
    global clusters
    global landmarks
    #pick a vertex from the landmark list
    for v in landmarks:
    #v is the vertex id for the landmark
    #set the social distance for this landmark
        #call dijkstra's for v
        length=nx.single_source_dijkstra_path_length(G,v)
        for c in clusters:
        	maxim = 0
        	minim = 1000
        	for u in clusters[c].users:
        		if u in length:
	        		if length[u] > maxim:
	        			maxim = length[u]
	        		if length[u] < minim:
	        			minim = length[u]
	        clusters[c].m_higher[v] = maxim
	        clusters[c].m_lower[v] = minim

#--------------------Function to set MINF of all nodes--------------------#
def set_MINF(uq , g):
	global clusters
	global landmarks
	length = nx.single_source_dijkstra_path_length(G, uq)
	for clt in clusters:
		pcap = 0
		for landmark in landmarks:
			mqj = length[landmark]
			if mqj < clusters[clt].m_lower[landmark]:
				pcap = max(pcap, clusters[clt].m_lower[landmark] - mqj)
			elif mqj > clusters[clt].m_higher[landmark]:
				pcap = max(pcap, mqj - clusters[clt].m_higher[landmark])
			else:
				pcap = max(pcap, 0)
		dcap = clusters[clt].set_dcap(g.node[uq]['x'], g.node[uq]['y'])
		clusters[clt].set_MINF(alpha, pcap, dcap)

#--------------------AIS Algorithm--------------------#
def AIS(G, alpha, k, uq):
	H = [] #initialise min-heap H
	R = {} #result set
	global clusters
	global fk
	global fk_id
	global max_dist
	count = 0
	length=nx.single_source_dijkstra_path_length(G,uq)
	for c in clusters:
		heapq.heappush(H, (clusters[c].MINF, 'Cluster', clusters[c].cluster_id)) #push all clusters into heap with MINF as key
	while len(H): #while heap is not empty and head's key is less than fk
		if count<k:
			temp = heapq.heappop(H) #pop the head item of H
			if temp[1] == 'Cluster': #if popped item is a cluster
				cluster = clusters[temp[2]]				
				for u in cluster.users: #push all users in cluster with MINF as key
					if u != uq:
						d = math.sqrt((G.node[uq]['x'] - G.node[u]['x'])**2 + (G.node[uq]['y'] - G.node[u]['y'])**2)
						user_key = alpha*cluster.pcap + (1-alpha)*d/max_dist
						heapq.heappush(H, (user_key, 'User', u))
			else: #if popped item is a user
				if temp[2] in length:
					p = length[temp[2]] #implement Dijkstra's here for now
					d = math.sqrt((G.node[uq]['x'] - G.node[temp[2]]['x'])**2 + (G.node[uq]['y'] - G.node[temp[2]]['y'])**2)
					f = alpha*p + (1-alpha)*d/max_dist
					if f>fk:
						fk = f
						fk_id = temp[2]
					R[temp[2]] = f
					#print(R)
					count += 1
		else:
			if H[0][0] < fk:
				temp = heapq.heappop(H) #pop the head item of H
				if temp[1] == 'Cluster': #if popped item is a cluster
					cluster = clusters[temp[2]]				
					for u in cluster.users: #push all users in cluster with MINF as key
						if u != uq:
							d = math.sqrt((G.node[uq]['x'] - G.node[u]['x'])**2 + (G.node[uq]['y'] - G.node[u]['y'])**2)
							user_key = alpha*cluster.pcap + (1-alpha)*d/max_dist
							heapq.heappush(H, (user_key, 'User', u))
				else: #if popped item is a user
					if temp[2] in length:
						p = length[temp[2]] #implement Dijkstra's here for now
						d = math.sqrt((G.node[uq]['x'] - G.node[temp[2]]['x'])**2 + (G.node[uq]['y'] - G.node[temp[2]]['y'])**2)
						f = alpha*p + (1-alpha)*d/max_dist
						if f<fk:
							del R[fk_id]
							R[temp[2]] = f
							#print(R)
							fk_id = max(R, key=R.get)
							fk = R[fk_id]
			else:
				break					
	return R
                
     
#--------------------Main Program--------------------#

if __name__ == '__main__':

	#creating the networkx graph
	G = nx.Graph()

	spatial = []
	features = []
	with open('spatial_main_sample_1.txt', 'r') as f:
		for line in f:
			words = line.split()
			spatial.append([int(words[0]), float(words[1])*111, float(words[2])*111, -1])
			features.append([float(words[1]), float(words[1])])
			G.add_node(int(words[0]) , x = float(words[1])*111, y = float(words[2])*111)
			min_x = min(min_x, float(words[1])*111)
			max_x = max(max_x, float(words[1])*111)
			min_y = min(min_y, float(words[2])*111)
			max_y = max(max_y, float(words[2])*111)

	max_dist = math.sqrt((max_x - min_x)**2 + (max_y - min_y)**2)

	with open('social_main_sample_1.txt', 'r') as f:
		for line in f:
			words = line.split()
			G.add_edge(int(words[0]) , int(words[1]) , weight=float(words[2]))
	
	#k-means clustering
	codebook, distortion = kmeans(features, num_clusters)
	code, dist = vq(features, codebook)

	print(codebook)

	#assigning cluster ids to users
	i = 0
	for u in spatial:
		u[3] = code[i]
		i += 1

	cluster_id = 0
	for centroids in codebook:
		clt = Cluster(cluster_id, centroids[0], centroids[1])
		clusters[cluster_id] = clt
		cluster_id +=1

	#assigning users to clusters and setting radius of each cluster
	for user in spatial:
		c_id = user[3]
		clusters[c_id].users.append(user[0])
		radius = clusters[c_id].radius
		clusters[c_id].radius = max(radius, math.sqrt((clusters[c_id].center_x - user[1])**2 + (clusters[c_id].center_y - user[2])**2))

	with open('main_sample_landmarks_1.txt', 'r') as f:
		for line in f:
			words = line.split()
			landmarks.append(int(words[0]))
		
	print('Short and long')
	findShortestAndLongest(G)

	#setting MINF for all clusters
	print('MINF')
	set_MINF(uq_id , G)
	
	

	start_time = time.clock()
	print(AIS(G, alpha, k, uq_id))
	time_taken = time.clock() - start_time
	print ("Time elapsed: {} seconds".format(time_taken))
