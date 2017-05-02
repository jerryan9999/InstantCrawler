# usr/bin/python3
# -*- coding: utf-8 -*-

import requests
from parsel import Selector
import re

def get_html(url):
  response = requests.get(url).text
  return response

def parse(response):
  ''' parse html and get dict-like item
  '''
  item = {}
  sel = Selector(text=response)
  item['beds'] = sel.xpath("//header[contains(@class,'zsg-content-header')]/h3/span[@class='addr_bbs'][1]/text()").extract_first()
  item['baths'] = sel.xpath("//header[contains(@class,'zsg-content-header')]/h3/span[@class='addr_bbs'][2]/text()").extract_first()
  item['size'] = sel.xpath("//header[contains(@class,'zsg-content-header')]/h3/span[@class='addr_bbs'][3]/text()").extract_first()

  fact_and_features_sel = sel.xpath('//div[contains(@class,"hdp-facts-expandable-container")]')
  item['type'] =fact_and_features_sel.xpath('div[1]/div[1]/div/div[2]/div/text()').extract_first()
  item['laundry'] = fact_and_features_sel.xpath('div[1]/div[2]/div/div[2]/div/text()').extract_first()

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
  item['dryer'] = True if "DRYER" in features else False
  item['refrigerator'] = True if "REFRIGERATOR" in features or "FREEZER" in features else False
  item['dishwasher'] = True if "DISHWASHER" in features else False
  item['cooling'] = True if "AIR CONDITIONING" in features or "CENTRAL A/C" in features else False

  # pet
  item['cat'] = True if "CAT" in features else False
  item['small_dogs'] = True if "SMALL DOGS" in features else False
  item['large_dogs'] = True if "LARGE DOGS" in features else False

  #process item
  item = process_item(item)
  return item

def process_item(item):
  ''' extract only useful string 
  '''
  for key, value in item.items():
    if isinstance(value,bool):
      continue
    if key == 'beds' and 'bed' in value:
      item['beds'] = re.match(r'[0-9]+',value).group()
    elif key == 'baths' and 'bath' in value:
      item['baths'] = re.match(r'[0-9.]+',value).group()
    elif key == 'size' and 'sqft' in value:
      item['size'] = re.match(r'[0-9.]+',value).group()
    elif 'No Data' in value:
      item[key] = False

  return item


if __name__ == '__main__':
  url = "https://www.zillow.com/homedetails/32-W-40th-St-APT-2N-New-York-NY-10018/2111535338_zpid/"
  response = get_html(url)
  item = parse(response)
  print(item)
