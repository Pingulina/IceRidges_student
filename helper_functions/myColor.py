import os
import numpy as np

# make a dictionary with dot notation
from dotdict import Map

# dict named params, that contains all parameters
myColor = Map({}) # dict() with dotdict functionality

myColor['dark_red'] = lambda a: f'rgba(215,48,39,{a})'
myColor['orange'] = lambda a: f'rgba(252,141,89,{a})'
myColor['yellow'] = lambda a: f'rgba(254,224,144,{a})'
myColor['light_blue'] = lambda a: f'rgba(224,243,248,{a})'
myColor['mid_blue'] = lambda a: f'rgba(145,191,219,{a})'
myColor['dark_blue'] = lambda a: f'rgba(69,117,180,{a})'
myColor['black'] = lambda a: f'rgba(0,0,0,{a})'
myColor['green'] = lambda a: f'rgba(145,207,96,{a})'
myColor['grey'] = lambda a: f'rgba(150,150,150,{a})'
myColor['light_grey'] = lambda a: f'rgba(200,200,200,{a})'

myColor['tab_selected'] = myColor['light_grey'](1)
myColor['tab_unselected'] = myColor['light_grey'](1)
myColor['text_selected'] = myColor['black'](1)
myColor['text_unselected'] = myColor['grey'](1)

