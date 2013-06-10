# This file contains python variables that configure Salmon for email processing.
import logging
import sys
import os

DEBUG = False

sys.path.append('..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

accepted_queue_dir = 'run/accepted'
accepted_queue_opts_in = {}
accepted_queue_opts_out = {}

reject_dir = "run/rejected"

receiver_config = {'host': 'localhost', 'port': 8823}

out_handlers = ['app.handlers.out']
in_handlers = ['app.handlers.in']

router_defaults = {}

template_config = {'dir': 'app', 'module': 'templates'}

datetime_format = "%Y-%m-%d %H:%M:%S %z"
recieved_header_name = 'x-salmon-recieved'

# the config/boot.py will turn these values into variables set in settings
