# -*- coding: utf-8 -*-
# this api is copyed from https://github.com/Sasivarnasarma/telegraph
# if you need update this lib, go to https://github.com/Sasivarnasarma/
"""
Python Telegraph API wrapper

@author: python273
@contact: https://python273.pw
@license MIT License, see LICENSE file

Copyright (C) 2024
"""

__title__ = 'telegraph'
__author__ = 'python273'
__version__ = '3.0.0'
__all__ = (
    '__version__',
    'Telegraph',
    'UploadFile',
    'AsyncTelegraph',
    'AsyncUploadFile',
    'TelegraphException',
    'ResponseNotOk',
    'RetryAfterError',
    'ParsingException',
    'NotAllowedTag',
    'InvalidHTML'
)

from ._api import Telegraph, UploadFile
from ._api_async import AsyncTelegraph, AsyncUploadFile
from .exceptions import TelegraphException, ResponseNotOk, RetryAfterError, ParsingException, NotAllowedTag, InvalidHTML
