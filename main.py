#!/usr/bin/env python3

import argparse
import parsing
import os.path

def main():

    #Init Parser
    parser = argparse.ArgumentParser(description='Identify a bird\'s specie by its sing')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-c', '--continent', help = 'Continent where the recording was made') #Default action = store
    group.add_argument('-u', '--country', help = 'Country where the recording was made')
    args = parser.parse_args()

    '''
    #Check if the file exist
    if args.continent & os.path.isfile(args.continent.lower()):
        print(parsing.extendContinent(args.continent.lower()))
    else :
        print('Erreur : fichier du continent',args.continent,'introuvable')

    if args.country & os.path.isfile(args.country.lower()):
        print(parsing.extendContinent(args.country.lower()))
    else :
        print('Erreur : fichier du continent',args.country,'introuvable')
    '''

    if args.country :
        if parsing.hasNumber(args.country):
            raise TypeError("Country must be a string")
        parsing.retrieveDatabase('cnt:'+args.country)


    if args.continent:
        if parsing.hasNumber(args.continent):
            raise TypeError("Continent must be a string")
        try :
            print(args.continent)
            for country in parsing.extendContinent(args.continent.lower()):
                if parsing.retrieveDatabase('cnt:'+country) == '0':
                    print(country)
                #print(country)
                #print(parsing.retrieveDatabase('cnt:'+country))
        except :
            print('Error: File',args.continent,'not found')

if __name__ == '__main__' :
    main()