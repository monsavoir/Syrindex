#!/usr/bin/env python3
import requests
from collections import defaultdict
from collections import Counter
import collections
import json
import matplotlib.pyplot as plt
import numpy as np
import math as m
from scipy.interpolate import UnivariateSpline
import time
import os
import urllib.request
from pathlib import Path
from math import log
from mutagen.mp3 import MP3



def numberRecordsPerCountry(response):
    return response.json()['numRecordings']

def numberSpeciesPerCountry(response):
    return response.json()['numSpecies']

def speciePerCountry(response):
    species = {}
    numPages = int(response.json()['numPages'])
    numRec = int(numberRecordsPerCountry(response))
    for j in range(numPages-1):
        for i in range(500):
            if response.json()['recordings'][i]['gen']+' '+response.json()['recordings'][i]['sp'] in species:
                species[(response.json()['recordings'][i]['gen']+' '+response.json()['recordings'][i]['sp'])].append(response.json()['recordings'][i]['id'])
            else:
                species[(response.json()['recordings'][i]['gen']+' '+response.json()['recordings'][i]['sp'])]=[response.json()['recordings'][i]['id']]
        response = requests.get(response.request.url+'&page='+str(j+2))
    for i in range(numRec-500*(numPages-1)):
            if response.json()['recordings'][i]['gen']+' '+response.json()['recordings'][i]['sp'] in species:
                species[(response.json()['recordings'][i]['gen']+' '+response.json()['recordings'][i]['sp'])].append(response.json()['recordings'][i]['id'])
            else:
                species[(response.json()['recordings'][i]['gen']+' '+response.json()['recordings'][i]['sp'])]=[response.json()['recordings'][i]['id']]
    # with open('./Species/France.json', 'w') as fp:
    #     jason = json.dump(species, fp)
    return species

def retrieveDatabase(query):
    response = requests.get("https://www.xeno-canto.org/api/2/recordings?query="+query)
    return response


def importJson(filename):
    with open('./Species/'+filename+'.json', 'r') as fp:
        data = json.load(fp)
    return data

start_time = time.time()

'''
def listSpecies(outputfile):
    file = open(outputfile,'w')
    continent = ['africa','asia','europe','northamerica','oceania','southamerica']

def perContinent(query):
    filename = 'species'+query
    countries = extendContinent(query.lower())
    species = defaultdict(int)
    for country in countries :
        print(country)
        response = retrieveDatabase('cnt:'+country)
        species = Counter(species) + Counter(speciePerCountry(response))
    with open('./Species/'+filename+'.json', 'w') as fp:
        jason = json.dump(species, fp)
    return


def extendContinent(continent) :
    file = open('./Continent/'+continent, 'r')
    countries = []
    for line in file:
        countries.append(line[:-1])
    file.close()
    return countries

def hasNumber(s):
    return any(char.isdigit() for char in s)

def mergeDic(listdic):
    species = defaultdict(int)
    for i in listdic:
        with open('./Species/species'+i+'.json','r') as fp:
            specie = json.load(fp)
        species = Counter(species) + Counter(specie)
    species = dict(species)
    print(len(species))
    print(sum(species.values()))
    with open('./Species/grosdico.json','w') as fp:
        json.dump(species, fp)
    return

response = retrieveDatabase('cnt:France')
dico = speciePerCountry(response)
print(dico)
print(len(dico))
print(sum(i for i in dico.values()))
print("--- %s seconds ---" % (time.time() - start_time))


perContinent('asia')
perContinent('northamerica')
perContinent('southamerica')
perContinent('oceania')
perContinent('europe')
perContinent('africa')
continent = ['africa','asia','europe','northamerica','oceania','southamerica']
mergeDic(continent)
'''

def visuDic(filename):
    dic = importJson(filename)
    x = []
    for i in dic.values():
        x.append(i)
    x.sort()
    x = np.array(x)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x)
    ax.set(title = 'Visualisation du nombre d\'enregistrement pour chaque espèce (ordonné)',
        ylabel = 'Nombre d\'occurence',
        xlabel = 'Indice du dictionnaire')
    plt.savefig('./Results/graphbrute.png')
    plt.show()

