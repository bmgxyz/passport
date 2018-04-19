#!/usr/bin/env python

import os
import sys
import json
import getpass
import argparse
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

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

def get_key(password):
    h = SHA256.new()
    h.update(password.encode())
    return h.hexdigest()[:16]

def encrypt_and_write(password_database, filename, database_password=False):
    # get password from user if one isn't provided
    if not database_password:
        database_password = get_password(
                "Enter new database password: ",
                second_prompt="Enter it again: ")
    password_database = json.dumps(password_database)
    # encrypt the database and write it to disk
    key = get_key(database_password)
    cipher = AES.new(key, AES.MODE_CFB, key)
    password_database = cipher.encrypt(password_database.encode())
    outfile = open(filename, "wb")
    outfile.write(password_database)
    outfile.close()

def read_and_decrypt(filename, database_password=False):
    # get the password from the user
    password_database = " "
    if not database_password:
        database_password = get_password("Enter database password: ")
    # read and decrypt the password database
    password_database_file = open(filename, "rb")
    key = get_key(database_password)
    cipher = AES.new(key, AES.MODE_CFB, key)
    password_database = cipher.decrypt(password_database_file.read())
    password_database_file.close()
    # if the first character is '{', then the key is probably good, so proceed
    if password_database[0] == 34 or password_database[0] == 123:
        password_database = password_database.decode()
        password_database = password_database.strip('"')
        password_database = json.loads(password_database)
        # need to turn the password so we can use it later
        return password_database, database_password
    else:
        # the key is wrong, so raise an error
        raise Exception("BadKeyError")

if __name__ == "__main__":
    # make top-level parser
    parser = argparse.ArgumentParser(description="display and manage passwords")
    parser.add_argument("database", type=str, help="the database to work on")
    subparsers = parser.add_subparsers(dest="choice")
    # 'create' subcommand
    create_parser = subparsers.add_parser("create",
            help="make a new blank database")
    # 'list' subcommand
    list_parser = subparsers.add_parser("list",
            help="show a list of all entries in the database")
    # 'edit' subcommand
    # TODO add --generate-password=n flag (where n is the number of words)
    edit_parser = subparsers.add_parser("edit",
            help="make a new entry in the selected database")
    edit_parser.add_argument("account",
            type=str,
            help="friendly unique identifier for the new entry")
    # TODO 'search' subcommand
    # 'display' subcommand
    display_parser = subparsers.add_parser("display",
            help="display the password associated with a particular account")
    display_parser.add_argument("account",
            type=str,
            help="the account to display the password for")
    # 'changepw' subcommand
    changepw_parser = subparsers.add_parser("changepw",
            help="change the master password for a database")
    # 'remove' subcommand
    remove_parser = subparsers.add_parser("remove",
            help="delete an account from the database")
    remove_parser.add_argument("account",
            type=str,
            help="name of the account to remove")
    # parse all arguments and save namespace object
    args = parser.parse_args()

    # if the user doesn't choose a subcommand, then display help and exit
    if args.choice == None:
        parser.print_help(sys.stderr)
        sys.exit(1)
    # otherwise, execute the appropriate subcommand
    elif args.choice == "create":
        blank_database = json.dumps({})
        encrypt_and_write(blank_database, args.database)
    elif args.choice == "list":
        password_database, database_password = read_and_decrypt(args.database)
        if password_database == {}:
            print("'"+args.database+"' is empty.")
        else:
            print('\n'.join(sorted(password_database.keys())))
    elif args.choice == "edit":
        # read and decrypt password database from disk
        password_database, database_password = read_and_decrypt(args.database)
        # allow the user to update the entry
        account_name = args.account
        database_name = args.database
        if account_name in password_database.keys():
            existing_entry = password_database[account_name]
        else:
            existing_entry = ""
        # get entry data from user
        # TODO generate random name for the temp file
        os.system("echo '"+existing_entry+"' > /tmp/blergh")
        os.system("vi /tmp/blergh")
        password_database[account_name] = open("/tmp/blergh","r").read()
        os.system("rm /tmp/blergh")
        # encrypt the database and write it to disk
        encrypt_and_write(password_database, database_name, database_password=database_password)
        output = "Updated information for '"+account_name+"'"
    elif args.choice == "search":
        print("Searching is not yet implemented.")
    elif args.choice == "display":
        password_database, database_password = read_and_decrypt(args.database)
        # confirm that the account exists in the database
        account_name = args.account
        database_name = args.database
        if account_name not in password_database.keys():
            print("'"+account_name+"' does not exist in '"+database_name+"'")
        # if it does, then display the password for the particular account specified
        else:
            # TODO add a display timeout?
            # TODO implement a better display method (using ncurses?)
            os.system("echo '"+password_database[account_name]+"' | less")
    elif args.choice == "remove":
        account_name = args.account
        database_name = args.database
        # decrypt password database
        password_database, database_password = read_and_decrypt(database_name)
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
    elif args.choice == "changepw":
        # decrypt password database
        password_database, database_password = read_and_decrypt(args.database)
        # encrypt the database with a new password and write it to disk
        encrypt_and_write(password_database, args.database)
        print("Database password updated successfully")