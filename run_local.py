# -*- coding: utf-8 -*-
"""
Optional Python runner for the Flask Shift Management system.

What it does:
  * detects the Flask entry point (priority: app.py -> FLASK_APP -> other)
  * verifies Python/Flask and that the port is free
  * starts the Flask server locally on http://127.0.0.1:5000
  * opens the default browser automatically once the server is up
  * prints clear messages in Hebrew

Usage:   python run_local.py
(For a zero-setup experience on Windows, double-click run_local.bat instead —
 it creates a virtual environment and installs Flask first.)
"""
import os
import sys
import socket
import threading
import time
import webbrowser
import subprocess

# Make Hebrew print correctly on the Windows console
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HOST = "127.0.0.1"
PORT = 5000
URL = "http://%s:%d" % (HOST, PORT)
HERE = os.path.dirname(os.path.abspath(__file__))

# Candidate entry files, checked in order after app.py
OTHER_ENTRIES = ("main.py", "wsgi.py", "server.py", "run.py")


def say(line=""):
    print(line, flush=True)


def port_in_use(host, port):
    """True if something is already listening on host:port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def detect_entry():
    """Return (kind, target) following the required priority:
       1) app.py exists            -> ("file", "app.py")
       2) FLASK_APP env is set      -> ("flask", <value>)
       3) another known entry file  -> ("file", <name>)  (explained to the user)
       otherwise                    -> (None, None)
    """
    if os.path.exists(os.path.join(HERE, "app.py")):
        return ("file", "app.py")
    if os.environ.get("FLASK_APP"):
        return ("flask", os.environ["FLASK_APP"])
    for name in OTHER_ENTRIES:
        if os.path.exists(os.path.join(HERE, name)):
            return ("file", name)
    return (None, None)


def open_browser_when_ready():
    """Wait until the server accepts connections, then open the browser."""
    for _ in range(60):  # up to ~30 seconds
        if port_in_use(HOST, PORT):
            break
        time.sleep(0.5)
    webbrowser.open(URL)


def main():
    os.chdir(HERE)  # always operate from the project folder
    say("==================================================")
    say("   מערכת ניהול משמרות — הפעלה מקומית (Flask)")
    say("==================================================")

    # --- Flask must be importable ---
    try:
        import flask  # noqa: F401
    except ImportError:
        say("שגיאה: החבילה Flask אינה מותקנת.")
        say("  פתרון א': הריצו את run_local.bat (מתקין הכל אוטומטית).")
        say("  פתרון ב': pip install flask")
        sys.exit(1)

    # --- find the entry point ---
    kind, target = detect_entry()
    if kind is None:
        say("שגיאה: לא נמצא קובץ הפעלה (app.py) בתיקייה.")
        say("  התיקייה: %s" % HERE)
        say("  ודאו שהקובץ app.py קיים, או הגדירו משתנה סביבה FLASK_APP.")
        sys.exit(1)

    if kind == "flask":
        say("נמצא משתנה FLASK_APP=%s — מפעיל באמצעות 'flask run'." % target)
    elif target != "app.py":
        say("לא נמצא app.py, אך נמצא קובץ הפעלה אחר: %s — מפעיל אותו." % target)
    else:
        say("נמצא קובץ ההפעלה: app.py")

    # --- port must be free ---
    if port_in_use(HOST, PORT):
        say("שגיאה: הפורט %d כבר תפוס." % PORT)
        say("  ייתכן שהמערכת כבר רצה — נסו לפתוח: %s" % URL)
        say("  או סגרו את התהליך שתפס את הפורט ונסו שוב.")
        sys.exit(1)

    # --- open the browser in the background once the server is up ---
    threading.Thread(target=open_browser_when_ready, daemon=True).start()

    say("--------------------------------------------------")
    say("המערכת עולה... הדפדפן ייפתח אוטומטית בכתובת:")
    say("   %s" % URL)
    say("לעצירת המערכת: Ctrl+C")
    say("--------------------------------------------------")

    # --- start the server (blocks until stopped) ---
    if kind == "flask":
        env = dict(os.environ)
        env["FLASK_APP"] = target
        cmd = [sys.executable, "-m", "flask", "run",
               "--host", HOST, "--port", str(PORT)]
        rc = subprocess.call(cmd, env=env)
    else:
        rc = subprocess.call([sys.executable, target])
    return rc


if __name__ == "__main__":
    try:
        sys.exit(main() or 0)
    except KeyboardInterrupt:
        say("")
        say("המערכת נעצרה. להתראות!")
