# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 23:23:24 2019

@author: andre
"""

views = model.views
orgs = model.organizations

orgs = orgs[orgs.level1=='Views']

data = orgs.merge(views, how='inner', left_on='idRef', right_on='id')
data.columns
data_views = data[['id', 'level1', 'level2', 'level3', 'name']]

data_views.to_csv('view_evaluation_data.csv')