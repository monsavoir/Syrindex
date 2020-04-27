#!/usr/bin/env python3
import requests
from collections import defaultdict
from collections import Counter
import json
import matplotlib.pyplot as plt
import numpy as np
import math as m

def extendContinent(continent) :
    file = open('./Continent/'+continent, 'r')
    countries = []
    for line in file:
        countries.append(line[:-1])
    file.close()
    return countries

def hasNumber(s):
    return any(char.isdigit() for char in s)

def numberRecordsPerCountry(response):
    return response.json()['numRecordings']

def numberSpeciesPerCountry(response):
    return response.json()['numSpecies']

def speciePerCountry(response):
    species = defaultdict(int)
    numPages = int(response.json()['numPages'])
    numRec = int(numberRecordsPerCountry(response))
    for j in range(numPages-1):
        for i in range(500):
            species[(response.json()['recordings'][i]['gen']+' '+response.json()['recordings'][i]['sp'])]+=1
        response = requests.get(response.request.url+'&page='+str(j+2))
    for i in range(numRec-500*(numPages-1)):
        species[(response.json()['recordings'][i]['gen']+' '+response.json()['recordings'][i]['sp'])]+=1
    return species

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

def retrieveDatabase(query):
    response = requests.get("https://www.xeno-canto.org/api/2/recordings?query="+query)
    return response

def listSpecies(outputfile):
    file = open(outputfile,'w')
    continent = ['africa','asia','europe','northamerica','oceania','southamerica']

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

def importJson(filename):
    with open('./Species/'+filename+'.json', 'r') as fp:
        data = json.load(fp)
    return data
'''
perContinent('asia')
perContinent('northamerica')
perContinent('southamerica')
perContinent('oceania')
perContinent('europe')
perContinent('africa')
'''

'''
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
    x = []
    for i in dic.values():
        x.append(m.log(i))
    x.sort()
    x = np.array(x)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x)
    ax.set(title = 'Visualisation du nombre d\'enregistrement pour chaque espèce (ordonné)',
        ylabel = 'Nombre d\'occurence (log)',
        xlabel = 'Indice du dictionnaire')
    plt.savefig('./Results/graphrefined.png')
    plt.show()

def tangent(xa,xb,ya,yb):
    return ((yb-ya)/(xb-xa))


grodico = 'grosdico'
betterVisuDic(grodico)