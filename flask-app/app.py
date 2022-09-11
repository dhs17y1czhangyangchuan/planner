from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os, sqlite3
from werkzeug.utils import secure_filename

if not os.path.isfile("user.db"):
    db = sqlite3.connect("user.db")
    db.execute("CREATE TABLE Users " +
    "(Username TEXT NOT NULL, " +
    "Password TEXT NOT NULL, " +
    "Photo TEXT," +
    "PRIMARY KEY(Username))"
    )
    db.execute("INSERT INTO Users(Username, Password) VALUES(?, ?)", ("YangChuan", "123"))
    db.commit()

    db.execute("CREATE TABLE Tasks " +
    "(Username TEXT NOT NULL, " +
    "Date TEXT NOT NULL, " +
    "Task TEXT NOT NULL," +
    "Status TEXT)"
    )
    db.commit()
    db.close()

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        db = sqlite3.connect("user.db")
        cursor = db.execute("SELECT Username, Password FROM Users")
        
        found = False

        for user in cursor:
            if username == user[0]:
                found = True
                userinfo = user
                break
        db.close()

        if found == False:
            return redirect(url_for('error', msg="Wrong credentials"))
        else:
            if password == userinfo[1]:
                return redirect(url_for('profile', username=username))
            else:
                return redirect(url_for('error', msg="Wrong credentials"))

    return render_template("home.html")

@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    db = sqlite3.connect("user.db")
    if request.method == "POST" and request.files:
        if "upload" in request.files:
            file = request.files['upload']
            filename = secure_filename(file.filename)
            path = os.path.join("photos", filename)
            file.save(path)

            db.execute("UPDATE Users SET Photo = ? WHERE Username = ?", (filename, username))
            db.commit()

        elif "change" in request.files:
            file = request.files['change']
            filename = secure_filename(file.filename)
            path = os.path.join("photos", filename)
            file.save(path)

            db.execute("UPDATE Users SET Photo = ? WHERE Username = ?", (filename, username))
            db.commit()
    
    cursor = db.execute("SELECT Photo FROM Users WHERE Username = ?", (username, ))
    row = cursor.fetchone()
    filename = row[0]

    if filename == None:
        db.close()
        return render_template("profile-nopic.html", username=username)
    else:
        db.close()
        return render_template("profile.html", username=username, filename=filename)
    
@app.route("/photo/<filename>")
def get_directory(filename):
    return send_from_directory("photos", filename)

@app.route("/planner/<username>", methods=["GET", "POST"])
def planner(username):
    db = sqlite3.connect("user.db")
    if request.method == "POST":
        if "add" in request.form:
            date = request.form['date']
            task = request.form['task']

            db.execute("INSERT INTO Tasks(Username, Date, Task) VALUES(?, ?, ?)", (username, date, task))
            db.commit()
        elif "complete" in request.form:
            username = request.form["username"]
            date = request.form["date"]
            task = request.form["task"]

            db.execute("UPDATE Tasks SET Status = ? WHERE Username = ? AND Date = ? AND Task = ?", ("completed", username, date, task))
            db.commit()
        
        else:
            username = request.form["username"]
            date = request.form["date"]
            task = request.form["task"]

            db.execute("DELETE FROM Tasks WHERE Username = ? AND Date = ? AND Task = ?", (username, date, task))
            db.commit()

    cursor = db.execute("SELECT Date, Task, Status FROM Tasks WHERE Username = ?", (username, ))
    tasks=[]
    for row in cursor:
        tasks.append(row)
    db.close()

    return render_template("planner.html", tasks=tasks, username=username)

@app.route("/error/<msg>")
def error(msg):
    return render_template("error.html", msg=msg)

if __name__ == "__main__":
    app.run()