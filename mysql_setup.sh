#!/bin/bash
dbpass2="."
echo -n "Enter database host [localhost]: "
read dbhost
if [ -z "$dbhost" ]
then
    dbhost="localhost"
fi

echo -n "New database name [kdrpoints]: "
read dbname
if [ -z "$dbname" ]
then
    dbname="kdrpoints"
fi

echo -n "New user name for database [kdrpoints]: "
read dbuser
if [ -z "$dbuser" ]
then
    dbuser="kdrpoints"
fi

while [ "$dbpass" != "$dbpass2" ]
do
    echo -n "New user password for database: "
    read -s dbpass
    echo
    echo -n "Confirm password: "
    read -s dbpass2
    echo
    if [ "$dbpass" != "$dbpass2" ]
    then
        echo Passwords do not match
    fi
done
echo

echo "Logging you in as root at $dbhost..."
echo "create database $dbname;
create user '$dbuser'@'$dbhost' identified by '$dbpass';
grant all privileges on $dbname.* to '$dbuser'@'$dbhost';
flush privileges;" | mysql -u root -p -h $dbhost
if [ $? == 0 ]
then
    echo Done.
else
    echo It looks like something went wrong with mysql.
fi
