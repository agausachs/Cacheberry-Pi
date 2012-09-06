#!/usr/bin/env python
import os
import sys
import math
import gislib
from pyspatialite import dbapi2 as db
from lcdproc.server import Server
import unicodedata
import time
import gps

def bearing(start, target):
  lat1, lon1 = map(math.radians, start)
  lat2, lon2 = map(math.radians, target)
  dLon = lon2-lon1
  y = math.sin(dLon) * math.cos(lat2)
  x = math.cos(lat1)*math.sin(lat2) - \
      math.sin(lat1)*math.cos(lat2)*math.cos(dLon)
  return (math.degrees(math.atan2(y, x))+180) % 360

def humanizeBearing(bearing):
  # symbols = ['N','NE','E','SE','S','SW','W','NW']
  symbols = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
  step = 360.0 / len(symbols) 
  for i in range(len(symbols)):
    min = (i*step - .5*step) % 360
    max = (i*step + .5*step) % 360
    if bearing > min and bearing <= max:
        return symbols[i]

class CacheDatabase:
  def __init__(self, dbfile):
    self.__conn = db.connect(dbfile)
  
  def findNearest(self, lat, lon):
    cur = self.__conn.cursor()

    # SQL to define a circle around the home point with a given radius
    radius = 3000.0 / 111319 #3km
    circle = 'BuildCircleMbr(%f, %f, %f)' % (lat, lon, radius)

    # SQL to calculate distance between geocache and home point
    dist = 'greatcirclelength(geomfromtext("linestring(" || x(location) || " " || y(location) || ", %f %f)", 4326))' % (lat, lon)
    dist2 = 'geodesiclength(geomfromtext("linestring(" || x(location) || " " || y(location) || ", %f %f)", 4326))' % (lat, lon)

    # Query for caches within circle and order by distance
    rs = cur.execute('select code, description, x(location), y(location), %(dist)s, %(dist2)s from gc where MbrWithin(location, %(searchCircle)s) order by %(dist)s' % {'dist':dist, 'searchCircle':circle, 'dist2':dist2})

    data = []
    for row in rs:
      coord = (row[2], row[3])
      data.append({
        'code': row[0],
        'description': row[1],
        'distance': int(row[4]),
        'human_bearing': humanizeBearing(bearing(coord, (lat, lon))), 
        'bearing': bearing(coord, (lat, lon)),
        'lat': row[2],
        'lon': row[3]
        })

    if len(data) > 0:
      return data[0]
    return None

def main(db):
 
  gps_session = gps.gps(mode=gps.WATCH_ENABLE)

  lcd = Server()
  lcd.start_session()

  s = lcd.add_screen("cache")
  s.set_heartbeat("off")
  s.set_duration(10)
  s.set_priority("hidden")

  sl = lcd.add_screen("latlon")
  sl.set_duration(2)
  lat_widget = sl.add_string_widget("lat","", y=1)
  lon_widget = sl.add_string_widget("lon","", y=2)

  #title = s.add_title_widget("title","")
  title = s.add_scroller_widget("title",1,1,16,1,"h",1,"" )
  code = s.add_string_widget("code", "", y=2)
  dist = s.add_string_widget("dist", "", y=2, x=9)
  bearing = s.add_string_widget("bearing", "", y=2, x=14)

  lat, lon = (0,0)

  while 1:
    gpsinfo = gps_session.next()
    if 'lat' in gpsinfo.keys() and 'lon' in gpsinfo.keys():
      lat = gpsinfo.lat
      lon = gpsinfo.lon
      lat_widget.set_text("lat: %0.6f" % lat)
      lon_widget.set_text("lon: %0.6f" % lon)
      print lat,lon
    closest = db.findNearest(lat, lon)
    if closest:
      print closest
      s.set_priority("info")
      title.set_text(closest['description'].encode('ascii'))
      code.set_text(closest['code'].encode('ascii'))
      if closest['distance'] > 1000:
        dist.set_text('%0.0fkm' % closest['distance']/1000.0)
      else:
        dist.set_text('%0.0fm' % closest['distance'])
      if closest['distance'] < 200:
        s.set_backlight("flash")
      bearing.set_text(closest['human_bearing'])
    else:
      s.set_priority("hidden")

if __name__=='__main__':
  db = CacheDatabase('db.sqlite')
  main(db)

    