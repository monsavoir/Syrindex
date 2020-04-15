#!/usr/bin/env python3
import requests

def extendContinent(continent) :
    file = open(continent, 'r')
    countries = []
    for line in file:
        countries.append(line[:-1])
    file.close()
    return countries

def hasNumber(s):
    return any(char.isdigit() for char in s)

def retrieveDatabase(query):
    response = requests.get("https://www.xeno-canto.org/api/2/recordings?query="+query)
    return response.json()['numRecordings']