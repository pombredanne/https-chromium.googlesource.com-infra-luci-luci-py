# Copyright 2014 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Authentication and authorization component.

Exports public API of 'auth' component. Each module in 'auth' package can
export a portion of public API by specifying exported symbols in its __all__.
"""

from .version import __version__

try:
  import endpoints
except ImportError:
  endpoints = None

# Auth component is using google.protobuf package, it requires some python
# package magic hacking.
from components import utils
utils.fix_protobuf_package()

from . import api
from . import delegation
from . import exceptions
from . import gce_vm_auth
from . import handler
from . import ipaddr
from . import machine_auth
from . import model
from . import prpc
from . import service_account
from . import signature
from . import tokens
from . import ui.app

# Endpoints support is optional, enabled only when endpoints library is
# specified in app.yaml.
if endpoints:
  from endpoints_support import *
  from ui.endpoints_api import AuthService

# Import 'config' to register lib_config hook.
import config
