#! /usr/bin/python3
# -*- coding: UTF-8 -*-#

from flask import Flask, jsonify, request
from .crawlers import zillow, redfin
import json
from config import app

@app.route('/post-url',methods=['POST'])
def posturl():
  """
  Service entrance 
  Args:
    {'url' : 'http://example.com'}

  Returns:
    The parameter must contain url field. else return {'errmsg':'missing url in parameters'}
    if status == 400
      return {'errmsg':'request failed'}
    else:
      return { 'msg': 'success' 'data' : dict}
  """
  params = request.get_json(force=True,silent=True)
  if not params or not 'url' in params:
    return jsonify({'errmsg':'missing url in parameters'}), 400

  url = params['url']
  if 'www.redfin.com' in url:
    item = redfin.parse(url)
  elif 'zillow.com' in url:
    item = zillow.parse(url)
  else:
    return jsonify({'errmsg':'invalid url'}),400

  if item.get('status') == 400:
    return jsonify({'errmsg':'no match found for input url'}),400

  return jsonify({'msg':'success','data':item.get('data')}), 201


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
  params = request.get_json(force=True,silent=True)
  if not params or not 'addr' in params:
    return jsonify({'errmsg':'missing addr in parameters'}), 400

  formatted_address = params['addr']

  if not params.get('source'):
    params['source'] = 'zillow'

  # search zillow
  if params['source']=='zillow':
    search_url = zillow.addr_to_search_url(formatted_address)
    url = zillow.parse_searching_page(search_url)
    if url:
      item = zillow.parse(url)
      return jsonify({'msg':'success','data':item.get('data')}), 201
    else:
      return jsonify({'errmsg':'no match found for input address'}),400

  # search redfin
  if params['source']=='redfin':
    search_url = redfin.addr_to_search_url(formatted_address)
    #print(search_url)
    url = redfin.parse_searching_page(search_url)
    if url:
      item = redfin.parse(url)
      return jsonify({'msg':'success','data':item.get('data')}), 201
    else:
      return jsonify({'errmsg':'no match found for input address'}),400