def betterVisuDic(filename):
    dic = importJson(filename)
    y = []
    for i in dic.values():
        y.append(i)
    y.sort()
    y = np.array(y)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(y)
    ax.set(title = 'Visualisation du nombre d\'enregistrement pour chaque espèce (ordonné)',
        ylabel = 'Nombre d\'occurence',
        xlabel = 'Indice du dictionnaire')
    #plt.savefig('./Results/graphbrute.png')
    plt.show()
    '''
    # x = [0]
    y=[]
    for i in range(1,len(x)):
         y.append(m.log(x[i]))
    y = np.array(y)
    x = np.array(x)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(y)
    ax.set(title = 'Visualisation du nombre d\'enregistrement pour chaque espèce (ordonné)',
        ylabel = 'Nombre d\'occurence',
        xlabel = 'Indice du dictionnaire')
    #plt.savefig('./Results/graphlog.png')
    plt.show()
    '''
    x = [i for i in range(len(y))]
    print(x)
    print(y)
    xx = np.arange(1,len(x),0.1)

    y_spl = UnivariateSpline(x, y, k = 3)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    # ax1.plot(x[2000:],y[2000:],'ro', ms = 0.1)
    ax.plot(xx,y_spl(xx),'b')
    ax.plot(x, y, 'ro', label = 'Data', ms = 0.5)
    ax.set(
         ylabel = 'Nombre d\'occurence',
         xlabel = 'Indice du dictionnaire')
    plt.show()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    y_spl = y_spl.derivative(n=2)
    x_range = np.linspace(x[0],x[-1],1000)
    ax.plot(x,log(y_spl(x)),'g')
    # ax2.set(title = 'Dérivé seconde de la fonction',
    #     ylabel = 'y',
    #     xlabel = 'x')
    # plt.savefig('./Results/graphrefined.png')
    plt.show()

#betterVisuDic('France')
#print("--- %s seconds ---" % (time.time() - start_time))

def parseDicFrance(threshold):
    dico = importJson('France_ver2')
    newdico = {}
    print(dico)
    print(len(dico.keys()))
    for specie in dico.keys():
        if len(dico[specie])>threshold:
            newdico[specie] = dico[specie]
    print(len(newdico.keys()))
    newdico.pop('Sonus naturalis', None)
    with open('./Species/FranceTest.json', 'w') as fp:
        jason = json.dump(newdico, fp)

    return

def getData(query):
    dico = importJson(query)
    print(dico.keys())
    print(len(dico.keys()))
    for i in dico.values():
        print(i)
        for j in i:
            print(j)
            r = requests.get("http://www.xeno-canto.org/"+str(j)+"/download")
            urllib.request.urlretrieve(r.url, "Records10/"+str(j)+".mp3")    
    return


#response = retrieveDatabase('cnt:France type:song q:A')
#speciePerCountry(response)
#betterVisuDic('France')
#parseDicFrance(15)
#getData('France')


def createCSV():
    dico = importJson('France10')
    filename = './Song10.csv'
    CSV = open(filename, 'w')
    print('specie,filename,label,duration')
    for i in dico:
        for j in dico[i]:
            print(i+','+j)
            CSV.write(i+','+j+'\n')
    CSV.close()
    return

def getTest(query):
    dico = importJson(query)
    for i in dico.keys():
        if not os.path.exists("Test/"+i.replace(" ","_")):
            os.makedirs("Test/"+i.replace(" ","_"))
        response = retrieveDatabase(i)
        speciePerCountry(response)
        k = 0
        j = 0
        while j < 10:
            if response.json()['recordings'][k]['cnt']!='France':
                ID = response.json()['recordings'][k]['id']
                r = requests.get("http://www.xeno-canto.org/"+str(ID)+"/download")
                urllib.request.urlretrieve(r.url, "Test/"+i.replace(" ","_")+"/"+str(ID)+".mp3")  
                j += 1
            k += 1
    return

#getData('FranceTest')
#getTest('FranceTest')

def createCode():
    nom = 'Espece.txt'
    fichier = open(nom,'r')
    code = open('code.txt','w')
    j=0
    for i in fichier:
        code.write(i[:-1]+' '+str(j)+'\n')
        j+=1
    fichier.close()
    code.close()

'''
dire = Path('./Test/')
fichier = open('./test.csv','w')
all_dir =[x for x in dire.iterdir() if x.is_dir()]
for i in all_dir:
    for f in listdir(i):
        fichier.write(str(i)[5:]+','+f+'\n')
fichier.close()
'''

def checkDico(filename):
    dico = importJson(filename)
    dic2 = {}
    for i in dico:
        dic2[i]=len(dico[i])
    dic2 = {k: v for k, v in sorted(dic2.items(), key=lambda item: item[1])}
    x=dic2.keys()
    x = list(x)[-10:]
    newdico = {}
    for i in x:
        newdico[i]=dico[i]
    with open('./Species/France10.json', 'w') as fp:
        jason = json.dump(newdico, fp)

def codeLabel():
    CSV = open('Song10.csv','r')
    inp = open('code.txt','r')
    out = open('FSong10.csv','w')
    j=0
    l = []
    out.write('specie,filename,code,label,duration\n')
    for i in inp:
        k=[i[:-1],i[:3]+i[-3:-1],str(j)]
        l.append(k)
        j+=1
    for n in CSV:
        for m in range(len(l)):
            if n.split(',')[0]==l[m][0]:
                out.write(n[:-1]+'.mp3,'+l[m][1]+','+l[m][2]+','+str(MP3('./Records10/'+str(n.split(',')[1][:-1]+'.mp3')).info.length)+'\n')
                break
    out.close()
    inp.close()
    CSV.close()             



#checkDico('FranceTest')
#createCSV()
getData('France10')
codeLabel()