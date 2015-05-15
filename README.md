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

Then install requirements with pip: pip install -r requirements.txt

Google Auth
-----------
The consumer id and secret can be generated at https://console.developers.google.com/project

Create a new project, go to APIs and Auth, then Credentials. Create a new OAuth client ID.

Make sure the redirect URI is http://127.0.0.1:1072/login/authorized or auth will not work

Running the Server
------------------
Use the following command to start the server: python run.py

It should work now.
