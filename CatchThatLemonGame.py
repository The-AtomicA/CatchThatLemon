import turtle
import time
import random
import pygame
import os, sys
import tkinter as tk

# =================================================================================
# Catch That Lemon Game by Dave Luisterburg
# =================================================================================

# TODO LIST:
# - Troubleshoot 180 Flip
# - Add Bossfight
# - Add different sounds to different Food Items.
# - Spice up menu's
# - Add more options in Options Menu
# - Implement new features
# - HD Sprites?
# - Improve eating and spawning animations
# - Add Better Game Over screen


# =================================================================================
# Debug
# =================================================================================

def resource_path(*parts):
    """
    Works in dev and in PyInstaller builds.
    """
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, *parts)

print("turtle module file:", turtle.__file__)
print("has Screen:", hasattr(turtle, "Screen"))


# =================================================================================
# Sound Settings
# =================================================================================
bgm_volume = 1.0
current_screen = "menu"


def set_bgm_volume(vol: float):
   global bgm_volume
   bgm_volume = max(0.0, min(1.0, vol))
   pygame.mixer.music.set_volume(bgm_volume)


def play_bgm_music(filename):
   pygame.mixer.music.load(filename)
   set_bgm_volume(bgm_volume)
   pygame.mixer.music.play(-1)


# -- Pygame Mixer --
pygame.mixer.init()


# ==================================================================================
# Difficulty Settings
# ==================================================================================


difficulty = "Easy"   # Classic, Easy, Medium, Hard


def cycle_difficulty():
   global difficulty
   modes = ["Classic", "Easy", "Medium", "Hard"]
   i = modes.index(difficulty)
   difficulty = modes[(i + 1) % len(modes)]
   play_sfx("sounds/Plop.wav")
   show_menu()




DIFFICULTY_SETTINGS = {
   "Classic": {
       "spawn_rotten": 0.0,
       "spawn_rotten2": 0.0,
       "spawn_apple": 0.0,
       "spawn_banana": 0.0,
       "speed_bonus": 0.0,
       "obstacles": False,
       "boss_mode": False,
   },
   "Easy": {
       "spawn_rotten": 0.2,
       "spawn_rotten2": 0.1,
       "spawn_apple": 0.10,
       "spawn_banana": 0.02,
       "speed_bonus": 0.001,
       "obstacles": False,
       "boss_mode": False,
   },
   "Medium": {
       "spawn_rotten": 0.35,
       "spawn_rotten2": 0.25,
       "spawn_rotten3": 0.15,
       "spawn_apple": 0.12,
       "spawn_banana": 0.04,
       "speed_bonus": 0.002,
       "obstacles": True,
       "obstacle_count": 6,
       "boss_mode": False,
   },
   "Hard": {
       "spawn_rotten": 0.80,
       "spawn_rotten2": 0.70,
       "spawn_rotten3": 0.60,
       "spawn_rotten4": 0.60,
       "spawn_apple": 0.10,
       "spawn_banana": 0.01,
       "speed_bonus": 0.004,
       "obstacles": True,
       "obstacle_count": 12,
       "boss_mode": True,
       # TODO Implement Boss Mode.
   }
}




# =================================================================================
# Leaderboard Settings
# =================================================================================


import hashlib




def get_save_path(filename):
   base = os.getenv("APPDATA") or os.path.expanduser("~")
   save_dir = os.path.join(base, "CatchThatLemon")
   os.makedirs(save_dir, exist_ok=True)
   return os.path.join(save_dir, filename)


def save_secure_high_score(score: int):
   score_str = str(int(score))
   checksum = hashlib.sha256(score_str.encode()).hexdigest()
   with open(SECURE_HIGH_SCORE_FILE, "w") as f:
       f.write(score_str + "|" + checksum)




def load_secure_high_score() -> int:
   try:
       text = open(SECURE_HIGH_SCORE_FILE).read().strip()
       if "|" not in text:
           return 0


       score_str, checksum = text.split("|")


       # Validate checksum
       expected = hashlib.sha256(score_str.encode()).hexdigest()
       if checksum == expected:
           return int(score_str)
       else:
           print("⚠ High Score file was tampered with — resetting!")
           return 0
   except:
       return 0




def leaderboard_file_for(diff: str) -> str:
   diff = diff.lower()
   return get_save_path(f"leaderboard_{diff}.dat")  # uses your AppData helper


MAX_LEADERBOARD_ENTRIES = 5
SECURE_HIGH_SCORE_FILE = get_save_path("highscore_secure.dat")


def save_secure_leaderboard(entries, diff: str):
   path = leaderboard_file_for(diff)
   with open(path, "w", encoding="utf-8") as f:
       for name, score in entries[:MAX_LEADERBOARD_ENTRIES]:
           payload = f"{name}|{score}"
           checksum = hashlib.sha256(payload.encode()).hexdigest()
           f.write(payload + "|" + checksum + "\n")




def load_secure_leaderboard(diff: str):
   path = leaderboard_file_for(diff)
   entries = []
   try:
       with open(path, "r", encoding="utf-8") as f:
           for line in f:
               line = line.strip()
               parts = line.split("|")
               if len(parts) != 3:
                   continue
               name, score_str, checksum = parts
               payload = f"{name}|{score_str}"
               expected = hashlib.sha256(payload.encode()).hexdigest()
               if checksum != expected:
                   continue
               try:
                   entries.append((name, int(score_str)))
               except:
                   pass
   except FileNotFoundError:
       return []


   return sorted(entries, key=lambda e: e[1], reverse=True)








