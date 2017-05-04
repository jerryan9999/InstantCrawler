# usr/bin/python3
# -*- coding: utf-8 -*-

import requests
from parsel import Selector
import re

def get_html(url):
  try:    
    response = requests.get(url, timeout=10)
  except:
    return {'status':400, 'data':None}
  if response.status_code != 200:
    return {'status':400, 'data':None}
  response = response.text
  return {'status':200, 'data':response}


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

  fact_and_features_sel = sel.xpath('//div[contains(@class,"hdp-facts-expandable-container")]')
  item['type'] =fact_and_features_sel.xpath('div[1]/div[1]/div/div[2]/div/text()').extract_first()
  item['washer'] = fact_and_features_sel.xpath('div[1]/div[2]/div/div[2]/div/text()').extract_first()

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
  value = re.match(r'[0-9]+',value).group()
  return value

if __name__ == '__main__':
  url = "https://www.zillow.com/homedetails/32-W-40th-St-APT-2N-New-York-NY-10018/2111535338_zpid/"
#  url = 'https://www.redfin.com/WA/Seattle/2591-Perkins-Ln-W-98199/home/126436'
  item = parse(url)
