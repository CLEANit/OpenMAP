#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : Jan 20 6:04 p.m. 2021
@Author  : Conrard TETSASSI
@Email   : giresse.feugmo@gmail.com
@File    : imap.py
@Project : OpenMAP
@Software: PyCharm

Adapted from https://www.thepythoncode.com/article/reading-emails-in-python
"""
import email
import imaplib
import os
import webbrowser
from email.header import decode_header

# account credentials
username = 'giresse.feugmo@gmail.com'
password = 'soraya09'


def clean(text):
    # clean text for creating a folder
    return ''.join(c if c.isalnum() else '_' for c in text)


# create an IMAP4 class with SSL
imap = imaplib.IMAP4_SSL('imap.gmail.com')
# authenticate
imap.login(username, password)

status, messages = imap.select('INBOX')
# number of top emails to fetch
N = 3
# total number of emails
messages = int(messages[0])
