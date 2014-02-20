#! /usr/bin/env python
#################################################
# Tool used for the inventory of ec2 instances
#
# Author: Alejandro Inestal Garcia
#################################################

import sys
from datetime import datetime, timedelta, date
from boto import boto
from boto import ec2
from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import RegionInfo
#from boto.emr.connection import EmrConnection
from bottle import *
import json

app = Bottle()

############################################################################
# Generic functions
############################################################################
# class EnableCors(object):
#   name = 'enable_cors'
#   api = 2

#   def apply(self, fn, context):
#     def _enable_cors(*args, **kwargs):
#       # set CORS headers
#       response.headers['Access-Control-Allow-Origin'] = '*'
#       response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
#       response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

#       if bottle.request.method != 'OPTIONS':
#         # actual request; reply with the actual response
#         return fn(*args, **kwargs)

#     return _enable_cors

def get_time_running(launch_time):
  time_running = datetime.now() - datetime.strptime(launch_time[:-5], '%Y-%m-%dT%H:%M:%S')
  time_running = int(time_running.total_seconds() / 3600)
  return time_running



def get_type_cost(instance_type):
  return 1

def _initialize_EC2Connection():
  AWS_ACCESS_KEY = boto.config.get('Credentials', 'aws_access_key_id')
  AWS_SECRET_KEY = boto.config.get('Credentials', 'aws_secret_access_key')
  regionEC2 = RegionInfo (name='eu-west-1',
                          endpoint='ec2.eu-west-1.amazonaws.com')
  return EC2Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY, region=regionEC2)

def instance_getTag(tags, tag_key):
  if tags.has_key(tag_key):
    return tags[tag_key]
  else:
    return ''

############################################################################
# Routes
############################################################################
@app.route('/')
def hello():
  return static_file('index.html', 
                     root='/home/ainestal/Development/awsCostMonitor/dist')

@app.route('/<filename:path>')
def send_static(filename):
    return static_file(filename, 
                       root='/home/ainestal/Development/awsCostMonitor/dist')

@app.route('/api/all')
def get_all_instances():
  instancesList = json.loads('[]')
  reservations = ec2Connection.get_all_reservations()
  for reservation in reservations:
    for instance in reservation.instances:      
      row = json.loads('{}')
      row['id']               = instance.id
      row['name']             = instance_getTag(instance.tags, 'Name')
      row['instance_type']    = instance.instance_type
      row['root_device_type'] = instance.root_device_type
      row['state']            = instance.state
      row['key_name']         = instance.key_name
      row['launch_time']      = instance.launch_time
      current_cost = int(get_time_running(row['launch_time'])) * \
                     int(get_type_cost(row['instance_type']))
      row['current_cost']     = current_cost
      # Custom user tags
      row['Description']      = instance_getTag(instance.tags, 'Description')
      row['Environment']      = instance_getTag(instance.tags, 'Environment')
      row['Contact']          = instance_getTag(instance.tags, 'Contact')
      row['Workhours']        = instance_getTag(instance.tags, 'Workhours')
      row['CostGroup']        = instance_getTag(instance.tags, 'CostGroup')
      instancesList.append(row)
  instancesList = json.dumps(instancesList)
  return instancesList

@error(404)
def error404(error):
  return 'Error 404. "' + error + '" does not exist in our system'

############################################################################
# Main
############################################################################
if __name__ == "__main__":
  ec2Connection = _initialize_EC2Connection()
  #ec2Connection = _initialize_EC2Connection()
  #self.emrConnection = _initialize_EmrConnection()
  run(app, host="0.0.0.0", port = 8080)
