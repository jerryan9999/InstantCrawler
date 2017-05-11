### InstantCrawler
#### Starting:
gunicorn wsgi:app


#### interface1: http://xxx.xx.xx.xx:8000/post-addr
```
{
  'addr':'2913 Pescadero Terrace, Fremont, CA 94538, USA'
}
```
```
{
  'addr':'2913 Pescadero Terrace, Fremont, CA 94538, USA'
  'source':'redfin'
}
```
exception:
```
    {'errmsg':'missing addr in parameters'}

    {'errmsg':'no match found for input address'}
```


#### additional interface2: http://xxx.xx.xx.xx:8000/post-url
```
{
  'url':'https://www.zillow.com/homedetails/2913-Pescadero-Ter-Fremont-CA-94538/116150263_zpid/'
}
```
```
{
  'url':'https://www.redfin.com/CA/Fremont/2913-Pescadero-Ter-94539/home/40627585/'
}
```
exception:
```
    {'errmsg':'missing url in parameters'}
    
    {'errmsg':'no match found for input url'}
```
