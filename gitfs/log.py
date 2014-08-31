import logging

logging.basicConfig(level=logging.DEBUG,
                    filename='/tmp/gitfs.log',
                    format='%(asctime)s %(message)s',
                    datefmt='%B-%d-%Y %H:%M:%S')
log = logging.getLogger('gitfs')
