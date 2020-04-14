#!/usr/bin/env python3
import requests

response = requests.get("https://www.xeno-canto.org/api/2/recordings?query=bearded+bellbird+q:A")

print(response.json()['numRecordings'])
