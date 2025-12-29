from unittest import result

import pygame
import turtle
import time
import random
import os, sys

#===========================================================
#FOLDER LOADING
#===========================================================
wn = turtle.Screen()
t = turtle.Turtle()
t.hideturtle()

def Load_folder(folder):
    result = {}
    if not(os.path.isdir(folder)):
        print(f"Warning: folder '{folder}' not found.")
        return result

    for filename in os.listdir(folder):
        if filename.lower().endswith(".gif"):
            path = os.path.join(folder, filename)
            wn.addshape(path)
            key = os.path.splitext(filename)[0]
            result[key] = path
            print("Registered Shape:", key, "->", path)
    return result

def Load_Gifs_From(folder):
    result = {}
    if not(os.path.isdir(folder)):
        print(f"Warning: folder '{folder}' not found.")
        return result
    for filename in os.listdir(folder):
        if filename.lower().endswith(".gif"):
            path = os.path.join(folder, filename)
            wn.addshape(path)
            key = os.path.splitext(filename)[0]
            result[key] = path
            print("Registered Shape:", key, "->", path)
    return result


sprites = Load_Gifs_From("sprites")
backgrounds = Load_Gifs_From("backgrounds")

#===========================================================
#GLOBALS
#===========================================================
blink_turtle = turtle.Turtle()
game_started = False
blinking = False
blink_turtle.hideturtle()
blink_turtle.penup()
Rotten_Apple = False
Rotten_Lemon = False
Good_Lemon = True
Debug_List = True

#===========================================================
#MENU
#===========================================================





#===========================================================
#Screen Setup
#===========================================================
t = turtle.Turtle()
t.hideturtle()
wn = turtle.Screen()
wn.background = "black"
wn.bgcolor("black")
wn.setup(width = 1920, height = 1080)

t.goto(-700, 400)
t.color("white")
wn.bgpic(backgrounds["Options_BG"])
wn.exitonclick()

# Test Script for Catch That Lemon by Dave Luisterburg
# From head only. This is to test my knowledge.