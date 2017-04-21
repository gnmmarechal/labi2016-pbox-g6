#!/usr/bin/env python
# encoding=utf-8
import pytest
import client
import json


def test_get_box_list():
    assert isinstance(client.get_box_list(client.tgt_server), dict)


def test_get_box_index():
    try:
        data = json.dumps(client.get_box_list(client.tgt_server))
        assert True
    except ValueError:
        assert False


def test_get_box_number():
    assert isinstance(client.get_box_number(client.get_box_list(client.tgt_server)), int)

