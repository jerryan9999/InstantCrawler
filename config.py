from flask import Flask
import yaml


config_yml = {}
with open('config.yml') as f:
  config_yml = yaml.load(f)


class Config:
  """Base config"""
  APP_NAME = "INSTANT CRALWER"
  SECRET_KEY = config_yml['secret_key']


app = Flask(__name__)
app.config.from_object(Config)
