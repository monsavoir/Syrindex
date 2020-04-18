#!/usr/bin/env python3

import argparse
import parsing
import os.path

def main():

    #Init Parser
    parser = argparse.ArgumentParser(description='Identify a bird\'s specie by its sing')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-c', '--continent', help = 'Continent where the recording was made') #Default action = store
    group.add_argument('-u', '--country', help = 'Country where the recording was made, (remplace space by underscore)')
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
            raise TypeError("Country cant contain number")
        print(parsing.numberPerCountry('cnt:'+args.country))


    if args.continent:
        if parsing.hasNumber(args.continent):
            raise TypeError("Continent cant contain number")
        try :
            print(args.continent)
            print(parsing.numberPerContinent(args.continent))
        except :
            print('Error: File',args.continent,'not found')

    

if __name__ == '__main__' :
    main()