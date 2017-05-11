# usr/bin/python3
# -*- coding: utf-8 -*-

import requests
from parsel import Selector
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
import re

class Webcrawler(object):

  headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36'
            }
  def __init__(self,check_string):
    self.check_string = check_string

  def get_html(self,url,timeout=10):
    try:
      response = requests.get(url,headers=self.headers, timeout=timeout)
    except:
      return {'status':400, 'html':None}
    if response.status_code != 200:
      return {'status':400, 'html':None}
    else:
      if self.check_string in response.url:
        response = response.text
        return {'status':200, 'html':response}
      else:
        return {'status':400, 'html':None}

  def parse(self,response):
    pass

  def addr_to_search_url(address):
    pass

  def parse_searching_page(url):
    pass


class RedfinCrawler(Webcrawler):

  homepage = "https://www.redfin.com"
  API = 'https://www.redfin.com/stingray/do/location-autocomplete'

  def parse(self,response):
    item = {}
    sel = Selector(text=response.get('html'))
    item['beds'] = sel.xpath('//div[contains(@class,"HomeMainStats home-info")]/div[3]/div/text()').extract_first()
    item['baths'] = sel.xpath('//div[contains(@class,"HomeMainStats home-info")]/div[4]/div/text()').extract_first()
    item['size'] = sel.xpath('//span[contains(@class,"main-font statsValue")]/text()').extract_first()
    types = sel.xpath('//div[contains(@class, "keyDetailsList")]/div/span[1]/text()').extract()
    for i,name in enumerate(types):
      if "Property Type" in name:
        index = i
    item['type'] = sel.xpath('//div[contains(@class, "keyDetailsList")]/div/span[2]/text()').extract()[index]
    fact_and_features_sel1 = sel.xpath('//div[contains(@class, "amenity-group")]/ul//li/text()').extract()
    fact1 = set(re.split('# |:|,| ', ','.join(fact_and_features_sel1)))
    fact_and_features_sel2 = sel.xpath('//div[contains(@class, "amenity-group")]/ul//span/text()').extract()

    fact2 = set(re.split(', |,|/| ', ','.join(fact_and_features_sel2)))
    features = fact1 | fact2
    features = {f.upper() for f in features}
    item = self._process_features(features, item)
    return {'status':200, 'data':item}

  def _process_features(self,features,item):
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

  def addr_to_search_url(self,address):
    ''''input: 2913 Pescadero Terrace, Fremont, CA 94538, USA'''
    address = address.split(',')[0]
    params_dict = {'location':address,'start':0,'count':10,'v':2,'al':1,'iss':'false','ooa':'true'}
    search_url = self.API + "?" + urlencode(params_dict)
    return search_url

  def parse_searching_page(self,url):
    r = requests.get(url,headers=self.headers)
    urlstringre = re.search(r'url":"(.+?)"',r.text)
    if urlstringre:
      return self.homepage+urlstringre.group(1)


class ZillowCrawler(Webcrawler):

  API = 'https://www.zillow.com/webservice/GetDeepSearchResults.htm'
  key = 'X1-ZWz197judx38y3_6r0dc'


  def parse(self,response):
    item = {}
    sel = Selector(text=response.get('html'))
    item['beds'] = self._process_value(sel.xpath("//header[contains(@class,'zsg-content-header')]/h3/span[@class='addr_bbs'][1]/text()").extract_first())
    item['baths'] = self._process_value(sel.xpath("//header[contains(@class,'zsg-content-header')]/h3/span[@class='addr_bbs'][2]/text()").extract_first())
    item['size'] = self._process_value(sel.xpath("//header[contains(@class,'zsg-content-header')]/h3/span[@class='addr_bbs'][3]/text()").extract_first())

    # location
    ts = re.search(r'Latitude:([0-9\.-]+),Longitude:([0-9\.-]+)',response.get('html'),re.IGNORECASE)
    if ts:
      item['latitude'] = ts.group(1)
      item['longitude'] = ts.group(2)
    fact_and_features_sel = sel.xpath('//div[contains(@class,"hdp-facts-expandable-container")]')
    item['type'] =fact_and_features_sel.xpath('div[contains(@class,"zsg-g")]/div[1]/div/div[2]/div/text()').extract_first()

    # features set preparation
    features = fact_and_features_sel.xpath('//span[@class="hdp-fact-value"]/text()').extract()
    features_set = set(re.split(',|, | - ',','.join(features)))     # convert one sting 'Cats, large dogs, small dogs' to three sub string in a set
    features_set_without_space = {f.strip().upper() for f in features_set}
    item = self._process_features(features_set_without_space,item)
    return item

  def _process_features(self,features,item):
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

  def _process_value(self,value):
    if value == None:
      return None
    value = re.match(r'[0-9,\.]+',value)
    if value:
      value = value.group()
    return value

  def addr_to_search_url(self,address):
    ''' String address input: 100 W 39th St, New York, NY 10018, USA'''
    addresslist = address.split(',')
    address,citystatezip = addresslist[0],addresslist[1].lstrip()+','+addresslist[2].strip()
    params_dict={'zws-id':self.key,
                'address':address,
                'citystatezip':citystatezip}
    search_url = self.API + "?" + urlencode(params_dict)
    return search_url

  def parse_searching_page(self,url):
    ''' input: https://www.zillow.com/webservice/GetDeepSearchResults.htm?zws-id=X1-ZWz197judx38y3_6r0dc
    &address=100+W+39th+St&citystatezip=New+York%2CNY+10018'''
    r = requests.get(url)
    tree = ET.fromstring(r.text)
    code = tree[1][1].text
    if int(code)==0:
      url = tree[2][0][0][1][0].text
      return url
