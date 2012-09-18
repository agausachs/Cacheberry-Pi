Cacheberry-Pi
=============

Cacheberry Pi is a geocaching assistant built upon the Raspberry Pi platform.

It's intended to be a permanent fixture in the car and alert you of nearby caches (when stopped) or along your route (when driving).  The intent is not to replace your handheld GPSr but to complement it. 

See an overview [Video on YouTube](http://youtu.be/bwD6K2EeeV8) or view the [project homepage](http://jclement.ca/cacheberry-pi/).
# Features #
* Smart Search: depending on speed and direction of travel
* Ability to maintain a database of 20k+ geocaches
* Easy syncing of cache lists with GSAK via thumb drive
* Automatic tracklog recording and syncing with thumb drive

# Hardware #
* [RaspberryPi B](http://canada.newark.com/raspberry-pi/raspbrry-pcba/raspberry-pi-model-b-board-only/dp/83T1943)
* [Arduino IIC / I2C Serial 2.6" LCD 1602 Module Display](http://dx.com/p/arduino-iic-i2c-twi-spi-serial-lcd-1602-module-electronic-building-block-136922?item=4)
* [Holux M-215 GPRr](http://dx.com/p/genuine-holux-usb-gps-receiver-black-106778?item=8) - Likely almost any other NMEA GPS will suffice
* 8GB SD Card
* 12V USB Charger + MicroUSB cable

# Software Requirements #
* Python 2.7
* [GPsd](http://www.catb.org/gpsd/) - Available through APT
* [PySpatialite](http://code.google.com/p/pyspatialite/) - Available through APT
* [LCDProc] (http://www.lcdproc.org/) - Available through APT (required custom display driver)                                                      
* [RPi.GPIO] (http://pypi.python.org/pypi/RPi.GPIO) 
* [AutoFS] (http://www.autofs.org/) - Available through APT
                                     
# Setup Instructions #

These are, obviously, a work in progress :)

## Package Installation ##

Most of the packages can be obtained from APT.

~~~
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get install autofs lcdproc python-pyspatialite sqlite3 gpsd vim-nox gpsd-clients screen
~~~

The RPi.GPIO library needs to be installed separately since it's not in APT.

~~~
$ cd /usr/src
$ sudo wget http://pypi.python.org/packages/source/R/RPi.GPIO/RPi.GPIO-0.3.1a.tar.gz#md5=1588ebc23872ce281b846a9f01d389af
$ sudo tar -xvf RPi.GPIO-0.3.1a.tar.gz
$ cd RPi.GPIO-0.3.1a/
$ sudo python setup.py install
~~~

The lcdproc python library also needs to be installed separately.

~~~
$ cd /usr/src
$ sudo wget http://pypi.python.org/packages/source/l/lcdproc/lcdproc-0.03.tar.gz#md5=177328fd30c973151b5e75f9c1b992c7
$ sudo tar -xzf lcdproc-0.03.tar.gz
$ cd lcdproc-0.03/
$ sudo python setup.py install

## Download CacheberryPi Software ##

Clone the CacheberryPi repository to your "pi" user's home folder.

~~~
$ cd ~
$ git clone https://github.com/jclement/Cacheberry-Pi.git
~~~

## Configuration ##

Install the ifup script so we can see network configuration on the LCD.

~~~
$ cd ~/Cacheberry-Pi/utils
$ sudo cp ifup-lcdproc.py /etc/network/if-up.d
$ sudo chmod 755 /etc/network/if-up.d/ifup-lcdproc.py
~~~

Install lcdproc configuration files and LCD driver.

~~~
$ cd ~/Cacheberry-Pi/misc
$ sudo cp LCDd.conf /etc
$ sudo cp hd44780-i2c/hd44780.so /usr/lib/lcdproc/
~~~

Setup udev to make GPS devices world write/readable:

~~~
$ cd ~/Cacheberry-Pi/misc
$ sudo cp 70-persistent-net.rules  /etc/udev/rules.d/
~~~

Edit /etc/rc.local to start CacheberryPi on startup.  Add the following before "exit 0"

~~~
nohup /home/pi/Cacheberry-Pi/start &
~~~

Configure autofs for update functionality.

~~~
$ cd ~/Cacheberry-Pi/misc
$ cp auto.removable /etc
$ cp auto.master /etc
~~~

Edit /etc/hosts and /etc/hostname and replace "raspberrypi" with "cacheberrypi".


