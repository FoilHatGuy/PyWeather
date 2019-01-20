import http.client as hclient

con = hclient.HTTPConnection("pogoda-service.ru", port=80)
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
con.request("POST", "/archive_gsod_res.php", "country=RU&station=276120&datepicker_beg=01.01.2000&datepicker_end=31.12.2009", headers)
response = con.getresponse()
print(response.read().decode("UTF-8"))