def maybe_update_leaderboard(final_score, diff: str):
   if final_score <= 0:
       return


   entries = load_secure_leaderboard(diff)


   qualifies = (len(entries) < MAX_LEADERBOARD_ENTRIES) or (final_score > entries[-1][1])
   if not qualifies:
       return


   name = wn.textinput("New Leaderboard Score!", f"[{diff}] You scored {final_score}!\nEnter your name:")
   if not name or name.strip() == "":
       name = "Player"
   name = name.strip()


   entries.append((name, final_score))
   entries.sort(key=lambda e: e[1], reverse=True)
   save_secure_leaderboard(entries, diff)
   wn.listen()








# ========================================================================
# Music Definitions
# ========================================================================


def play_music():
   pygame.mixer.music.load("sounds/Game_BGM2.wav")
   set_bgm_volume(bgm_volume)
   pygame.mixer.music.play(-1)


def stop_music():
   pygame.mixer.music.stop()


def play_sfx(filename, volume=1.0):
   sound = pygame.mixer.Sound(filename)
   sound.set_volume(volume)
   sound.play()


def play_bgm_music(filename):
   pygame.mixer.music.load(filename)
   set_bgm_volume(bgm_volume)
   pygame.mixer.music.play(-1)


# =================================================================================
# Globals
# =================================================================================


# --- Global state ---
game_started = False
play_bgm_music("sounds/Menu_Music.mp3")
rotten_food = None
rotten_active = False
rotten2_food = None
rotten2_active = False
rotten3_food = None
rotten3_active = False
rotten4_food = None
rotten4_active = False
apple_active = False
apple_food = None
banana_food = None
banana_active = False
blink_turtle = turtle.Turtle()
blink_turtle.hideturtle()
blink_turtle.penup()
spawn_anims = {}
obstacles = []
obstacles_active = False
blink_timer_id = None






# -- Reverse Control Mechanics --
reverse_controls = False
reverse_timer = 0.0
if reverse_controls and time.time() > reverse_timer:
   reverse_controls = False




# =================================================================================
# Menu Screen
# =================================================================================


# --- Screen setup ---
wn = turtle.Screen()
wn.title("Catch that Lemon V0.3.1 Demo Version")
wn.bgcolor("black")
wn.setup(width=1600, height=820)


# --- Blinking "Press O for Options" text ---
blink_turtle = turtle.Turtle()
blink_turtle.hideturtle()
blink_turtle.penup()
blink_turtle.color("black")


# Main text turtle (menu text)
t = turtle.Turtle()
t.hideturtle()
t.color("white")


# Menu graphics turtles
bg_logo = turtle.Turtle()
bg_logo.hideturtle()
char_logo = turtle.Turtle()
char_logo.hideturtle()


# =================================================================================
# Graphics
# =================================================================================
def head_hit_animation():
   """Little left-right shake when the snake dies."""
   if head is None:
       return


   ox = head.xcor()
   oy = head.ycor()


   # Sequence of small x offsets
   wiggle = [-10, 10, -8, 8, -5, 5, 0]


   for dx in wiggle:
       head.goto(ox + dx, oy)
       wn.update()
       time.sleep(0.03)


   # Make sure it ends exactly centered
   head.goto(ox, oy)
   wn.update()


def head_bite_animation():
   """Small forward chomp in the direction of movement."""
   if head is None:
       return


   ox = head.xcor()
   oy = head.ycor()


   # How far forward to 'bite'
   step = 10


   if head.direction == "up":
       head.goto(ox, oy + step)
   elif head.direction == "down":
       head.goto(ox, oy - step)
   elif head.direction == "left":
       head.goto(ox - step, oy)
   elif head.direction == "right":
       head.goto(ox + step, oy)
   else:
       return  # not moving, no bite


   wn.update()
   time.sleep(0.04)


   # Snap back
   head.goto(ox, oy)
   wn.update()




blink_visible = True
blink_timer_id = None
blink_session = 0


def blink_options_text(session_id):
    global blink_visible

    try:
        if session_id != blink_session:
            return

        if current_screen != "menu":
            blink_turtle.clear()
            return

        blink_turtle.clear()

        if blink_visible:
            blink_turtle.goto(0, -175)
            blink_turtle.color("black")  # <-- IMPORTANT
            blink_turtle.write("Press O for Options", align="center", font=("Arial", 25, "bold"))

        blink_visible = not blink_visible
        wn.ontimer(lambda: blink_options_text(session_id), 500)

    except (turtle.Terminator, tk.TclError):
        return

# --- Sprite loader ---
def load_gifs_from(folder):
   result = {}
   if not os.path.isdir(folder):
       print(f"Warning: folder '{folder}' not found.")
       return result


   for filename in os.listdir(folder):
       if filename.lower().endswith(".gif"):
           path = os.path.join(folder, filename)
           wn.addshape(path)
           key = os.path.splitext(filename)[0]  # "Lemon.gif" -> "Lemon"
           result[key] = path
           print("Registered shape:", key, "->", path)
   return result


