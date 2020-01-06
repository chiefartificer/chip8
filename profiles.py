# This module contains the configuration's profiles and functions
# New profiles may be added to the dictonary as needed

import pygame
import sys

profiles = {

"normal": {  
    "zoom": 10,
    "speed": 10,
    "shift_VY": 0,
    "debugging": "False", 
    "background_color": (0x99, 0xBD, 0x2A),
    "foreground_color": (0x2F, 0x63, 0x33)  
    },

"fast": {  
    "zoom": 10,
    "speed": 100000,
    "shift_VY": 0,
    "debugging": "False", 
    "background_color": (0xFA, 0x86, 0xC4),
    "foreground_color": (0xFF, 0xFF, 0xFF)  
    },

"debug": {  
    "zoom": 10,
    "speed": 10,
    "shift_VY": 0,
    "debugging": "True", 
    "background_color": (0xFF, 0xFF, 0xFF),
    "foreground_color": (0x00, 0x00, 0x00)  
    }
    
}

# Returns a profile dictionary if its name is provided as a string
def profile_get(name):
    try:
        return profiles[name]
    except:
        print("WRONG PROFILE NAME, USE SYNTAX: python main.py <FILE>, <profile>")
        print("EXAMPLE: python main.py INVADERS, normal")

        pygame.quit()
        sys.exit()
