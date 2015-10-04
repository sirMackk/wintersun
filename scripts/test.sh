#!/bin/bash
coverage run --source=wintersun --omit=wintersun/test*  wintersun/test_all.py && coverage report -m
