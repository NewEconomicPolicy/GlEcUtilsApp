#!/usr/bin/env python

#=======================================================================================
# Patrick Brockmann - 2019/05/07 for the VERIFY project

from xml.dom import minidom
import urlopen

import sys
import ssl

#=======================================================================================
# USAGE:
#        ./wget_THREDDS.py URL
#
# EXAMPLE:
#        ./wget_THREDDS.py https://verifydb.lsce.ipsl.fr/thredds/catalog/verify/WP3/CRUHAR_V1/MONTHLY/

#=======================================================================================
request_url = sys.argv[1]

#---------------------------------------------------   
# Create context for certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

#---------------------------------------------------   
def get_elements(url, tag_name, attribute_name):
  """Get elements from an XML file"""
  usock = urlopen(url, context=ctx)
  xmldoc = minidom.parse(usock)
  usock.close()
  tags = xmldoc.getElementsByTagName(tag_name)
  attributes=[]
  for tag in tags:
    attribute = tag.getAttribute(attribute_name)
    attributes.append(attribute)
  return attributes
 
#---------------------------------------------------   
def main():
  url = request_url + 'catalog.xml'
  catalog = get_elements(url,'dataset','urlPath')
  files=[]
  for citem in catalog:
    if (citem[-3:]=='.nc'):
      files.append(citem)

  count = 0
  for fle in files:
    count +=1
    file_name = fle.split('/')[-1]
    file_url = request_url.replace('catalog/', 'fileServer/') + file_name
    print ('wget --no-check-certificat ' +  file_url)
 
#---------------------------------------------------   
if __name__ == '__main__':
  main()
