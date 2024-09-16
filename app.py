from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helper import login_required, login_error, get_db, get_journal_entries, get_journal_entry, get_active_quests, get_completed_quests, get_difficulties, get_stats, initialize_user, update_quest_stats, debug_print, get_password_hash, set_password_hash

import sqlite3

app = Flask(__name__)

# Global
DB = get_db()
# /Global

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Index route
@app.route('/')
@login_required
def index():
    # return render_template("base.html", username=session.get("username"))
    # return render_template("home.html", username=session.get("username"))
    return redirect("/home")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        # Server-Side validate the inputs
        if not request.form.get("username"):
            return login_error("Error: No username provided.")
        if not request.form.get("password"):
            return login_error("Error: No password provided.")
        
        username, password = request.form.get("username"), request.form.get("password")

        # Connect to db and get user based on username
        con = sqlite3.connect(DB)
        cur = con.cursor()
        res = cur.execute("SELECT id,hash,username FROM users WHERE username  = ?", (username,))
        
        # Check for a result and validate passwords
        row = res.fetchone()
        con.close()
        if not row or not check_password_hash(row[1], password):
            return login_error("Error: Invalid credentials.")
        
        # Assiugn the users.id to session
        session["user_id"] = int(row[0])
        session["username"] = row[2]

        # Redirect to home page
        return redirect("/")
    else:
        return render_template("login.html")
    

# Insert the new user to users
@app.route("/register", methods=["GET","POST"])
def register():
    session.clear()
    
    if request.method == "POST":
        # Server side validate input
        if not request.form.get("username"):
            return login_error("Error: No username provided.", True)
        if not request.form.get("password") or not request.form.get("password_confirm"):
            return login_error("Error: No password provided.", True)
        
        username, password, password_confirm = request.form.get("username"), request.form.get("password"), request.form.get("password_confirm")

        if password != password_confirm:
            return login_error("Error: Passwords do not match.", True)

        # check if user already exists
        con = sqlite3.connect(DB)
        cur = con.cursor()
        res = cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = res.fetchone()
        if row:
            return login_error("Username already exists.", True)

        # Add to users db
        try:
            con = sqlite3.connect(DB)
            cur = con.cursor()
            cur.execute("INSERT INTO users (username, hash) VALUES (?,?)", (username, generate_password_hash(password)))
            new_id = cur.lastrowid
            con.commit()
            con.close()

            # Initialize new user's stats
            initialize_user(new_id)

            session["user_id"] = new_id
            session["username"] = username

            return redirect("/")
        except Exception as e:
            return login_error(f"Error: {e}", True)

    else:
        return render_template("register.html")
    

@login_required
@app.route("/journal")
def journal():
    entries = get_journal_entries(session.get("user_id"))
    
    return render_template("journal.html", journal=True, entries=entries, username=session.get("username"))


@login_required
@app.route("/journalAdd", methods=["GET","POST"])
def journalAdd():
    if request.method == "POST":
        # Check if title is filled in
        if request.form.get("action") == "back":
            return redirect("/journal")
        
        if not request.form.get("title"):
            return render_template("journalAdd.html", error_msg="Title can't be empty.")
        
        # Insert into journal in db
        try:
            con = sqlite3.connect(DB)
            cur = con.cursor()
            cur.execute("INSERT INTO journal(user_id,title, contents) VALUES (?,?,?)",(int(session.get("user_id")),request.form.get("title"),request.form.get("contents")))
            con.commit()
            con.close()

            # return render_template("/journal.html", journal=True)
            return redirect("/journal")
        except Exception as e:
            return render_template("journalAdd.html", error_msg=f"Error: {e}")

    else:
        return render_template("journalAdd.html", journal=True, username=session.get("username"))
    

@login_required
@app.route("/journal/<int:journal_id>", methods=["GET","POST"])
def journalView(journal_id):
    if request.method == "POST":
        if request.form.get("action") == "edit":
            # Edit the note
            try:
                con = sqlite3.connect(DB)
                cur = con.cursor()
                cur.execute("UPDATE journal SET title = ?, contents = ? WHERE id = ? AND user_id = ?", (request.form.get("title"), request.form.get("contents"), journal_id, session.get("user_id")))
                con.commit()
                con.close()
            except:
                pass
        elif request.form.get("action") == "delete":
            # Delete the note
            try:
                con = sqlite3.connect(DB)
                cur = con.cursor()
                cur.execute("DELETE FROM journal WHERE id = ? AND user_id = ?", (journal_id, session.get("user_id")))
                con.commit()
                con.close()
            except:
                pass
        elif request.form.get("action") == "back":
            return redirect("/journal")    

        return redirect("/journal")
    else:
        # View the note
        entry = get_journal_entry(session.get("user_id"), journal_id)
        if entry is None:
            return redirect("/journal")

        return render_template("journalView.html", journal=True,id=journal_id,entry=entry, username=session.get("username"))
    

@login_required
@app.route("/quests", methods=["GET", "POST"])
def quests():
    if request.method == "POST":
        # Create new quest
        if not request.form.get("quest"):
            return render_template("quests.html", quests=True)

        quest = request.form.get("quest")
        difficulty = request.form.get("difficulty")

        try:
            con = sqlite3.connect(DB)
            cur = con.cursor()
            cur.execute("INSERT INTO quests(user_id,contents,difficulty) VALUES(?,?,?)",(session.get("user_id"),quest,difficulty))
            con.commit()
            con.close()
        except Exception as e:
            return render_template("quests.html", quests=True, error_msg=f"Error: {e}")

        return redirect("/quests")
    else:
        # Show all quests
        activeQuests = get_active_quests(session.get("user_id"))
        completedQuests = get_completed_quests(session.get("user_id"))
        difficulties = get_difficulties()

        return render_template("quests.html", quests=True, active_quests=activeQuests, completed_quests=completedQuests, username=session.get("username"), difficulties=difficulties)
    

@login_required
@app.route("/complete/<int:quest_id>", methods=["POST"])
def complete_quest(quest_id):
    try:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("UPDATE quests SET completed = 1 WHERE id = ?", (quest_id,))
        con.commit()
        con.close()
        
        update_quest_stats(quest_id)

    except Exception as e:
        pass

    return redirect("/quests")

@login_required
@app.route("/clear-quests", methods=["POST"])
def clear_completed_quests():
    try:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("DELETE FROM quests WHERE user_id = ? AND completed = 1", (session.get("user_id"),))
        con.commit()
        con.close()
    except:
        pass

    return redirect("/quests")


@login_required
@app.route("/about")
def about():
    return render_template("about.html", about=True)


@login_required
@app.route("/home")
def home():
    stats = get_stats(session.get("user_id"))

    return render_template("home.html", username=session.get("username"), stats=stats)


@login_required
@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        if not request.form.get("old_password") or not request.form.get("new_password"):
            return render_template("newPassword.html", error_msg="Please Fill In The Fields.")
        
        if not check_password_hash(get_password_hash(session.get("user_id")),request.form.get("old_password")):
            return render_template("newPassword.html", error_msg="Incorrect Credentials.")
        
        set_password_hash(session.get("user_id"), generate_password_hash(request.form.get("new_password")))
        
        return redirect("/login")
        
    else:
        return render_template("newPassword.html")