# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import base64
import hashlib
import logging

from google.appengine.api import app_identity
from google.appengine.api import memcache
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

import httplib2
import webapp2

http = httplib2.Http(memcache)

service = discovery.build(
    "remotebuildexecution",
    "v2",
    http=http,
    credentials=GoogleCredentials.get_application_default())


def get_digest(data):
  return {"sizeBytes": str(len(data)), "hash": hashlib.sha256(data).hexdigest()}


def get_request(data):
  return {
      "data": base64.b64encode(data),
      "digest": get_digest(data),
  }


class MainHandler(webapp2.RequestHandler):

  def get(self):
    project = app_identity.get_application_id()
    instance = "projects/%s/instances/default_instance" % project

    update_resp = service.blobs().batchUpdate(
        instanceName=instance,
        body={
            "requests": [
                get_request(""),
                get_request("a"),
            ]
        }).execute()
    logging.info("%s", update_resp)

    read_resp = service.blobs().batchRead(
        instanceName=instance,
        body={
            "digests": [
                get_digest(""),
                get_digest("a"),
            ]
        }).execute()
    logging.info("%s", read_resp)

    self.response.write("%s %s" % (update_resp, read_resp))


app = webapp2.WSGIApplication([
    ('/', MainHandler),
], debug=True)
