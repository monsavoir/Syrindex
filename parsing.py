#!/usr/bin/env python3

def extendContinent(continent) :
	file = open(continent, 'r')
	countries = []
	for line in file:
		countries.append(line[:-1])
	file.close()
	return countries

print(extendContinent('africa'), len(extendContinent('africa')))