Kappa Delta Rho Iota Beta Points System
=======================================
Here it is boys.

Setup
------
Run:
git clone --recursive https://github.com/jgeigerm/KDRPoints/

Then you need a few things.

If you don't want to use mysql then you can use sqlite... just comment out the mysql lines in config.py and uncomment the sqlite line

Install python-dev, libmysqlclient-dev, and mysql-server
```
sudo apt-get install libmysqlclient-dev python-dev mysql-server
```
Change the root password of your mysql installation :)

Run mysql_setup.sh (you can just keep the defaults, except for the password, which you should define)

Make a new file in the root of the project (where requirements.txt is) called app.vars with the following lines (1-4 are not needed with sqlite)

1. The database name
2. The database host
3. The database username
4. The database password
5. A random key: Can be whatever (md5 sum something and paste it in there)
6. The Google Consumer ID
7. The Google Consumer Secret

Next, start up a virtualenv with the command: virtualenv flask

Enter the virtualenv with the command: source flask/bin/activate

Then install requirements with pip:
```
pip install -r requirements.txt
```
Flask-MySQL will fail if you don't install python-dev and libmysqlclient-dev above, if you aren't using MySQL then take that line out of the requirements.txt file, otherwise the installation will fail

Google Auth
-----------
The consumer id and secret can be generated at https://console.developers.google.com/project

Create a new project, go to APIs and Auth, then Credentials. Create a new OAuth client ID.

Make sure the redirect URI is http://127.0.0.1:1072/login/authorized or auth will not work

Running the Server
------------------
Use the following command to start the server: python run.py

It should work now but you have to run a few queries to insert things before you can complete registration:

```
mysql -u root -p < db_base.dump
```
OR
```
sqlite3 app.db -init db_base.dump
```
It will error because of the use statement but it should work otherwise. 

Then restart the server

Log in with your kdrib Google account

Run the following to upgrade yourself to admin:

```
echo "use kdrpoints;update brother set role=2;" | mysql -u kdrpoints -p
```
OR
```
sqlite3 app.db 'update brother set role=2;'
```

Now you can access the admin panel as a superadmin
