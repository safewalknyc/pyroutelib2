#!/usr/bin/python
#----------------------------------------------------------------
# Routing for OSM data
#
#------------------------------------------------------
# Usage as library:
#   datastore = loadOsm('transport type')
#   router = Router(datastore)
#   result, route = router.doRoute(node1, node2)
#
# (where transport is cycle, foot, car, etc...)
#------------------------------------------------------
# Copyright 2007-2008, Oliver White
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------
import time
import sys
import math 
try:
  from .loadOsm import *
except (ImportError, SystemError):
  from loadOsm import *

class Router:
  def __init__(self):
    data = LoadOsm("foot")
    file_name = "lowertown.osm"
    data.loadOsm(file_name)
    riskFile= 'routing.csv'
    data.readInRisk(riskFile)
    self.data = data
    self.alpha=1
    self.beta=.1
  def distance(self,n1,n2):
    """Calculate distance between two nodes"""
    lat1 = self.data.rnodes[n1][0]
    lon1 = self.data.rnodes[n1][1]
    lat2 = self.data.rnodes[n2][0]
    lon2 = self.data.rnodes[n2][1]
    # TODO: projection issues
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    dist2 = dlat * dlat + dlon * dlon
    dist = math.sqrt(dist2)
    return(dist)
  
  def doRoute(self,start,end):
    """Do the routing"""
    self.searchEnd = end
    closed = [start]
    self.queue = []
    
    # Start by queueing all outbound links from the start node
    blankQueueItem = {'end':-1,'distance':0,'nodes':str(start)}
    print("Starting Node: " + str(start))
    try:
      for i, weight in self.data.routing[start].items():
        self.addToQueue(start,i, blankQueueItem, weight)
    except KeyError:
      return('no_such_node',[])

    # Limit for how long it will search
    count = 0
    while count < 1000000:
      count = count + 1
      try:
        nextItem = self.queue.pop(0)
      except IndexError:
        # Queue is empty: failed
        # TODO: return partial route?
        return('no_route',[])
      x = nextItem['end']
      if x in closed:
        continue
      if x == end:
        # Found the end node - success
        routeNodes = [int(i) for i in nextItem['nodes'].split(",")]
        return('success', routeNodes)
      closed.append(x)
      try:
        for i, weight in self.data.routing[x].items():
          if not i in closed:
            self.addToQueue(x,i,nextItem, weight)
      except KeyError:
        pass
    else:
      return('gave_up',[])
  
  def addToQueue(self,start,end, queueSoFar, weight = 1):
    """Add another potential route to the queue"""

    # getArea() checks that map data is available around the end-point,
    # and downloads it if necessary
    #
    # TODO: we could reduce downloads even more by only getting data around
    # the tip of the route, rather than around all nodes linked from the tip
    end_pos = self.data.rnodes[end]
    #self.data.getArea(end_pos[0], end_pos[1])
    
    # If already in queue, ignore
    for test in self.queue:
      if test['end'] == end:
        return
    if(weight == 0):
      return
    ##Weight will be "risk-value" precalculated by kernel clutsering and will be factors in
      #by (alpha*distance+beta*weight)^.5
     ##Distance precalculated on each edge and risk too
    alpha=1
    beta=.1
    #distance = alpha*self.distance(start,end)+beta*self.data.routing[start][end][1]
    distance = self.alpha*math.exp(self.data.routing[start][end][0])+self.beta*math.exp(self.data.routing[start][end][1])
    # Create a hash for all the route's attributes
    distanceSoFar = queueSoFar['distance']
    queueItem = { \
      'distance': distanceSoFar + distance,
      'maxdistance': distanceSoFar + self.distance(end, self.searchEnd),
      'nodes': queueSoFar['nodes'] + "," + str(end),
      'end': end}
    
    # Try to insert, keeping the queue ordered by decreasing worst-case distance
    count = 0
    for test in self.queue:
      if test['maxdistance'] > queueItem['maxdistance']:
        self.queue.insert(count,queueItem)
        break
      count = count + 1
    else:
      self.queue.append(queueItem)

  def getRoutes(self,source_lat,source_long,dest_lat,dest_long, alpha, beta):
    source_lat = float(source_lat)
    source_long = float(source_long)
    dest_lat = float(dest_lat)
    dest_long = float(dest_long)
    self.alpha = float(alpha)
    self.beta= float(beta)
 
    #print(source_lat, source_long, dest_lat, dest_long) 
    start = (source_lat, source_long)
    end = (dest_lat, dest_long)
    node1 = self.data.findNode(start[0],start[1])
    node2 = self.data.findNode(end[0],end[1])
    result, route = self.doRoute(node1, node2)
    
    steps=[]
    if result == 'success':
      # list the nodes

      for i in route:
        node = self.data.rnodes[i]
        #print("%f,%f" % (node[0],node[1]))
        steps.append([node[0],node[1]])
    else:
      print("Failed (%s)" % result)

    return steps 
