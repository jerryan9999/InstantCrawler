# usr/bin/python3
# -*- coding: utf-8 -*-

import requests
from parsel import Selector
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
import re

headers = {
  'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
  'Accept-Encoding':'gzip',
  'Accept-Language':'zh-CN,zh;q=0.8',
  'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36'
}

API = 'https://www.zillow.com/webservice/GetDeepSearchResults.htm'

def get_html(url):
  try:    
    response = requests.get(url,headers=headers, timeout=10)
  except:
    return {'status':400, 'data':None}
  if response.status_code != 200:
    return {'status':400, 'data':None}
  else:
    if "zpid" in response.url:
      response = response.text
      return {'status':200, 'data':response}
    else:
      return {'status':400, 'data':None}


def parse(url):
  ''' parse html and get dict-like item
  '''
  response = get_html(url)
  if response.get('status') == 400:
    return response

  item = {}
  sel = Selector(text=response.get('data'))
  item['beds'] = process_value(sel.xpath("//header[contains(@class,'zsg-content-header')]/h3/span[@class='addr_bbs'][1]/text()").extract_first())
  item['baths'] = process_value(sel.xpath("//header[contains(@class,'zsg-content-header')]/h3/span[@class='addr_bbs'][2]/text()").extract_first())
  item['size'] = process_value(sel.xpath("//header[contains(@class,'zsg-content-header')]/h3/span[@class='addr_bbs'][3]/text()").extract_first())

  # location
  ts = re.search(r'Latitude:([0-9\.-]+),Longitude:([0-9\.-]+)',response.get('data'),re.IGNORECASE)
  if ts:
    item['latitude'] = ts.group(1)
    item['longitude'] = ts.group(2)
  fact_and_features_sel = sel.xpath('//div[contains(@class,"hdp-facts-expandable-container")]')
  item['type'] =fact_and_features_sel.xpath('div[1]/div[1]/div/div[2]/div/text()').extract_first()

  # features set preparation
  features = fact_and_features_sel.xpath('//span[@class="hdp-fact-value"]/text()').extract()
  features_set = set(re.split(',|, | - ',','.join(features)))     # convert one sting 'Cats, large dogs, small dogs' to three sub string in a set
  features_set_without_space = {f.strip().upper() for f in features_set}
  item = process_features(features_set_without_space,item)
  return item


def process_features(features,item):
  ''' mapping key and value from features
  '''
  # facilities
  item['pool'] = True if "POOL" in features else False
  item['garden'] = True if "GARDEN" in features else False
  item['garage'] = True if "GARAGE" in features or "CARPORT" in features else False
  item['basement'] = True if "BASEMENT" in features or "PARTIAL BASEMENT" in features else False
  item['patio'] = True if "PATIO" in features else False
  item['fitness_center'] = True if "FITNESS CENTER" in features else False

  # appliances
  item['washer'] = True if 'WASHER' in features else False
  item['dryer'] = True if "DRYER" in features else False
  item['refrigerator'] = True if "REFRIGERATOR" in features or "FREEZER" in features else False
  item['dishwasher'] = True if "DISHWASHER" in features else False
  item['cooling'] = True if "AIR CONDITIONING" in features or "CENTRAL A/C" in features else False
  item['trash_compactor'] = True if "GARBAGE DISPOSAL" in features or "TRASH COMPACTOR" in features else False

  # pet
  item['cat'] = True if "CAT" in features else False
  item['small_dogs'] = True if "SMALL DOGS" in features else False
  item['large_dogs'] = True if "LARGE DOGS" in features else False

  return {"status":200, "data": item}

def process_value(value):
  ''' extract only useful string 
  '''
  if value == None:
    return None
  value = re.match(r'[0-9,\.]+',value)
  if value:
    value = value.group()
  return value

def addr_to_search_url(address):
  ''' String address input: 100 W 39th St, New York, NY 10018, USA'''
  addresslist = address.split(',')
  address,citystatezip = addresslist[0],addresslist[1].lstrip()+','+addresslist[2].strip()
  #print("address:{},citystatezip:{}".format(address,citystatezip))
  params_dict={'zws-id':'X1-ZWz197judx38y3_6r0dc',
              'address':address,
              'citystatezip':citystatezip}
  search_url = API + "?" + urlencode(params_dict)
  #print(search_url)
  return search_url

def parse_searching_page(url):
  ''' input: https://www.zillow.com/webservice/GetDeepSearchResults.htm?zws-id=X1-ZWz197judx38y3_6r0dc
  &address=100+W+39th+St&citystatezip=New+York%2CNY+10018'''
  r = requests.get(url)
  tree = ET.fromstring(r.text)
  code = tree[1][1].text
  if int(code)==0:
    url = tree[2][0][0][1][0].text
    return url

if __name__ == '__main__':
  #url = "https://www.zillow.com/homedetails/32-W-40th-St-APT-2N-New-York-NY-10018/2111535338_zpid/"
  #formatted_address = '100 W 39th St, New York, NY 10018, USA'
  #formatted_address = '28 W 40th St, New York, NY 10018, USA'
  formatted_address = '380 5th Ave, New York, NY 10018, USA'
  search_url = addr_to_search_url(formatted_address)
  url = parse_searching_page(search_url)
  if url:
    print(url)
    item = parse(url)
    print('item:{},url:{}'.format(item,url))
