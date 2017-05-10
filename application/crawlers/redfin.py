# usr/bin/python3
# -*- coding: utf-8 -*-

import requests
from parsel import Selector
import re

headers = {
  'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
  'Accept-Encoding':'gzip',
  'Accept-Language':'zh-CN,zh;q=0.8',
  'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36'
}

def get_html(url):
  try:    
    response = requests.get(url, headers=headers, timeout=10)
  except:
    return {'status':400, 'data':None}
  if response.status_code != 200:
    return {'status':400, 'data':None}
  response = response.text
  return {'status':200, 'data':response}

def parse(url):
  ''' 
  parse html and get dict-like item
  '''
  response = get_html(url)
  if response.get('status') == 400:
    return response
  item = {}
  sel = Selector(text=response.get('data'))
  item['beds'] = sel.xpath('//div[contains(@class,"HomeMainStats home-info")]/div[3]/div/text()').extract_first()
  item['baths'] = sel.xpath('//div[contains(@class,"HomeMainStats home-info")]/div[4]/div/text()').extract_first()
  item['type'] = sel.xpath('//div[contains(@class, "keyDetailsList")]/div/span[2]/text()').extract_first()
  item['size'] = sel.xpath('//span[contains(@class,"main-font statsValue")]/text()').extract_first()
  
  fact_and_features_sel1 = sel.xpath('//div[contains(@class, "amenity-group")]/ul//li/text()').extract()
  fact1 = set(re.split('# |:|,| ', ','.join(fact_and_features_sel1)))
  fact_and_features_sel2 = sel.xpath('//div[contains(@class, "amenity-group")]/ul//span/text()').extract()

  fact2 = set(re.split(', |,|/| ', ','.join(fact_and_features_sel2)))
  features = fact1 | fact2
  features = {f.upper() for f in features}
  item = process_features(features, item)
  return {'status':200, 'data':item}

def process_features(features,item):
  # Interior Features
  item['washer'] = True if 'WASHER' in features else False
  item['dryer'] = True if 'DRYER' in features else False
  item['refrigerator'] = True if 'REFRIGERATOR' in features else False
  item['dishwasher'] = True if 'DISHWASHER' in features else False
  item['trash_compactor'] = True if 'GARBAGE' in features or 'TRASH' and 'COMPACTOR' in features else False
  item['cooling'] = True if 'AIR' and 'CONDITIONING' in features else False

  # Equipment
  item['pool'] = True if 'POOL' in features else False
  item['garden'] = True if 'GARDEN' in features else False
  item['garage'] = True if 'GARAGE' in features or 'CARPORT' in features else False
  item['basement'] = True if 'BASEMENT' in features else False
  item['patio'] = True if 'PATIO' in features else False
  item['fitness_center'] = True if 'FITNESS' in features or 'EXERCISE' in features else False

  # pet
  item['cat'] = True if 'CATS' in features or 'CAT' in features else False
  item['small_dogs'] = True if 'DOGS' in features or 'DOG' in features else False
  item['large_dogs'] = False

  return item

if __name__ == '__main__':
  url = 'https://www.redfin.com/WA/Seattle/4721-47th-Ave-SW-98116/home/152688'
  item = parse(url)
