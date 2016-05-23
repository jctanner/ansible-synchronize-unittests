#!/bin/bash

#python test_synchronize.py
# ./runtest.sh test_synchronize:TestSynchronizeAction.test_basic_become

nosetests -v --with-isolation --nocapture $@ #test_synchronize.py
