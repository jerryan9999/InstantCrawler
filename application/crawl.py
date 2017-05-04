#! /usr/bin/python3
# -*- coding: UTF-8 -*-#

from flask import Flask, jsonify, request
from .crawlers import zillow, redfin
import json
from config import app

@app.route('/posturl',methods=['POST'])
def posturl():
  """
  Service entrance 
  args:
    {'url' : 'http://example.com'}
    url : must
  returns:
    The parameter must contain url field. else return {'errmsg':'missing url in parameters'}
    if status == 400
      return {'errmsg':'request failed'}
    else:
      return { 'msg': 'success' 'data' : item}
  """
  params = request.get_json(force=True,silent=True)
  if not params or not 'url' in params:
    return jsonify({'errmsg':'missing url in parameters'}), 400

  url = params['url']
  if 'www.redfin.com' in url:
    item = redfin.parse(url)
  else:
    item = zillow.parse(url)

  if item.get('status') == 400:
    return jsonify({'errmsg':'request failed'}),400

  return jsonify({'msg':'success','data':item.get('data')}), 201