sprites = load_gifs_from("sprites")
backgrounds = load_gifs_from("backgrounds")


# --- Game objects (will be created later in start_game) ---
head = None
food = None
segments = []
pen = None
score = 0
high_score = load_secure_high_score()
delay = 0.1


def random_safe_position(margin=40, extra_forbidden=None):
   """
   Pick a random (x, y) inside the playfield that is not too close
   to the snake, or any item. `margin` is the minimum allowed distance in pixels.
   """
   # Build a list of objects we want to avoid
   forbidden = []


   if head is not None:
       forbidden.append(head)


   for obj in (food, rotten_food, rotten2_food, rotten3_food, rotten4_food, apple_food, banana_food):
       if obj is not None:
           forbidden.append(obj)


   for ob in obstacles:
       forbidden.append(ob)


   # Avoid body segments
   forbidden.extend(segments)




   # Optional extra stuff to avoid (like: don't spawn rotten on top of food)
   if extra_forbidden:
       forbidden.extend(extra_forbidden)


   while True:
       x = random.randint(-280, 280)
       y = random.randint(-280, 280)


       too_close = False
       for obj in forbidden:
           # distance(x, y) works on turtles
           if obj.distance(x, y) < margin:
               too_close = True
               break


       if not too_close:
           return x, y




def clear_obstacles():
   global obstacles, obstacles_active
   for ob in obstacles:
       ob.goto(1000, 1000)
       ob.hideturtle()
   obstacles.clear()
   obstacles_active = False




def spawn_obstacles(count):
   global obstacles, obstacles_active


   clear_obstacles()
   if count <= 0:
       return


   for _ in range(count):
       ob = turtle.Turtle()
       ob.speed(0)
       ob.penup()
       ob.shape(sprites["Spike"])
       ob.shapesize(stretch_wid=1, stretch_len=1)


       x, y = random_safe_position(margin=80)
       ob.goto(x, y)
       ob.showturtle()
       obstacles.append(ob)


   obstacles_active = True


# ===============================================================================
# Game Screens
# ===============================================================================


def show_menu():
   global current_screen, blink_visible, blink_session
   current_screen = "menu"

   t.clear()
   wn.bgcolor("black")
   wn.bgpic(backgrounds["MenuScreen"])
   play_bgm_music("sounds/Menu_Music.mp3")

   t.color("black")
   t.penup()

   # Credits
   t.goto(0, -400)
   t.write(
       "V0.3.1 Demo Version                                                                                                                                                    Made by AtomicA, more updates will come soon!",
       align="center",
       font=("Arial", 16, "bold")
   )

   t.goto(0, -300)
   t.write(
       f"Difficulty: {difficulty}  (Press X to change)",
       align="center",
       font=("Arial", 22, "bold")
   )

   blink_visible = True
   blink_turtle.clear()
   blink_session += 1
   blink_options_text(blink_session)


   wn.listen()
   wn.onkey(start_game, "Return")
   wn.onkey(cycle_difficulty, "x")
   wn.onkey(cycle_difficulty, "X")



def show_options_menu():
   global current_screen
   current_screen = "options"
   t.clear()


   wn.bgcolor("black")
   wn.bgpic(backgrounds["Options_BG"])
   play_bgm_music("sounds/Menu_Music.mp3")


   # ======================
   # LEFT SIDE: OPTIONS
   # ======================
   t.color("white")
   t.penup()
   t.goto(-460, 200)
   t.write("OPTIONS", align="center", font=("Arial", 40, "bold"))


   # Volume label
   t.goto(-460, 120)
   t.write("Music Volume", align="center", font=("Arial", 20, "bold"))


   # Volume bar
   bar_length = int(bgm_volume * 20)
   bar = "[" + "#" * bar_length + "-" * (20 - bar_length) + "]"


   t.goto(-450, 70)
   t.write(f"{bar}  {int(bgm_volume * 100)}%",
           align="center", font=("Consolas", 18))


   t.goto(-460, -20)
   t.write("A / Left: -   |   D / Right: +",
           align="center", font=("Arial", 14))


   t.goto(-460, -70)
   t.write("Press B or ESC to go back",
           align="center", font=("Arial", 14))


   # ===========================
   # RIGHT SIDE: LEADERBOARD
   # ===========================
   entries = load_secure_leaderboard(difficulty)   # <- SECURE leaderboard
   if entries:
       t.goto(460, 250)
       t.goto(460, 250)
       t.write(
           f"Leaderboard ({difficulty}) - Top {MAX_LEADERBOARD_ENTRIES}",
           align="center",
           font=("Arial", 20, "bold"),
       )


       start_y = 170
       line_spacing = 80


       for i, (name, s) in enumerate(entries[:MAX_LEADERBOARD_ENTRIES], start=1):
           t.goto(460, start_y - (i * line_spacing))
           t.write(
               f"{i}. {name} - {s}",
               align="center",
               font=("Arial", 25, "normal"),
       )


   else:
       # No entries yet
       t.goto(460, 200)
       t.write("Leaderboard", align="center", font=("Arial", 22, "bold"))
       t.goto(460, 160)
       t.write("No scores yet – go play!", align="center", font=("Arial", 14))






