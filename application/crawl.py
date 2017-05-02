#! /usr/bin/python3
# -*- coding: UTF-8 -*-#

from flask import Flask, jsonify, request
from .crawlers.zillow import get_html,parse
import json

from config import app

@app.route('/zillow/',methods=['POST'])
def zillow():
  params = request.get_json(force=True,silent=True)
  if not params or not 'url' in params:
    return jsonify({'errmsg':'missing url in parameters'}), 400
  url = params['url']
  resp = get_html(url)
  item = parse(resp)
  return jsonify({'msg':'success','data':item}), 201
