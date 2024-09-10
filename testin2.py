from js import XMLHttpRequest, Blob
import json

data = {"a": 1}

req = XMLHttpRequest.new()
req.open("POST", "https://httpbin.org/anything", False)
blob = Blob.new([json.dumps(data)], {type : 'application/json'})
req.send(blob)
str(req.response)