def show_game_over(final_score):
   global current_screen, game_started
   current_screen = "game_over"
   game_started = False   # stop gameplay updates


   t.clear()
   clear_obstacles()
   wn.bgcolor("black")
   wn.bgpic("")


   t.color("white")
   t.penup()


   # Title
   t.goto(0, 120)
   t.write("GAME OVER", align="center", font=("Arial", 40, "bold"))


   # Final score
   t.goto(0, 40)
   t.write(f"Your score: {final_score}", align="center",
           font=("Arial", 24, "normal"))


   # Best score
   t.goto(0, -10)
   t.write(f"Best score: {high_score}", align="center",
           font=("Arial", 20, "normal"))


   # Instructions
   t.goto(0, -80)
   t.write("Press R to Retry!", align="center",
           font=("Arial", 16, "normal"))


   t.goto(0, -120)
   t.write("Press M for Main Menu!", align="center",
           font=("Arial", 16, "normal"))


   t.goto(0, -160)
   t.write("Press O for Options!", align="center",
           font=("Arial", 16, "normal"))


   # 🔑 Re-enable key listening and re-bind controls
   wn.listen()
   wn.onkey(start_game, "R")
   wn.onkey(start_game, "r")
   wn.onkey(show_menu, "m")
   wn.onkey(show_menu, "M")




def options_volume_up():
   if current_screen != "options":
       return
   set_bgm_volume(bgm_volume + 0.05)
   play_sfx("sounds/Plop.wav")
   show_options_menu()




def options_volume_down():
   if current_screen != "options":
       return
   set_bgm_volume(bgm_volume - 0.05)
   play_sfx("sounds/Plop.wav")
   show_options_menu()




def options_back():
   global current_screen
   if current_screen != "options":
       return


   t.clear()


   if game_started:
       # Resume game
       current_screen = "game"
       wn.bgpic(backgrounds["Game_BG"])
       play_bgm_music("sounds/Game_BGM2.wav")


   else:
       t.clear()
       show_menu()


# =================================================================================
# Rotation of Segments
# =================================================================================


# Rotational Segments
def update_body_sprites():
   # Skip if no body segments
   if len(segments) < 1:
       return


   # For every body segment, determine orientation
   for i in range(len(segments)):
       seg = segments[i]


       # Determine the direction this segment is moving
       if i == 0:
           # first segment follows the head
           prev = head
       else:
           prev = segments[i - 1]


       # Compare x/y positions to decide orientation
       if abs(seg.xcor() - prev.xcor()) > abs(seg.ycor() - prev.ycor()):
           seg.shape(sprites["Snake_Segment_Horizontal"])  # moving horizontally
       else:
           seg.shape(sprites["Snake_Segment_Vertical"])  # moving vertically


# -------------------------------------------------
# Non-blocking blink spawn animation for items
# -------------------------------------------------
spawn_anims = {}


def start_spawn_animation(turt, duration=0.25):
   """
   Start a non-blocking blink animation for this turtle.
   Works with GIF sprites (hide/show).
   """
   spawn_anims[turt] = {
       "start": time.time(),
       "duration": duration,
   }
   turt.showturtle()



def update_spawn_animations():

   now = time.time()
   finished = []


   for turt, data in spawn_anims.items():
       start = data["start"]
       dur = data["duration"]
       rel = (now - start) / dur  # 0.0 → 1.0


       if rel >= 1.0:
           turt.showturtle()
           finished.append(turt)
           continue



       phase = int(rel * 20)


       # Even phases: visible, odd: hidden
       if phase % 2 == 0:
           turt.showturtle()
       else:
           turt.hideturtle()


   for turt in finished:
       spawn_anims.pop(turt, None)




# =================================================================================
# Snake Segments
# =================================================================================


# -- New Segment Positions --
def get_new_segment_position():
   """
   Returns an (x, y) for where the new body segment should spawn.
   """
   if len(segments) == 0:
       # No segments yet -> follow the head
       follower = head
   else:
       # Follow last segment of Snake
       follower = segments[-1]


   x = follower.xcor()
   y = follower.ycor()


   # Offset backwards based on direction
   if follower == head:
       direction = head.direction
   else:
       # Determine direction of this segment by comparing with the segment in front
       if len(segments) == 1:
           prev = head
       else:
           prev = segments[-2]


       dx = follower.xcor() - prev.xcor()
       dy = follower.ycor() - prev.ycor()


       if abs(dx) > abs(dy):
           direction = "right" if dx > 0 else "left"
       else:
           direction = "up" if dy > 0 else "down"


   if direction == "up":
       y -= 20
   elif direction == "down":
       y += 20
   elif direction == "left":
       x += 20
   elif direction == "right":
       x -= 20


   return x, y




# ===========================================================================
# STARTING GAME
# ===========================================================================


