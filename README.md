Kappa Delta Rho Iota Beta Points System
=======================================
Here it is boys.

Setup
------
Run:
git clone --recursive https://github.com/jgeigerm/KDRPoints/

Then you need a few things.

Make a new file in the root of the project (where requirements.txt is) called app.vars

- The first line should be a random key: Can be whatever (md5 sum something and paste it in there)

- The second line should be the Google Consumer ID

- The third line should be the Google Consumer Secret

Next, start up a virtualenv with the command: virtualenv flask

Enter the virtualenv with the command: source flask/bin/activate

Then install requirements with pip: pip install -r requirements.txt

Google Auth
-----------
The consumer id and secret can be generated at https://console.developers.google.com/project

Create a new project, go to APIs and Auth, then Credentials. Create a new OAuth client ID.

Make sure the redirect URI is http://127.0.0.1:1072/login/authorized or auth will not work

Running the Server
------------------
Use the following command to start the server: python run.py

It should work now but you have to run a few queries to insert things before you can complete registration:

sqlite3 app.db -init db_base.dump

Then restart the server

Log in with your kdrib Google account

Run the following to upgrade yourself to admin:

sqlite3 app.db -cmd 'update brother set role=2;'

Then .exit to exit sqlite3

Now you can access the admin panel as a superadmin
