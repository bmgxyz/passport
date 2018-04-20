# passport
a command-line password manager written in Python

## Usage

**Write a new empty database file:**

```passport <database_name> create```

You will be prompted to set a password for the database. Be sure to use a strong
password, and don't forget it. Your data cannot be recovered without the
password.

**Add a new account entry:**

```passport <database_name> edit <account_name>```

Launches ```vi``` in a ```screen``` session. Enter all the information you want
to keep under that account (passwords, 2FA backup codes, last update times,
etc.) and save. Note that the screen session will lock after 30 seconds of
inactivity, and you'll have to enter your user account password to get back in.

**Display an existing account entry:**

```passport <database_name> display <account_name>```

This will launch ```less``` and display the information under that account.
Press ```q``` to quit.

**List the names of all of the entries on the account:**

```passport <database_name> list```

Note that for security reasons this will only write *account names* to
```stdout```, not any secret data pertaining to them.

**Remove an account from the database:**

```passport <database_name> remove <account_name>```

**Search the database:**

```passport <database_name> search <query>```

Returns a list of accounts in the database whose entries or titles match
```<query>```. Note that ```<query>``` can either be plaintext or a regex.

For more information, run ```passport -h```.

## Installation

Full installation instructions TODO

I have no idea how to package Python code for distribution, so you're mostly on
your own. On my system, I just linked the source code to
```<python environment>/lib/passport``` and ```passport.py``` to
```/usr/local/bin/passport``` or ```<python environment>/bin/passport``` to let
```bash``` pick it up.

**Dependencies**

- pycrypto
- GNU screen

Note that I've only tested ```passport``` under Python 3.5.2 on Ubuntu 16.04.4.
Also, there are currently
[zarro boogs](https://en.wikipedia.org/wiki/Bugzilla#Zarro_Boogs). YMMV

## Contributing

Sure, knock yourself out. If you know anything about packaging, feel free to
teach me your ways.