def start_game():
   global game_started, head, food, pen, segments, score, high_score, delay
   global rotten_food, rotten_active, apple_food, apple_active
   global reverse_timer, reverse_controls
   global banana_food, banana_active, current_screen
   if game_started:
       return  # don't start twice


   game_started = True
   current_screen = "game"


   # Clear menu visuals
   t.clear()
   bg_logo.hideturtle()
   char_logo.hideturtle()
   pygame.mixer.music.stop()
   play_music()




   # =================================================================================
   # Game Screen
   # =================================================================================


   # Adjust screen for the game
   wn.clear()
   wn.setup(width=1600, height=820)
   wn.tracer(0)
   wn.bgpic(backgrounds["Game_BG"])




   t.goto(0, -325)
   t.color("black")
   t.write(
       "Made by AtomicA",
       align="center",
       font=("Arial", 10, "bold"),
   )




   # =================================================================================
   # Item Sprites
   # =================================================================================


   # --- Snake head ---
   head = turtle.Turtle()
   head.speed(0)
   head.shape(sprites["Snake_Up"])
   head.penup()
   head.goto(0, 0)
   head.direction = "stop"


   # --- Snake food ---
   food = turtle.Turtle()
   food.speed(0)
   food.shape(sprites["Lemon"])
   food.color("yellow")
   food.penup()
   food.goto(0, 100)


   # --- Rotten lemon (danger!) ---
   global rotten_food, rotten_active
   rotten_food = turtle.Turtle()
   rotten_food.speed(0)
   rotten_food.penup()
   rotten_food.shape(sprites["Rotten_Lemon"])
   rotten_food.goto(1000, 1000)
   rotten_active = False


   # --- Second Rotten lemon (danger!) ---
   global rotten2_food, rotten2_active
   rotten2_food = turtle.Turtle()
   rotten2_food.speed(0)
   rotten2_food.penup()
   rotten2_food.shape(sprites["Rotten_Lemon"])
   rotten2_food.goto(1000, 1000)
   rotten2_active = False


   # --- Third Rotten lemon (danger!) ---
   global rotten3_food, rotten3_active
   rotten3_food = turtle.Turtle()
   rotten3_food.speed(0)
   rotten3_food.penup()
   rotten3_food.shape(sprites["Rotten_Lemon"])
   rotten3_food.goto(1000, 1000)
   rotten3_active = False


   # --- Fourth Rotten lemon (danger!) ---
   global rotten4_food, rotten4_active
   rotten4_food = turtle.Turtle()
   rotten4_food.speed(0)
   rotten4_food.penup()
   rotten4_food.shape(sprites["Rotten_Lemon"])
   rotten4_food.goto(1000, 1000)
   rotten4_active = False


   # --- Apple ---
   global apple_food, apple_active
   apple_food = turtle.Turtle()
   apple_food.speed(0)
   apple_food.penup()
   apple_food.shape(sprites["Apple"])
   apple_food.goto(1000, 1000)
   apple_active = False


   # --- Banana ---
   global banana_food, banana_active
   banana_food = turtle.Turtle()
   banana_food.speed(0)
   banana_food.penup()
   banana_food.shape(sprites["Banana"])
   banana_food.goto(1000, 1000)
   banana_active = False


   # --- Snake body segments ---
   segments = []


   D = DIFFICULTY_SETTINGS[difficulty]
   if D.get("obstacles", False):
       spawn_obstacles(D.get("obstacle_count", 0))
   else:
       clear_obstacles()
# =================================================================================
#   Scoring
# =================================================================================


   # --- Score text ---
   score = 0
   # keep existing high_score from file!
   delay = 0.1


   pen = turtle.Turtle()
   pen.speed(0)
   pen.shape("circle")
   pen.color("black")
   pen.penup()
   pen.hideturtle()
   pen.goto(0, 320)
   pen.write(f"Current Score: {score}  High Score: {high_score}",
             align="center", font=("Arial", 24, "bold"))


   # =================================================================================
   # Keybinds
   # =================================================================================

   # TODO: Troubleshoot and clean up.
   # TODO: Find a way to make rebinding possible in Options Menu



   # Keyboard bindings for movement
   wn.listen()
   wn.onkeypress(go_up, "w")
   wn.onkeypress(go_up, "Up")
   wn.onkeypress(go_down, "s")
   wn.onkeypress(go_down, "Down")
   wn.onkeypress(go_left, "a")
   wn.onkeypress(go_left, "Left")
   wn.onkeypress(go_right, "d")
   wn.onkeypress(go_right, "Right")


   wn.onkey(show_options_menu, "o")
   wn.onkey(show_options_menu, "O")


   wn.onkey(options_volume_up, "d")
   wn.onkey(options_volume_up, "D")
   wn.onkey(options_volume_up, "Right")


   wn.onkey(options_volume_down, "a")
   wn.onkey(options_volume_down, "A")
   wn.onkey(options_volume_down, "Left")


   wn.onkey(options_back, "b")
   wn.onkey(options_back, "B")
   wn.onkey(options_back, "Escape")




def opposite_direction(direction: str) -> str:
   if direction == "up":
       return "down"
   if direction == "down":
       return "up"
   if direction == "left":
       return "right"
   if direction == "right":
       return "left"
   return direction




# --- Functions to control the snake ---
def go_up():
   global head, reverse_controls
   desired = "up"
   if reverse_controls:
       desired = "down"  # flipped


   # block instant 180° flip so snake cannot kill itself
   # TODO Sometimes 180 flip still possible, Troubleshoot
   if head.direction != opposite_direction(desired):
       head.direction = desired




def go_down():
   global head, reverse_controls
   desired = "down"
   if reverse_controls:
       desired = "up"


   if head.direction != opposite_direction(desired):
       head.direction = desired




