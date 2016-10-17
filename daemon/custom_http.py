import http.cookiejar, urllib.request, urllib.parse

class NoRedirection(urllib.request.HTTPErrorProcessor):

    def http_response(self, request, response):
        return response

    https_response = http_response


jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(NoRedirection, urllib.request.HTTPCookieProcessor(jar))

def http(url, data = None):
    #print('Http request:', url)
    if data:
        data = '&'.join( key+'='+urllib.parse.quote(str(value)) for key, value in data )
        data = str.encode(data)
    
    req = urllib.request.Request(url, data)
    res = opener.open(req)
    return res.read().decode('utf-8')