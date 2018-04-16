#!/usr/bin/env python

import os
import sys
import json
import base64
import getpass
import argparse
import subprocess
from pprint import pprint
from Crypto.Hash import SHA256
from Crypto.Cipher import AES

def get_password(prompt, second_prompt=False):
    """TODO I can't figure out how to write an automated test for this function.
    If you can, please add one. Until then, you can test this function manually
    by running the following:

    echo "import passport; print(passport.get_password('prompt '))" | python
    echo "import passport; print(passport.get_password('first ',
        second_prompt='second '))" | python

    The first line will take in a single password and print it.
    The second line will take in two passwords and print them if they match.
    Otherwise, it will tell you they don't match and prompt you again."""
    if second_prompt:
        first_attempt, second_attempt = "0", "1"
        while first_attempt != second_attempt:
            if first_attempt != "0" or second_attempt != "1":
                print("Passwords do not match")
            first_attempt = getpass.getpass(prompt)
            second_attempt = getpass.getpass(second_prompt)
        password = first_attempt
    else:
        password = getpass.getpass(prompt)
    return password

def get_key(passphrase):
    h = SHA256.new()
    h.update(passphrase.encode())
    return h.hexdigest()[:16]

def encrypt_and_write(password_database, filename, database_password=False):
    # get passphrase from user if one isn't provided
    if not database_password:
        database_password = get_password(
                "Enter new database password: ",
                second_prompt="Enter it again: ")
    # TODO prompt user to choose between using the same password or a new one
    password_database = json.dumps(password_database)
    # encrypt the database and write it to disk
    key = get_key(database_password)
    cipher = AES.new(key, AES.MODE_CFB, key)
    password_database = cipher.encrypt(password_database.encode())
    outfile = open(filename, "wb")
    outfile.write(password_database)
    outfile.close()

def read_and_decrypt(filename):
    # get the passphrase from the user
    # TODO implement bad passphrase checking
    password_database = " "
    password = get_password("Enter database password: ")
    # read and decrypt the password database
    password_database = open(filename, "rb").read()
    key = get_key(password)
    cipher = AES.new(key, AES.MODE_CFB, key)
    password_database = cipher.decrypt(password_database)
    password_database = password_database.decode().strip('"')
    password_database = json.loads(password_database)
    # need to turn the passphrase so we can use it later
    return password_database, passphrase

def create(database_name):
    blank_database = json.dumps({})
    encrypt_and_write(blank_database, database_name)
    print("New database created")

def list_accounts(password_database, database_name):
    # notify the user if the database is empty
    if password_database == {}:
        print("'"+database_name+"' is empty.")
    # otherwise display all keys in the database in alphabetical order
    else:
        print('\n'.join(sorted(password_database.keys())))

def edit(password_database, database_name, account_name, database_password):
    # allow the user to update the entry
    if account_name in password_database.keys():
        existing_entry = password_database[account_name]
    else:
        existing_entry = ""
    # TODO generate random name for the temp file
    os.system("echo '"+existing_entry+"' > /tmp/blergh")
    os.system("vi /tmp/blergh")
    password_database[account_name] = open("/tmp/blergh","r").read()
    os.system("rm /tmp/blergh")
    # encrypt the database and write it to disk
    encrypt_and_write(password_database, database_name, database_password=database_password)
    print("Updated information for '"+account_name+"'")

def display(password_database, database_name, account_name):
    # confirm that the account exists in the database
    if account_name not in password_database.keys():
        print("'"+account_name+"' does not exist in '"+database_name+"'")
    # if it does, then display the password for the particular account specified
    else:
        # TODO add a display timeout?
        # TODO implement a better display method (using ncurses?)
        os.system("echo '"+password_database[account_name]+"' | less")

def remove(password_database, database_name, account_name, database_password):
    # check to make sure the account exists in the database
    if account_name not in password_database.keys():
        print("'"+account_name+"' does not exist in '"+database_name+"'")
    # otherwise, proceed with confirmation of deletion
    else:
        # confirm that the user really wants to delete the account
        response = ""
        while response not in ["y","Y","n","N"]:
            response = input("Are you sure you want to delete '"+account_name+"'? (y/n) ")
        if response in ["y","Y"]:
            # delete the account
            del password_database[account_name]
            # encrypt and write new password database to disk
            encrypt_and_write(password_database, database_name, database_password=database_password)
            print("Removed account '"+account_name+"'")
        else:
            print("Aborted")

if __name__ == "__main__":
    # make top-level parser
    parser = argparse.ArgumentParser(description="display and manage passwords")
    parser.add_argument("database", type=str, help="the database to work on")
    subparsers = parser.add_subparsers(dest="choice")
    # 'create' subcommand
    create_parser = subparsers.add_parser("create", help="make a new blank database")
    # 'list' subcommand
    list_parser = subparsers.add_parser("list", help="show a list of all entries in the database")
    # 'add' subcommand
    edit_parser = subparsers.add_parser("edit", help="make a new entry in the selected database")
    edit_parser.add_argument("account", type=str, help="friendly unique identifier for the new entry")
    # TODO 'search' subcommand
    # 'display' subcommand
    display_parser = subparsers.add_parser("display", help="display the password associated with a particular account")
    display_parser.add_argument("account", type=str, help="the account to display the password for")
    # 'modify' subcommand
    modify_parser = subparsers.add_parser("modify", help="change the password for an account")
    modify_parser.add_argument("account", help="the account to change the password for")
    # TODO 'change-master-password' subcommand
    # 'remove' subcommand
    remove_parser = subparsers.add_parser("remove", help="delete an account from the database")
    remove_parser.add_argument("account", type=str, help="name of the account to remove")
    # parse all arguments and save namespace object
    args = parser.parse_args()

    # if we're not creating a new database
    if args.choice != "create":
        # read and decrypt the existing database
        password_database, database_password = read_and_decrypt(args.database)

    # if the user doesn't choose a subcommand, then display help and exit
    if args.choice == None:
        parser.print_help(sys.stderr)
        sys.exit(1)
    # otherwise, execute the appropriate subcommand
    elif args.choice == "create":
        create(args.database)
    elif args.choice == "list":
        list_accounts(password_database, args.database)
    elif args.choice == "edit":
        edit(password_database, args.database, args.account, database_password)
    elif args.choice == "search":
        print("Searching is not yet implemented.")
    elif args.choice == "display":
        display(password_database, args.database, args.account)
    elif args.choice == "remove":
        remove(password_database, args.database, args.account, database_password)
