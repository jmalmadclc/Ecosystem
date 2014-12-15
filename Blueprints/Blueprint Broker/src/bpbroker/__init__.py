# -*- coding: utf-8 -*-
"""
CenturyLink Cloud Blueprint Broker Toolset.

This broker foundation works to support advanced Blueprint deployment requiring
shared state and multi-server/multi-role communication across multiple server deployments.

CenturyLink Cloud: http://www.CenturyLinkCloud.com
Package Github page: 

"""

import bpbroker.api as API
import bpbroker.discovery as discovery
import bpbroker.ping as ping
import bpbroker.services as services
import bpbroker.config as config_class


####### module/object vars #######
#_V1_API_KEY = False

config = config_class.Config()
