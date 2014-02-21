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

INSTANCE_PRICES = {'m3.medium': 0.124,
                  'm3.large':  0.248,
                  'm3.xlarge': 0.495,
                  'm3.2xlarge':  0.990,
                  'm1.small':  0.065,
                  'm1.medium': 0.130,
                  'm1.large':  0.260,
                  'm1.xlarge': 0.520,
                  'c3.large':  0.171,
                  'c3.xlarge': 0.342,
                  'c3.2xlarge':  0.683,
                  'c3.4xlarge':  1.366,
                  'c3.8xlarge':  2.732,
                  'c1.medium': 0.165,
                  'c1.xlarge': 0.660,
                  'cc2.8xlarge': 2.700,
                  'g2.2xlarge':  0.702,
                  'cg1.4xlarge': 2.36,
                  'm2.xlarge': 0.460,
                  'm2.2xlarge':  0.920,
                  'm2.4xlarge':  1.840,
                  'cr1.8xlarge': 3.750,
                  'i2.xlarge': 0.938,
                  'i2.2xlarge':  1.876,
                  'i2.4xlarge':  3.751,
                  'i2.8xlarge':  7.502,
                  'hs1.8xlarge': 4.900,
                  'hi1.4xlarge': 3.100,
                  't1.micro':  0.020}

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
  return INSTANCE_PRICES[instance_type]

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
def get_all():
  instancesList = get_all_instances()
  volumesList   = get_all_volumes()
  return json.dumps([json.loads(instancesList),json.loads(volumesList)])

@app.route('/api/instances')
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
      row['ebs_optimized']    = instance.ebs_optimized
      row['state']            = instance.state
      row['key_name']         = instance.key_name
      row['launch_time']      = instance.launch_time
      current_cost = get_time_running(row['launch_time']) * get_type_cost(row['instance_type'])
      if row['state'] == 'running':
        row['current_cost']   = round(current_cost, 2)
      else:
        row['current_cost']   = 'N/A. Stopped instance'
      # Custom user tags
      row['Description']      = instance_getTag(instance.tags, 'Description')
      row['Environment']      = instance_getTag(instance.tags, 'Environment')
      row['Contact']          = instance_getTag(instance.tags, 'Contact')
      row['Workhours']        = instance_getTag(instance.tags, 'Workhours')
      row['CostGroup']        = instance_getTag(instance.tags, 'CostGroup')
      instancesList.append(row)
  instancesList = json.dumps(instancesList)
  return instancesList

@app.route('/api/volumes')
def get_all_volumes():
  volumesList = json.loads('[]')
  volumes = ec2Connection.get_all_volumes()
  for volume in volumes:
    row = json.loads('{}')
    row['id']                 = volume.id
    row['create_time']        = volume.create_time
    row['volume_status']      = volume.status
    row['size']               = volume.size
    row['snapshot_id']        = volume.snapshot_id
    row['zone']               = volume.zone
    row['type']               = volume.type
    row['iops']               = volume.iops
    row['instance_id']        = volume.attach_data.instance_id
    row['instance_status']    = volume.attach_data.status
    row['attach_time']        = volume.attach_data.attach_time
    row['device']             = volume.attach_data.device
    volumesList.append(row)
  volumesList = json.dumps(volumesList)
  return volumesList

@error(404)
def error404(error):
  return 'Error 404. '' + error + '' does not exist in our system'

############################################################################
# Main
############################################################################
if __name__ == '__main__':
  ec2Connection = _initialize_EC2Connection()
  #ec2Connection = _initialize_EC2Connection()
  #self.emrConnection = _initialize_EmrConnection()
  run(app, host='0.0.0.0', port = 8080)
