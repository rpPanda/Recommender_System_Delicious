from __future__ import division
import csv
from math import *
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
import tkinter as tk
from tkinter import messagebox
from tkinter import *
from sklearn.cluster import DBSCAN
from sklearn import metrics

class User():
	id = 0
	bookmarks = {}
	tags = {}
	friends = {}
	count = 0
	def __init__(self,id):
		self.id = id
		self.tags = {}
		self.bookmarks = {}
		self.friends ={}
		self.count = 0

users = {}

def biclustering(matrix):
	model = SpectralBiclustering()
	model.fit(matrix)
	fit_data = data[np.argsort(model.row_labels_)]
	fit_data = fit_data[:, np.argsort(model.column_labels_)]
	return fit_data
# df = pd.read_csv('dataset/user_taggedbookmarks.dat', 
#                  sep='\t', 
#                  usecols=[2])
# print(df)

# db=DBSCAN(eps=0.01, min_samples=1).fit(df)

# labels = db.labels_
# print(labels)
# n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

# print('Estimated number of clusters: %d' % n_clusters_)

def read_data():
	for line in open('dataset/user_taggedbookmarks.dat'):
		fields = line.split('\t')
		uid = fields[0]
		bid = fields[1]
		tid = fields[2]

		if not uid in users:
			users[uid] = User(uid)

		if not tid in users[uid].tags:
			users[uid].tags[tid] = 0
		users[uid].count += 1
		users[uid].tags[tid] += 1

		users[uid].bookmarks[bid] = 1


read_data()



class Bookmark():
	id = 0
	tags = {}
	def __init__(self,id):
		self.id = id
		self.tags = {}

bookmarks = {}
def read_bookmarks():
	for line in open('dataset/bookmark_tags.dat'):
		fields = line.split('\t')
		bid = fields[0]
		tid = fields[1]
		weight = fields[2]
		if(not bid in bookmarks):
			bookmarks[bid] = Bookmark(bid)
		bookmarks[bid].tags[tid] = fields[2]

read_bookmarks()
print('Bookmarks Read')

#Getting similarity between 2 bookmarks
def book_sim(i,j):
	if(i in bookmarks and j in bookmarks):
		intersection = len(list( (set(bookmarks[i].tags.keys()) & set(bookmarks[j].tags.keys())) ))
	
		union = sqrt(len(list( (set(bookmarks[i].tags.keys())))))*len(list( (set(bookmarks[j].tags.keys()))))
#		union =len(list( (set(bookmarks[i].tags.keys()) | set(bookmarks[j].tags.keys())) ))
		sim=intersection/union
		return sim
	
	else:
		return -1



S = []
n = 1867
total_tags = 53388
A = []
alpha = 0.1
beta = 0.1

def ts(key1,key2):
	#calculate mean_vu and mean_vm
	vu_mean = vm_mean = 0
	for key in users[key1].tags:
		vu_mean += users[key1].tags[key]
	vu_mean = vu_mean/total_tags
	for key in users[key2].tags:
		vm_mean += users[key2].tags[key]
	vm_mean = vm_mean/total_tags

	#Pearsons formula to calulate similarity
	numerator = 0
	den1 = den2 = 0
	for key in users[key1].tags:
		if key in users[key2].tags:
			#vuj, vmj are tag based user profiles for the tag 'key'
			vuj = users[key1].tags[key]/users[key1].count
			vmj = users[key2].tags[key]/users[key2].count
			numerator += ( (vuj - vu_mean)*(vmj - vm_mean) )
			den1 += pow((vuj-vu_mean),2)
			den2 += pow((vmj-vm_mean),2)
	#print(key1,den1,den2)
	den1 = den1**(1.0/2)
	den2 = den2**(1.0/2)
	if(den1 != 0 and den2 != 0):
		ans = numerator/(den1*den2)
		return ans
	else:
		return 0

# db1=DBSCAN(eps=2, min_samples=4).fit_predict(X)


def ui(key1,key2):
	numerator = 0
	den = len(users[key1].bookmarks)
	for key in users[key1].bookmarks:
		if key in users[key2].bookmarks:
			numerator += 1

	ans = numerator/den
	return ans



#Store contacts of users
contacts = {}
for line in open('dataset/user_contacts.dat'):
	fields = line.split('\t')
	if(not ( ((fields[0],fields[1]) in contacts) or ((fields[1],fields[0])in contacts) )):
			contacts[(fields[0],fields[1])] = 1



#resources = {}

"""
booktags = {}
reader = csv.reader(open('booktags.csv', 'r'))
for row in reader:
	k, v = row
	booktags[k] = v




tagsim = {}
def ressim():
	flag = 0
	for key1,value1 in booktags.items():
		fields1 = "a"
		fields2 = "b"
		union = 0
		intersection = 0
		for key2,valu1e2 in booktags.items():
			if(key1 != key2):
				fields1=key1.split("'")
				fields2=key2.split("'")
				union = union + 1
				if(booktags[key1] == booktags[key2]):
					intersection += 1
					flag = 1		#just to test for 1 pair

		tagsim[(fields1[1],fields2[1])] = intersection/union
		if(flag):
			break
"""

