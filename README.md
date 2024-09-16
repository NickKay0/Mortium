# Mortium: An Adventurer's Handbook
![Quick Demo](./static/images/screenshots/quick_demo1.gif)
## Welcome adventurer, to **Mortium**.

Mortium is my final project submission for **2024 Harvard CS50's** course. It's a *(medieval fantasy themed)* web application which aims to lighten travelers like *thyself*, from the burden of keeping track of all of your important quests and goals so you can truly focus on the most interesting aspect, **ADVENTURING**! Mortium offers quite a few features like Journal, Quests as well as keeping track of your completed tasks and thou level so you can see your progress in a single look. 

## ABOUT THE DEVELOPMENT
During the CS50 2024 course, I was absolutely *enthralled* by the ability to render dynamic html webpages through Python and Flask, writing and showing data through sql and as well setting up the whole enviroment. So when the time came for me to conceptualize what I wanted to do to farewell CS50 with a BANG with my final project, creating a web application was only natural. And I am very glad i did, because they were numerous knowledge roadblocks I triumphed and gain so much more knowledge and experience from them, and I am proudful of what I've created and I would love to share it. And as always, you can find the source code in my **GitHub** page, as well my other projects (older and future ones).

## BASIC OVERVIEW
Mortium is supposed to function as your personal, always available **E-Journal**. It's primarily meant to be used to keep track of your quests and log your thoughts and any note-worthy stuff you may stumble upon, across your RPG Video games or even to TableTop RPG adventures (*like DnD*), **without breaking immersion**! Of course, it's not absolutely limited to that so feel free to use it however works the best for you, even for your work/irl stuff.

As stated above, it consists of 3 distinct features (*and the **about** page which I won't spoil and I will let you see it on your own*) which are:
```
Journal
Quests
Stats/Home
```

### JOURNAL
In journal are kept your personal notes that you can write, edit and delete. It's meant to be a place to write out your thoughts about your in-game experiences, note crafting recipes or even a scrap paper to solve a puzzle. Given that it's akin to any notes app, you can absolutely use it as you see fit.

### Quests
This page allows you to log different quests in a task-like flow, that allows you to categorize them based on difficulty and their status (*completed or not*). In here, you'll keep track of the most generic fetch quest to the most complicated heist you may plan! Just remember, the harder the task, the more XP you'll earn...

### Stats/Home
This will be your home page, which also contains the stats of your account like how many quests you've completed, your current XP/Level and as well as the required level for the next level up. It also contains the functionality to change your password to your account.

## MORE IN DEPTH
If you take a quick glance at the source files of the project, you will see a few files, so let me guide you through them if you're curious. The stack it currently uses is **HTML/CSS** for the actual front end, **Python/Flask** for the dynamic render, logic behind the buttons and the communication with the db using **SQLITE(3)**.
### app.py
This is where the webpage actually lives. It handles ***all*** the routing of the app. It's written in Python and uses flask to handle the routing for both GETs and POSTs and getting and setting flask session data.
### helper.py
This is, as you can probably guess, a helper python file. It contains miscellaneous functions for getting and writing data to the database, managing passwords and other secondary functions. It's good practice and convenient to have them in an external file as to not cramp up the main app.py file. Otherwise it would be more akin to a living hell to stuff everything into a single file (*talking from experience*).
### app.db
This is the database of the app that contains everything from the stats and users, to the quests and journal entries of each user. If you're willing to see the actual schema of it, here it is:
```
CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL  username TEXT NOT NULL  hash TEXT NOT NULL);
CREATE TABLE sqlite_sequence(name seq);
CREATE TABLE journal (id INTEGER PRIMARY KEY AUTOINCREMENT  user_id INTEGER title TEXT  contents TEXT);
CREATE TABLE quests(id INTEGER PRIMARY KEY AUTOINCREMENT  user_id INTEGER  contents TEXT  completed INTEGER DEFAULT 0  difficulty integer default 0);
CREATE TABLE difficulty(id INTEGER PRIMARY KEY  name TEXT  xp_reward INTEGER DEFAULT 0  color text  img_name text);
CREATE TABLE stats(id INTEGER PRIMARY KEY AUTOINCREMENT  xp INTEGER DEFAULT 0  xp_till_levelup DEFAULT 20  tasks_completed INTEGER DEFAULT 0  user_id INTEGER  level INTEGER DEFAULT 1);
```
### templates
I make use of template html files, in order to minimize as much as possible redundancy, by having every html inherit the **base.html**, along with it's layout, stylesheet and references, and to speed up development for every module by focusing purely on the module's functionality.
### static
This folder contains all the static files, files that don't or won't change frequently like images, Cascading Style Sheets and other.
### __pycache__, flask_session
Miscellaneous files added from the modules i used.