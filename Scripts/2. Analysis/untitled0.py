# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 11:40:45 2018

@author: oliver.cairns
"""
import os
import pandas as pd

CURRENT_DIR = os.getcwd()

FILE_PATH = CURRENT_DIR + "\\" + "Market Date for Exercise.csv"

LENDERS_DF = pd.read_csv(FILE_PATH)