def go_left():
   global head, reverse_controls
   desired = "left"
   if reverse_controls:
       desired = "right"


   if head.direction != opposite_direction(desired):
       head.direction = desired




def go_right():
   global head, reverse_controls
   desired = "right"
   if reverse_controls:
       desired = "left"


   if head.direction != opposite_direction(desired):
       head.direction = desired






def move():
   if head.direction == "up":
       y = head.ycor()
       head.sety(y + 20)
       head.shape(sprites["Snake_Up"])


   if head.direction == "down":
       y = head.ycor()
       head.sety(y - 20)
       head.shape(sprites["Snake_Down"])


   if head.direction == "left":
       x = head.xcor()
       head.setx(x - 20)
       head.shape(sprites["Snake_Left"])


   if head.direction == "right":
       x = head.xcor()
       head.setx(x + 20)
       head.shape(sprites["Snake_Right"])




# --- Show menu and bind ENTER to start_game ---
show_menu()
wn.listen()


# Main menu bindings
wn.onkey(start_game, "Return")
wn.onkey(start_game, "KP_Enter")  # numpad enter just in case
wn.onkey(show_options_menu, "o")
wn.onkey(show_options_menu, "O")


wn.onkey(cycle_difficulty, "x")
wn.onkey(cycle_difficulty, "X")


# Options menu controls
wn.onkey(options_volume_up, "d")
wn.onkey(options_volume_up, "D")
wn.onkey(options_volume_up, "Right")


wn.onkey(options_volume_down, "a")
wn.onkey(options_volume_down, "A")
wn.onkey(options_volume_down, "Left")


wn.onkey(options_back, "b")
wn.onkey(options_back, "B")
wn.onkey(options_back, "Escape")


# =================================================================================
# Game Loop
# =================================================================================

