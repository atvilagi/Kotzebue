#Created: Fri Aug 16 13:43:35 2019
#By: mach

import gspread
import yaml
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('../puma-client.json', scope)
client = gspread.authorize(creds)

sheet = client.open("PuMA Units + SIMS").sheet1

units = sheet.col_values(6)
stoveTypes = sheet.col_values(5)
lat = sheet.col_values(15)
long = sheet.col_values(16)
header = [units[0], stoveTypes[0], lat[0], long[0]]

#print(header)
#print(units)

inventory = {}
for i in range(1, len(units)):
    inventory[units[i]] = {"Stove Type": stoveTypes[i], "Location": [float(lat[i]), float(long[i])]}

#print(inventory)        

print(yaml.dump(inventory))

file = open('../puma-inventory.yml', 'w')
file.write(yaml.dump(inventory))
file.close()