total_usrs = len(users)
true_positive = 0
true_recs = 0
g_novel = 0
g_satisfied = 0
g_serendipitous = 0
g_stf_denom = 0
g_seren_denom = 0
g_novel_denom = 0

def friend_reccomder(key1):
	counter = 0
	tr = 0
	tp = 0
	satisfied = 0
	satisfied_denom = 0
	novel = 0
	serendipitous = 0
	seren_denom = 0
	novel_denom = 0
	if not key1 in users:
		A.append(0)
	
	#for key1 in users:
	else:
		counter += 1
		#print(''+str(counter)+'/'+str(total_usrs))
		u = users[key1]
		flag = 0
		recom = 0
		for key2 in users:
			if(key1 != key2):
				m = users[key2]
				#sim = ts(key1,key2)
				user_interest1 = ui(key1,key2)
				user_interest2 = ui(key2,key1)
				#print(sim)
				if(user_interest1 > beta or user_interest2 > beta):
					#this friend is recommended to user (key1)
					# S.append((key1,key2))

					tr += 1		#total recommendations
					recom = 1	#current friend is recommended
					#print("tr %s"%(tr))
					#To check if it is a positive contact 
					if( ( (key1,key2) in contacts ) or ( (key2,key1) in contacts)):
						tp += 1
						flag = 1

					#To check if recommended bookmarks are serendipitous 
					for i in users[key2].bookmarks:
						check = 1
						for j in users[key1].bookmarks:
							sim = book_sim(i,j)
							if(sim>0):
								if(not key2 in A):
									A.append((key2))
								check = 0
								break
						if(check==1):
							serendipitous += 1
						seren_denom += 1

		#To check if recommended bookmarks are novel
	return A



def bookmark_reccomder(key1):
	C=[]
	alpha1 = 0.5
	while (not(len(C))):
		if(not key1 in users):
			C.append(0)
		for key2 in users:
			if( ( (key1,key2) in contacts ) or ( (key2,key1) in contacts)):
				for i in users[key2].bookmarks:
						for j in users[key1].bookmarks:
							sim = book_sim(i,j)
							if(sim>alpha1):
								if(not i in C):
									C.append(i)
		alpha1-=0.1
	
	return C
	
A = friend_reccomder('1')
C=bookmark_reccomder('8')
def ans_in_str(C):
	D=""
	for i in range(0,len(C)):
		for line in open('dataset/bookmarks.dat',encoding = "ISO-8859-1"):
			fields = line.split('\t')
			bid = fields[0]
			burl = fields[5]
			if(C[i]==0):
				return "User not found"
			if(bid == C[i]):
				D=D+burl;
	return D	
print(A)
def frs_in_str(C):
	D=""
	for i in range(0,len(C)):
		if(C[i]==0):
			return "User not found"
		D=D+str(C[i])+'\n'
	return D

# print(frs_in_str(A))

#print(C)
# precision = true_positive/true_recs
# percentage_satisfied = g_satisfied/g_stf_denom
# novelty = g_novel/g_novel_denom
# serendipity = g_serendipitous/g_seren_denom

# print("Satisfied Users: %s " %(percentage_satisfied))
# print("Precision: %s " %(precision))
# print("Novelty: %s " %(novelty))
# print("Serendipity: %s" %(serendipity))

# messagebox.askokcancel("Title","The application will be closed")
# messagebox.askyesno("Title","Do you want to save?")
# messagebox.askretrycancel("Title","Installation failed, try again?")
from tkinter import *
from tkinter.messagebox import *	
def show_answer():
    # Ans = int(num1.get()) + int(num2.get())
    C=bookmark_reccomder(str(num1.get()))
    ans=ans_in_str(C)
    print(ans)
    blank.delete(1.0,END)
    blank.insert(1.0,str(ans))

def show_friend():
    C=friend_reccomder(str(num1.get()))
    ans=frs_in_str(C)
    print(ans)
    blank.delete(1.0,END)
    blank.insert(1.0,str(ans))


main = Tk()


Label(main, text = "Enter Num 1:").grid(row=0)
# Label(main, text = "Enter Num 2:").grid(row=1)
Label(main, text = "Bookmark \n Reccomendations").grid(row=2)


num1 = Entry(main)
# num2 = Entry(main)
blank = Text(main, width = 40, height = 20,font=("Courier", 14))


num1.grid(row=0, column=1)
# num2.grid(row=1, column=1)
blank.grid(row=2, column=1)



Button(main, text='Quit', command=main.destroy).grid(row=4, column=0, sticky=W, pady=4)
Button(main, text='Bookmarks', command=show_answer).grid(row=4, column=1, sticky=W, pady=4)
Button(main, text='Friends', command=show_friend).grid(row=4, column=1, pady=4)

mainloop()