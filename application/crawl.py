#! /usr/bin/python3
# -*- coding: UTF-8 -*-#

from flask import Flask, jsonify, request
from .crawlers.crawlers import ZillowCrawler,RedfinCrawler
import json
from config import app

@app.route('/post-url',methods=['POST'])
def posturl():
  """
  Service entrance 
  Args:
    {'url' : 'http://example.com'}

  Returns:
    {'errmsg':'missing url in parameters'}
    {'errmsg':'invalid url'}
    {'errmsg':'no match found for input url'}

    { 'msg': 'success' 'data' : dict}
  """
  params = request.get_json()
  if not params or not 'url' in params:
    return jsonify({'errmsg':'missing url in parameters'}), 400

  url = params['url']
  if 'redfin.com' in url:
    crawler = RedfinCrawler(check_string='home')
  elif 'zillow.com' in url:
    crawler = ZillowCrawler(check_string='zpid')
  else:
    return jsonify({'errmsg':'invalid url'}),400

  response = crawler.get_html(url)
  if response.get('status') == 400:
    return jsonify({'errmsg':'no match found for input url'}),400

  item = crawler.parse(response)
  return jsonify({'msg':'success','data':item['data']}), 200


@app.route('/post-addr',methods=['POST'])
def post_addr():
  """
  Service entrance 
  Args:
    {'addr' : '380 5th Ave, New York, NY 10018, USA' 'source':'zillow'} -source is optional default is zillow
    {'addr' : '380 5th Ave, New York, NY 10018, USA' 'source':'redfin'}

  Returns:
    {'errmsg':'missing addr in parameters'}
    {'errmsg':'no match found for input address'}
    { 'msg': 'success','data' : data}
  """
  params = request.get_json()
  if not params or not 'addr' in params:
    return jsonify({'errmsg':'missing addr in parameters'}), 400

  formatted_address = params['addr']

  if not params.get('source'):
    params['source'] = 'zillow'

  # search zillow
  if params['source']=='zillow':
    crawler = ZillowCrawler(check_string='zpid')
  elif params['source']=='redfin':
    crawler = RedfinCrawler(check_string='home')

  search_url = crawler.addr_to_search_url(formatted_address)
  room_url = crawler.parse_searching_page(search_url)
  if room_url:
    response = crawler.get_html(room_url)
    if response.get('html'):
      item = crawler.parse(response)
      return jsonify({'msg':'success','data':item['data']}), 200
  return jsonify({'errmsg':'no match found for input address'}),400
