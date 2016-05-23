# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 18:07:00 2015

@authors: Sonya Tahir, Amit Talapatra, Wendy Zhang, Wei Zheng

This file contains the functions to select 5 indicators from the World Bank 
Education data, run k-means cluster and MDS analyses, and create csv files for 
mapping the data
"""

from bs4 import BeautifulSoup as bs
import requests as rq
from pandas.io import wb

from sklearn import preprocessing
import matplotlib.pyplot as plt
import numpy as np
import scipy.spatial.distance as dist
from sklearn import manifold  # multidimensional scaling

# Gets the list of 42 indicators under Education
def get_indicators():
    wb = rq.get("http://data.worldbank.org/indicator")
    soup = bs(wb.text)
    edu_text = soup.find('h3', text="Education")
    edu_tbl = edu_text.findNext('table')
    all_a = edu_tbl.findAll('a')
    indicators = [a["href"].split("/")[-1] for a in all_a ]
    descrs = [a.text for a in all_a]
    return (indicators, descrs)

# Gets the data for 2012 for a given indicator
def get_data(ind):
    d = wb.download(indicator=ind, country="all", start = 2012, end =2012)
    d = d[34:]
    return d

# Gets the 10 indicators with the least missing values
def get_bottom_10_miss(indicators):
    miss_counts = []
    for i, series in enumerate(indicators):
        d = get_data(series)
        miss_num = int(d.isnull().sum())
        miss_counts.append((miss_num, i))
    sorted_counts = sorted(miss_counts)
    bottom10 = sorted_counts[:10]
    return bottom10

# Creates a dictionary of the 10 indicators with the least missing values
def get_best_10():
    inds, descrs = get_indicators()
    best_10 = get_bottom_10_miss(inds)
    data_best_10  = []
    for s in best_10:
        d = {
            "indicator" : inds[s[1]],
            "data" : get_data(inds[s[1]]),  
            "desc" : descrs[s[1]]
        }
        data_best_10.append(d)
    return data_best_10

# Selects the five chosen indicators
def choose_5():
    best_10 = get_best_10()
    
    final_5 = ['SE.PRM.ENRL.TC.ZS', 'SE.PRM.ENRR', 'SL.UEM.TOTL.ZS','SL.TLF.TOTL.IN', 'SH.DYN.MORT']
    final_data = [s["data"] for s in best_10 if s["indicator"] in final_5 ]
    
    p1 = final_data[0]
    p1 = p1.fillna(p1.mean())
    for p in final_data[1:]:
        p = p.fillna(p.mean())
        p1 = p1.merge(p, left_index=True, right_index=True)
    return p1    
    
# Performs the MDS analysis
def mds_analysis():
    
    numpyMatrix = best_5.values
    
    indexes = list(best_5.index)  
    country_labels = []
    for i in range (len(indexes)):
        country_labels.append(indexes[i][0])
    
    labels = country_labels
    if choice == "2":
        numpyMatrix = numpyMatrix.transpose()  
        idx_labels = ['I1','I2','I3','I4','I5']
        labels = idx_labels
    
    np.set_printoptions(precision=3)
    distanceMatrix = dist.squareform(dist.pdist(numpyMatrix,"euclidean"))
    
    # apply the multidimensional scaling algorithm and plot the map
    mds_method = manifold.MDS(n_components = 2, random_state = 9999,\
        dissimilarity = 'precomputed') 
    mds_coordinates = mds_method.fit_transform(distanceMatrix) 
        
    # plot mds solution in two dimensions using city labels
    # defined by multidimensional scaling
    plt.figure()
    plt.scatter(mds_coordinates[:,0],mds_coordinates[:,1],\
        facecolors = 'blue', edgecolors = 'none')  # points in white (invisible)
    
    for label, x, y in zip(labels, mds_coordinates[:,0], mds_coordinates[:,1]):
        plt.annotate(label, (x,y), xycoords = 'data')
   
    plt.show()

# Creates a csv file merging the data from the five indicators into one scale
# for use in creating a map
def merge_5():
    numpyMatrix = best_5.values  

    indexes = list(best_5.index)  
    country_labels = []
    for i in range (len(indexes)):
        country_labels.append(indexes[i][0])
    
#   Normalizes the values for the five indicators
    df2 = preprocessing.scale(numpyMatrix)
    
#   Multiplies three of the normalized indicator values by -1 so positive 
#   values are 'good' factors for the countries
    for i in range (0,df2.shape[0]):   
        df2[i,0] = df2[i,0]*-1
    for i in range (0,df2.shape[0]):   
        df2[i,2] = df2[i,2]*-1
    for i in range (0,df2.shape[0]):   
        df2[i,4] = df2[i,4]*-1

#   Takes the mean of the five modified, normalized, indicators
    idx_means = np.mean(df2, axis=1)
    
    import csv
    data = zip(country_labels,idx_means)
    
#   Creates a csv file for the countries and values
    with open('merged.csv','w') as out:
        csv_out=csv.writer(out)
        for row in data:
            csv_out.writerow(row)
    
    
    
choice = raw_input("Enter 1 to plot countries, 2 to plot indicators.")
if choice == "1" or choice == "2":    
    best_5 = choose_5()  
    mds_analysis()
#    merge_5()
    
else:
    print "Invalid input."
    
    
