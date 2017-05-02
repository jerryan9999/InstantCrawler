#! /usr/bin/python3
# -*- coding: UTF-8 -*-

from flask import Flask, jsonify, request
from crawlers import zillow
import json


from config import app


@app.route('/zillow/<url>')
def zillow(url):
  resp = zillow.get_html(url)
  item = zillow.parse(resp)
  return jsonify({'msg':'success','data':item}), 201
