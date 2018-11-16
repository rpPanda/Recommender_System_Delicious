import csv
from math import *
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.cluster.bicluster import SpectralBiclustering
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans

df=pd.read_csv('dataset/user_contacts-timestamps.dat', 
                 sep='\t', 
                 usecols=[0,1])
 
DF=pd.read_csv('dataset/user_taggedbookmarks.dat', 
                 sep='\t', 
                 usecols=[0,1])

# df=df.drop_duplicates(subset=None, keep='first', inplace=False)
#print(df)
df1=df.drop_duplicates(subset='userID', keep='first', inplace=False)
df2=df.drop_duplicates(subset='contactID', keep='first', inplace=False)

d=df1.values
e=df2.values
f=df.values
g=DF.values
d=np.unique(np.concatenate((d,e),0))
d=np.unique(np.concatenate((d,g[:,0]),0))
bb=np.unique(g[:,1])
uid = {}
s=d.shape[0]
sb=bb.shape[0]
print(s,sb)
for i in range(0,s):
   uid[d[i]]=i
bid = {}
for j in range(0,g.shape[0]):
    bid[g[j][1]]=i


UxI = np.zeros((U.shape[0],I.shape[0]), dtype='int32')
for x in range(0,data.shape[0]):
    UxI[uid[index[x][0]]][bid[index[x][1]]]=1

f_data=biclustering(UxI)



print(U)
pca = PCA(n_components=100)
pca.fit(U)
U_pca = pca.transform(U)
print(U_pca)

kmeans = KMeans(n_clusters=10, random_state=0).fit(U_pca)
print(kmeans.labels_.shape)
np.savetxt("file",kmeans.labels_,newline=" ")