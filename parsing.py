#!/usr/bin/env python3
import requests
from collections import defaultdict

def extendContinent(continent) :
    file = open(continent, 'r')
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
            species[response.json()['recordings'][i]['gen'],response.json()['recordings'][i]['sp']]+=1
        response = requests.get(response.request.url+'&page='+str(j+2))
    for i in range(numRec-500*(numPages-1)):
        species[response.json()['recordings'][i]['gen'],response.json()['recordings'][i]['sp']]+=1
    return species

def perContinent(query):
    countR = 0
    countS = 0
    countries = extendContinent(query.lower())
    for country in countries :
        tempS = 0
        tempR = 0
        print(country)
        response = retrieveDatabase('cnt:'+country)
        speciePerCountry(response)
        tempS = numberSpeciesPerCountry(response)
        tempR = numberRecordsPerCountry(response)
        print('Species',tempS)
        countS += int(tempS)
        print('Records',tempR)
        countR += int(tempR)
    return (countS,countR)

def retrieveDatabase(query):
    response = requests.get("https://www.xeno-canto.org/api/2/recordings?query="+query)
    return response

def listSpecies(outputfile):
    file = open(outputfile,'w')
    continent = ['africa','asia','europe','northamerica','oceania','southamerica']

'''
response = retrieveDatabase('cnt:denmark')
dic = speciePerCountry(response)
print(sorted(dic.values(),reverse=True))
print(numberRecordsPerCountry(response))
print(numberSpeciesPerCountry(response))
'''
perContinent('europe')