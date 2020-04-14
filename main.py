#!/usr/bin/env python3
import requests
import argparse
import parsing

parser = argparse.ArgumentParser(description='Identify a bird\'s specie by its sing')
parser.add_argument('-c', '--cont', help = 'Continent in which the sound has been recorded') #Default action = store
args = parser.parse_args()

#response = requests.get("https://www.xeno-canto.org/api/2/recordings?query=bearded+bellbird+q:A")

#print(response.json()['numRecordings'])

print(parsing.extendContinent('europe'))