from flask import redirect, render_template, request, session
from functools import wraps
import sqlite3

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def login_error(msg, isRegister = False):
    """ 
    If an error occurs during the login validation then this function redirects the user
    to the login or register screen and it will display the error msg that is provided.
    """
    if isRegister:
        return render_template("register.html", error_msg=msg)
    
    return render_template("login.html", error_msg=msg)

def get_db():
    return "app.db"


def get_journal_entries(user_id):
    """
    Get all the journal entries of a specific user.
    """
    try:
        con = sqlite3.connect(get_db())
        cur = con.cursor()
        res = cur.execute("SELECT title,contents,id FROM journal WHERE user_id = ?", (user_id,))
        entries = res.fetchall()
        con.close()
    except:
        return None
    
    return sorted(entries,key = lambda x: x[2], reverse=True)

def get_journal_entry(user_id, journal_id):
    """
    Get a specific journal entry.
    """
    try:
        con = sqlite3.connect(get_db())
        cur = con.cursor()
        res = cur.execute("SELECT title,contents,id FROM journal WHERE user_id = ? AND id = ?", (user_id,journal_id))
        entry = res.fetchone()
        con.close()
    except:
        return None
    
    return entry


def get_active_quests(user_id):
    return get_quests_inner(user_id, 0)

def get_completed_quests(user_id):
    return get_quests_inner(user_id, 1)

def get_quests_inner(user_id, completed):
    try:
        con = sqlite3.connect(get_db())
        cur = con.cursor()
        # res = cur.execute("SELECT contents,id,(SELECT img_name FROM difficulty WHERE id = difficulty) AS img FROM quests WHERE user_id = ? and completed = ? ", (user_id,completed))
        res = cur.execute("SELECT contents,id,(SELECT img_name FROM difficulty WHERE id = difficulty) AS img FROM quests WHERE user_id = ? and completed = ? ORDER BY difficulty", (user_id,completed))
        entries = res.fetchall()
        con.close()
    except:
        return None
    
    # return sorted(entries, key= lambda x: x[1], reverse= True)
    return entries

def get_difficulties():
    try:
        con = sqlite3.connect(get_db())
        cur = con.cursor()
        res = cur.execute("SELECT id, name, color FROM difficulty")
        entries = res.fetchall()
        con.close()
    except:
        return None
    
    return sorted(entries, key=lambda x:x[0])

def get_stats(user_id):
    try:
        con = sqlite3.connect(get_db())
        cur = con.cursor()
        res = cur.execute("SELECT xp, xp_till_levelup, tasks_completed, level FROM stats WHERE user_id = ?", (user_id,))
        entry = res.fetchone()
        con.close()
    except:
        return None
    
    return entry

def initialize_user(user_id):
    try:
        con = sqlite3.connect(get_db())
        cur = con.cursor()
        cur.execute("INSERT INTO stats(user_id) VALUES(?)", (user_id,))
        con.commit()
        con.close()

        return 0
    except:
        return 1
    

def add_xp(user_id, amount):
    stats = get_stats(user_id)
    con = sqlite3.connect(get_db())
    cur = con.cursor()
    cur.execute("UPDATE stats SET xp = xp + ? where user_id = ?", (amount, user_id))
    con.commit()

    if stats[0] + amount >= stats[1]:
        # Level up
        cur.execute("UPDATE stats SET level = level + 1, xp_till_levelup = xp_till_levelup + 20 WHERE user_id = ?", (user_id,))
        con.commit()

    con.close()
    
def update_quest_stats(quest_id):
    con = sqlite3.connect(get_db())
    cur = con.cursor()
    res = cur.execute("SELECT xp_reward, stats.user_id FROM quests JOIN difficulty ON difficulty.id = quests.difficulty AND difficulty.id > 0 JOIN stats ON quests.user_id = stats.user_id WHERE quests.id = ?", (quest_id,))
    entry = res.fetchone()

    if entry:
        add_xp(entry[1], entry[0])

        # Track the completed quest
        cur.execute("UPDATE stats SET tasks_completed = tasks_completed + 1 WHERE user_id = ?", (entry[1],))
        con.commit()

    con.close()

def get_password_hash(user_id):
    con = sqlite3.connect(get_db())
    cur = con.cursor()
    res = cur.execute("SELECT hash FROM users WHERE id = ?", (user_id,))
    entry = res.fetchone()
    con.close()

    return entry[0]

def set_password_hash(user_id, hash):
    con = sqlite3.connect(get_db())
    cur = con.cursor()
    cur.execute("UPDATE users SET hash = ? WHERE id = ?",(hash,user_id))
    con.commit()
    con.close()


def debug_print(msg):
    print("#"*10)
    print(msg)
    print("#"*10)