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

INSTANCE_PRICES_LINUX_UK = {'m3.medium': 0.124,
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
VOLUME_PRICES_UK = {'storage': 0.055,
                    # ToDo: Get the number of requests
                    'millon-requests': 0.055,
                    'provisioned-storage': 0.138,
                    'provisioned-iops': 0.11,
                    'snapsot-storage': 0.095}

app = Bottle()

##########
# Get how much time has an instance been running
##########
def get_hours_running(launch_time):
  time_running = datetime.now() -\
                 datetime.strptime(launch_time[:-5], '%Y-%m-%dT%H:%M:%S')
  return int(time_running.total_seconds() / 3600)

##########
# Get how much time has a volume been existing
# param1: creation date as string
# Returns: time in months
##########
def get_months_existing(creation):
  time_running = datetime.now() -\
                 datetime.strptime(creation[:-5], '%Y-%m-%dT%H:%M:%S')
  return int(time_running.total_seconds() / 2592000)


##########
# 0 if null
##########
def zero_if_null(value):
  if value == None:
    value = 0
  return value

##########
# Cost of the type of instance
##########
def get_type_cost(instance_type):
  return INSTANCE_PRICES_LINUX_UK[instance_type]

##########
# Get the current instance cost since it is running
##########
def get_instance_cost(instance):  
  if instance.state == 'running':
    current_cost = get_hours_running(instance.launch_time) *\
                   get_type_cost(instance.instance_type)
  else:
    current_cost = 0
  return float(current_cost)

##########
# Get the instance cost per day
##########
def get_instance_cost_per_day(instance):
  return float(get_type_cost(instance.instance_type) * 24)

##########
# Get the instance cost per month
##########
def get_instance_cost_per_month(instance):
  return float(get_type_cost(instance.instance_type) * 30 * 24)

##########
# Get the instance cost per year
##########
def get_instance_cost_per_year(instance):
  return float(get_type_cost(instance.instance_type) * 365 * 24)

##########
# Get the current volume cost from its creation
##########
def get_volume_cost(volume):
  if volume.iops == None or volume.iops == 0:
    # ToDo: Get the number of requests
    current_cost = volume.size * VOLUME_PRICES_UK['storage'] *\
                   get_months_existing(volume.create_time)
  else:
    current_cost = (volume.size * VOLUME_PRICES_UK['provisioned-storage'] +\
                   volume.iops * VOLUME_PRICES_UK['provisioned-iops']) *\
                   get_months_existing(volume.create_time)
  return float(current_cost)

##########
# Get the volume cost per day
##########
def get_volume_cost_per_day(volume):
  if volume.iops == None or volume.iops == 0:
    # ToDo: Get the number of requests
    current_cost = volume.size * VOLUME_PRICES_UK['storage'] / 30
  else:
    current_cost = (volume.size * VOLUME_PRICES_UK['provisioned-storage'] +\
                    volume.iops * VOLUME_PRICES_UK['provisioned-iops']) / 30
  return float(current_cost)

##########
# Get the volume cost per month
##########
def get_volume_cost_per_month(volume):
  if volume.iops == None or volume.iops == 0:
    # ToDo: Get the number of requests
    current_cost = volume.size * VOLUME_PRICES_UK['storage']
  else:
    current_cost = (volume.size * VOLUME_PRICES_UK['provisioned-storage'] +\
                   volume.iops * VOLUME_PRICES_UK['provisioned-iops'])
  return float(current_cost)

##########
# Get the volume cost per year
##########
def get_volume_cost_per_year(volume):
  if volume.iops == None or volume.iops == 0:
    # ToDo: Get the number of requests
    current_cost = volume.size * VOLUME_PRICES_UK['storage'] * 12
  else:
    current_cost = (volume.size * VOLUME_PRICES_UK['provisioned-storage'] +\
                    volume.iops * VOLUME_PRICES_UK['provisioned-iops']) * 12 
  return float(current_cost)

##########
# Create the ec2 connection and make it ready to be used
##########
def _initialize_EC2Connection():
  AWS_ACCESS_KEY = boto.config.get('Credentials', 'aws_access_key_id')
  AWS_SECRET_KEY = boto.config.get('Credentials', 'aws_secret_access_key')
  regionEC2 = RegionInfo (name='eu-west-1',
                          endpoint='ec2.eu-west-1.amazonaws.com')
  return EC2Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY, region=regionEC2)

##########
# Get a custom tag from the instance
##########
def instance_getTag(tags, tag_key):
  if tags.has_key(tag_key):
    return tags[tag_key]
  else:
    return ''

############################################################################
# Routes
############################################################################
##########
# Provide the Client side content
##########
@app.route('/')
def hello():
  return static_file('index.html', 
                     root='./dist')

@app.route('/<filename:path>')
def send_static(filename):
    return static_file(filename, 
                       root='./dist')

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
      row['current_cost']     = get_instance_cost(instance)
      row['hour_cost']        = get_type_cost(instance.instance_type)
      row['day_cost']         = get_instance_cost_per_day(instance)
      row['month_cost']       = get_instance_cost_per_month(instance)
      row['year_cost']        = get_instance_cost_per_year(instance)
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
    row['iops']               = zero_if_null(volume.iops)
    row['current_cost']       = get_volume_cost(volume)
    row['day_cost']           = get_volume_cost_per_day(volume)
    row['month_cost']         = get_volume_cost_per_month(volume)
    row['year_cost']          = get_volume_cost_per_year(volume)
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
