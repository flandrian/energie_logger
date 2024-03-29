#!/usr/bin/python

from serial import Serial
from time import sleep
import json
import rrdtool
from ConfigParser import ConfigParser
import os
import argparse
import logging.handlers
from gateway.RrdTools import RrdTools

class EnergieLoggerGateway(object):
    def __init__(self):
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.INFO)
        self._logger.addHandler(logging.handlers.SysLogHandler(address='/dev/log'))

        parser = argparse.ArgumentParser(description='tinkwise gateway')
        parser.add_argument('-c','--config_file', type=str, dest='config_file', default='/etc/tinkwise.conf')
        args = parser.parse_args()
        
        config = ConfigParser()
        config.read(args.config_file)
        connection_file = config.get('connection', 'file')
        self._rrd_dir = config.get('rrd', 'path')
        
        try:
            self._serial_port = Serial(port=connection_file, baudrate=115200)
        except Exception as e:
            self._logger.critical('failed to open serial port ' + connection_file + ':' + e.message)
            raise
            
    def run(self):
        self._serial_port.write('?')
        sleep(2)
        self._serial_port.read(1000)
            
        data_sources_spaces = map(lambda o: o.encode('ascii', 'ignore'), sample.keys())
        data_sources = map(lambda s: s.replace(' ', '_'), data_sources_spaces)
        data_values = map(str, sample.values())
        rrd_path = self._rrd_dir + '/{}.rrd'.format(node_index)
        
        if not os.path.isfile(rrd_path):
            self._create_database(rrd_path, data_sources)
        
        try:
            RrdTools.update(node_index, data_sources, data_values)
            data_sources_colons = ':'.join(data_sources)
            rrdtool.update(rrd_path, '--template', data_sources_colons, 'N:' + ':'.join(data_values))
        except Exception as e:
            if e.message.find('unknown DS name') >= 0:
                self._logger.warning('data source reveived is missing in config file')
            else:
                raise
                    
    def _create_database(self, path, data_sources):
        self._logger.info('creating database {} with sources {}'.format(path, ','.join(data_sources)))
        data_source_specs = map(lambda s: 'DS:'+s+':GAUGE:600:U:U', data_sources)
        try:
            rrdtool.create(path, '--step', '600', data_source_specs, 'RRA:LAST:0.5:1:80000')
        except Exception as e:
            self._logger.error(e.message)
            raise

if __name__ == "__main__":
    gateway = EnergieLoggerGateway()
    gateway.run()
