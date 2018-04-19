# passport
a command-line password manager written in Python

## Usage

**Write a new empty database file:**

TODO Update this to reflect new features

```passport <database_name> create```

You will be prompted to set a password for the database. Be sure to use a strong password, and don't forget it. Your data cannot be recovered without the password.

**Add a new account entry:**

```passport <database_name> edit <account_name>```

This will launch ```vi```. Enter all the information you want to keep under that account (passwords, 2FA backup codes, last update times, etc.) and save.

**Display an existing account entry:**

```passport <database_name> display <account_name>```

This will launch ```less``` and display the information under that account. Press ```q``` to quit.

**List the names of all of the entries on the account:**

```passport <database_name> list```

Note that for security reasons this will only write *account names* to ```stdout```, not any secret data pertaining to them.

**Remove an account from the database:**

```passport <database_name> remove <account_name>```

For more information, run ```passport -h```.

## Installation

Full installation instructions TODO

**Dependencies**

- pycrypto
- GNU screen

Note that I've only tested ```passport``` under Python 3.5.2 on Ubuntu 16.04.4. YMMV

## Contributing

Sure, knock yourself out.