try:
    while True:
        wn.update()

        # If we are in OPTIONS, pause all gameplay updates
        if current_screen == "options":
            time.sleep(0.05)
            continue

        # If game hasn't started yet, just idle
        if not game_started:
            time.sleep(0.05)
            continue

        # turn off reverse controls when time is up
        if reverse_controls and time.time() >= reverse_timer:
            reverse_controls = False

        # --- Collision with border ---
        if (head.xcor() > 290 or head.xcor() < -290 or
                head.ycor() > 290 or head.ycor() < -290):
            play_sfx("sounds/Death.wav")
            head_hit_animation()
            time.sleep(1)

            # Hide snake
            head.goto(1000, 1000)
            head.direction = "stop"

            for segment in segments:
                segment.goto(1000, 1000)
            segments.clear()

            # Hide items
            rotten_food.goto(1000, 1000)
            rotten_active = False
            rotten2_food.goto(1000, 1000)
            rotten2_active = False
            rotten3_food.goto(1000, 1000)
            rotten3_active = False
            rotten4_food.goto(1000, 1000)
            rotten4_active = False
            apple_food.goto(1000, 1000)
            apple_active = False
            banana_food.goto(1000, 1000)
            banana_active = False
            reverse_controls = False

            # Leaderboard + highscore
            if score > 0:
                maybe_update_leaderboard(score, difficulty)
                if score > high_score:
                    high_score = score
                    save_secure_high_score(high_score)

            # Show Game Over screen
            show_game_over(score)

            # Prepare values for next round
            score = 0
            delay = 0.1
            continue

        # --- Collision with own body ---
        for segment in segments:
            if segment.distance(head) < 20:
                play_sfx("sounds/Death.wav")
                head_hit_animation()
                time.sleep(1)

                head.goto(1000, 1000)
                head.direction = "stop"

                for segment in segments:
                    segment.goto(1000, 1000)
                segments.clear()

                rotten_food.goto(1000, 1000)
                rotten_active = False
                rotten2_food.goto(1000, 1000)
                rotten2_active = False
                rotten3_food.goto(1000, 1000)
                rotten3_active = False
                rotten4_food.goto(1000, 1000)
                rotten4_active = False
                apple_food.goto(1000, 1000)
                apple_active = False
                banana_food.goto(1000, 1000)
                banana_active = False
                reverse_controls = False

                if score > 0:
                    maybe_update_leaderboard(score, difficulty)
                    if score > high_score:
                        high_score = score
                        save_secure_high_score(high_score)

                show_game_over(score)

                score = 0
                delay = 0.1
                break

        if obstacles_active:
            for ob in obstacles:
                if head.distance(ob) < 20:
                    play_sfx("sounds/Death.wav")
                    head_hit_animation()
                    time.sleep(1)

                    # Hide snake
                    head.goto(1000, 1000)
                    head.direction = "stop"

                    for segment in segments:
                        segment.goto(1000, 1000)
                    segments.clear()

                    # Hide items
                    rotten_food.goto(1000, 1000)
                    rotten_active = False
                    rotten2_food.goto(1000, 1000)
                    rotten2_active = False
                    rotten3_food.goto(1000, 1000)
                    rotten3_active = False
                    rotten4_food.goto(1000, 1000)
                    rotten4_active = False
                    apple_food.goto(1000, 1000)
                    apple_active = False
                    banana_food.goto(1000, 1000)
                    banana_active = False
                    reverse_controls = False

                    # Leaderboard + highscore
                    if score > 0:
                        maybe_update_leaderboard(score, difficulty)
                        if score > high_score:
                            high_score = score
                            save_secure_high_score(high_score)

                    # Show Game Over screen
                    show_game_over(score)
                    clear_obstacles()

                    # Prepare values for next round
                    score = 0
                    delay = 0.1
                    continue

        # ====================================================================================
        # ITEMS
        # ====================================================================================
        D = DIFFICULTY_SETTINGS[difficulty]

        # --- Collision with good lemon ---
        if head.distance(food) < 20:
            play_sfx("sounds/Bite.wav")
            head_bite_animation()

            # Move food to a safe random spot
            x, y = random_safe_position(margin=40)
            food.goto(x, y)
            start_spawn_animation(food, duration=0.25)
            play_sfx("sounds/Plop.wav")

            # Add a new segment
            new_segment = turtle.Turtle()
            new_segment.speed(0)
            new_segment.penup()

            # First segment: spawn just behind the head
            if len(segments) == 0:
                sx = head.xcor()
                sy = head.ycor()
                if head.direction == "up":
                    sy -= 20
                elif head.direction == "down":
                    sy += 20
                elif head.direction == "left":
                    sx += 20
                elif head.direction == "right":
                    sx -= 20
                new_segment.goto(sx, sy)
            else:
                # Later segments: spawn off-screen, will snap into place
                new_segment.goto(1000, 1000)

            segments.append(new_segment)

            # --- Rotten lemon 1 spawn ---
            if random.random() < D["spawn_rotten"]:
                rx, ry = random_safe_position(margin=40)
                rotten_food.goto(rx, ry)
                rotten_active = True
            else:
                rotten_food.goto(1000, 1000)
                rotten_active = False

            # --- Rotten lemon 2 spawn ---
            if random.random() < D["spawn_rotten2"]:
                rx, ry = random_safe_position(margin=40)
                rotten2_food.goto(rx, ry)
                rotten2_active = True
            else:
                rotten2_food.goto(1000, 1000)
                rotten2_active = False

            # --- Rotten lemon 3 spawn ---
            if random.random() < D.get("spawn_rotten3", 0.0):
                rx, ry = random_safe_position(margin=40)
                rotten3_food.goto(rx, ry)
                rotten3_active = True
            else:
                rotten3_food.goto(1000, 1000)
                rotten3_active = False

            # --- Rotten lemon 4 spawn ---
            if random.random() < D.get("spawn_rotten4", 0.0):
                rx, ry = random_safe_position(margin=40)
                rotten4_food.goto(rx, ry)
                rotten4_active = True
            else:
                rotten4_food.goto(1000, 1000)
                rotten4_active = False

            # Chance for banana to spawn
            if random.random() < D["spawn_banana"]:
                rx, ry = random_safe_position(margin=40)
                banana_food.goto(rx, ry)
                banana_active = True
            else:
                banana_food.goto(1000, 1000)
                banana_active = False

            # Chance for apple to spawn
            if random.random() < D["spawn_apple"]:
                rx, ry = random_safe_position(margin=40)
                apple_food.goto(rx, ry)
                apple_active = True
            else:
                apple_food.goto(1000, 1000)
                apple_active = False

            # Shorten delay (speed up)
            delay = max(0.03, delay - D["speed_bonus"])

            # Increase score by 1
            score += 1
            if score > high_score:
                high_score = score
                save_secure_high_score(high_score)

            pen.clear()
            pen.write(f"Current Score: {score}  High Score: {high_score}",
                      align="center", font=("Arial", 24, "bold"))

        # --- Collision with Banana (check EVERY frame) ---
        if banana_active and head.distance(banana_food) < 20:
            play_sfx("sounds/Hmmm.wav")
            score += 10
            if score > high_score:
                high_score = score
                save_secure_high_score(high_score)

            delay = max(0.03, delay - D["speed_bonus"])
            banana_food.goto(1000, 1000)
            banana_active = False

            pen.clear()
            pen.write(f"Current Score: {score}  High Score: {high_score}",
                      align="center", font=("Arial", 24, "bold"))

        # --- Collision with Apple(check EVERY frame) ---
        if apple_active and head.distance(apple_food) < 20:
            play_sfx("sounds/Hmmm.wav")
            reverse_controls = True
            reverse_timer = time.time() + 5

            score += 5
            if score > high_score:
                high_score = score
                save_secure_high_score(high_score)

            apple_food.goto(1000, 1000)
            apple_active = False

            pen.clear()
            pen.write(f"Current Score: {score}  High Score: {high_score}",
                      align="center", font=("Arial", 24, "bold"))

        # --- Collision with rotten lemon 1 (check EVERY frame) ---
        if rotten_active and head.distance(rotten_food) < 20:
            play_sfx("sounds/Blegh.wav")
            score -= 5
            rotten_food.goto(1000, 1000)
            rotten_active = False
            reverse_controls = False

            if score < 0:
                play_sfx("sounds/Death.wav")
                head_hit_animation()
                time.sleep(1)

                head.goto(1000, 1000)
                head.direction = "stop"
                for segment in segments:
                    segment.goto(1000, 1000)
                segments.clear()

                rotten_food.goto(1000, 1000); rotten_active = False
                rotten2_food.goto(1000, 1000); rotten2_active = False
                rotten3_food.goto(1000, 1000); rotten3_active = False
                rotten4_food.goto(1000, 1000); rotten4_active = False
                apple_food.goto(1000, 1000); apple_active = False
                banana_food.goto(1000, 1000); banana_active = False
                reverse_controls = False

                if score > 0:
                    maybe_update_leaderboard(score, difficulty)
                    if score > high_score:
                        high_score = score
                        save_secure_high_score(high_score)

                show_game_over(score)
                score = 0
                delay = 0.1
            else:
                pen.clear()
                pen.write(f"Current Score: {score}  High Score: {high_score}",
                          align="center", font=("Arial", 24, "bold"))

        # --- Collision with rotten lemon 2 (check EVERY frame) ---
        if rotten2_active and head.distance(rotten2_food) < 20:
            play_sfx("sounds/Blegh.wav")
            score -= 5
            rotten2_food.goto(1000, 1000)
            rotten2_active = False
            reverse_controls = False

            if score < 0:
                play_sfx("sounds/Death.wav")
                head_hit_animation()
                time.sleep(1)

                head.goto(1000, 1000)
                head.direction = "stop"
                for segment in segments:
                    segment.goto(1000, 1000)
                segments.clear()

                rotten_food.goto(1000, 1000); rotten_active = False
                rotten2_food.goto(1000, 1000); rotten2_active = False
                rotten3_food.goto(1000, 1000); rotten3_active = False
                rotten4_food.goto(1000, 1000); rotten4_active = False
                apple_food.goto(1000, 1000); apple_active = False
                banana_food.goto(1000, 1000); banana_active = False
                reverse_controls = False

                if score > 0:
                    maybe_update_leaderboard(score, difficulty)
                    if score > high_score:
                        high_score = score
                        save_secure_high_score(high_score)

                show_game_over(score)
                clear_obstacles()
                score = 0
                delay = 0.1
            else:
                pen.clear()
                pen.write(f"Current Score: {score}  High Score: {high_score}",
                          align="center", font=("Arial", 24, "bold"))

        # --- Collision with third rotten lemon ---
        if rotten3_active and head.distance(rotten3_food) < 20:
            play_sfx("sounds/Blegh.wav")
            score -= 5
            rotten3_food.goto(1000, 1000)
            rotten3_active = False
            reverse_controls = False

            if score < 0:
                play_sfx("sounds/Death.wav")
                head_hit_animation()
                time.sleep(1)

                head.goto(1000, 1000)
                head.direction = "stop"
                for segment in segments:
                    segment.goto(1000, 1000)
                segments.clear()

                rotten_food.goto(1000, 1000); rotten_active = False
                rotten2_food.goto(1000, 1000); rotten2_active = False
                rotten3_food.goto(1000, 1000); rotten3_active = False
                apple_food.goto(1000, 1000); apple_active = False
                banana_food.goto(1000, 1000); banana_active = False
                reverse_controls = False

                if score > 0:
                    maybe_update_leaderboard(score, difficulty)
                    if score > high_score:
                        high_score = score
                        save_secure_high_score(high_score)

                show_game_over(score)
                clear_obstacles()
                score = 0
                delay = 0.1
            else:
                pen.clear()
                pen.write(f"Current Score: {score}  High Score: {high_score}",
                          align="center", font=("Arial", 24, "bold"))

        # --- Collision with fourth rotten lemon ---
        if rotten4_active and head.distance(rotten4_food) < 20:
            play_sfx("sounds/Blegh.wav")
            score -= 5
            rotten4_food.goto(1000, 1000)
            rotten4_active = False
            reverse_controls = False

            if score < 0:
                play_sfx("sounds/Death.wav")
                head_hit_animation()
                time.sleep(1)

                head.goto(1000, 1000)
                head.direction = "stop"
                for segment in segments:
                    segment.goto(1000, 1000)
                segments.clear()

                rotten_food.goto(1000, 1000); rotten_active = False
                rotten2_food.goto(1000, 1000); rotten2_active = False
                rotten3_food.goto(1000, 1000); rotten3_active = False
                rotten4_food.goto(1000, 1000); rotten4_active = False
                apple_food.goto(1000, 1000); apple_active = False
                banana_food.goto(1000, 1000); banana_active = False
                reverse_controls = False

                if score > 0:
                    maybe_update_leaderboard(score, difficulty)
                    if score > high_score:
                        high_score = score
                        save_secure_high_score(high_score)

                show_game_over(score)
                clear_obstacles()
                score = 0
                delay = 0.1
            else:
                pen.clear()
                pen.write(f"Current Score: {score}  High Score: {high_score}",
                          align="center", font=("Arial", 24, "bold"))

        # =================================================================================
        # Movement
        # =================================================================================
        for index in range(len(segments) - 1, 0, -1):
            x = segments[index - 1].xcor()
            y = segments[index - 1].ycor()
            segments[index].goto(x, y)

        if len(segments) > 0:
            x = head.xcor()
            y = head.ycor()
            segments[0].goto(x, y)

        move()
        update_body_sprites()
        update_spawn_animations()

        time.sleep(delay)

except (turtle.Terminator, tk.TclError):
    try:
        pygame.mixer.quit()
    except:
        pass
    raise SystemExit

# ====================================================================================
# Catch That Lemon Game by Dave Luisterburg. V0.3.0
# ====================================================================================
