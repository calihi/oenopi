import os
import glob
from pymongo import MongoClient
import datetime
from datetime import timedelta
import time

import pprint

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

client = MongoClient('mongodb://localhost:27017/')
db = client.oenopi
wines = db.wines

def read_temp_raw():
 f = open(device_file, 'r')
 lines = f.readlines()
 f.close()
 return lines

def read_temp():
 lines = read_temp_raw()
 while lines[0].strip()[-3:] != 'YES':
   time.sleep(0.2)
   lines = read_temp_raw()
 equals_pos = lines[1].find('t=')
 if equals_pos != -1:
   temp_string = lines[1][equals_pos+2:]
   temp_c = float(temp_string) / 1000.0
   return temp_c

while True:
    isoDate = datetime.datetime.now()
    temp = read_temp()
    wines.update(
                    { "tank": 1 },
                    { "$push": { "temperatureHistory": {"readingDate" : isoDate,  "temperature" : temp }
                        }, "$set" : { "updated" : isoDate }
                    })
    # Test result
    # pprint.pprint(wines.find_one({"tank": 1}))
    
    time.sleep(3600)
