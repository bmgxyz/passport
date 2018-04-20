#!/usr/bin/env python3

import os
import re
import sys
import json
import random
import getpass
import logging
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
    # set up logging
    with open(sys.path[-1]+'/passport/logs/latest.log', 'w'):
        pass
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
            filename=sys.path[-1]+"/passport/logs/latest.log",
            level=logging.INFO)
    logging.info("Passport started")

    # make top-level parser
    logging.info("Parsing command line arguments...")
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
    edit_parser = subparsers.add_parser("edit",
            help="make a new entry in the selected database")
    edit_parser.add_argument("account",
            type=str,
            help="friendly unique identifier for the new entry")
    edit_parser.add_argument("--generate", "-g",
            type=int,
            required=False,
            help="number of words to make a random password out of")
    # 'search' subcommand
    search_parser = subparsers.add_parser("search",
            help="find all entries that match a regex query")
    search_parser.add_argument("query",
            help="the regex or plaintext to search on")
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
    logging.info("Arguments parsed successfully")

    # if the user doesn't choose a subcommand, then display help and exit
    if args.choice == None:
        logging.info("No subcommand chosen, exiting")
        parser.print_help(sys.stderr)
        sys.exit(1)
    # otherwise, execute the appropriate subcommand
    elif args.choice == "create":
        logging.info("User selected 'create' subcommand")
        logging.info("Creating blank database with name '"+args.database+"'")
        blank_database = json.dumps({})
        encrypt_and_write(blank_database, args.database)
        logging.info("Blank database written successfully")
    elif args.choice == "list":
        logging.info("User selected 'list' subcommand")
        logging.info("Reading and decrypting password database '"+
                args.database+"'...")
        password_database, database_password = read_and_decrypt(args.database)
        logging.info("Read and decrypted '"+args.database+"' successfully")
        logging.info("Printing database entry titles...")
        if password_database == {}:
            print("'"+args.database+"' is empty.")
        else:
            print('\n'.join(sorted(password_database.keys())))
        logging.info("Done printing, exiting")
    elif args.choice == "edit":
        # read and decrypt password database from disk
        logging.info("User selected 'edit' subcommand")
        logging.info("Reading and decrypting password database '"+
                args.database+"'...")
        password_database, database_password = read_and_decrypt(args.database)
        logging.info("Read and decrypted '"+args.database+"' successfully")
        # allow the user to update the entry
        logging.info("Reading existing entry for title '"+args.account+"'...")
        account_name = args.account
        database_name = args.database
        if account_name in password_database.keys():
            existing_entry = password_database[account_name]
        else:
            existing_entry = ""
        logging.info("Existing entry read in successfully")
        # generate a random password if the user requested one
        if args.generate != None:
            logging.info("User requested a random "+str(args.generate)+
                    "-word passphrase. Generating...")
            wordlist_file = open("./src/wordlist.txt","r")
            wordlist = []
            for line in wordlist_file:
                wordlist.append(line.split("\t")[1].rstrip("\n"))
            new_password = ""
            for i in range(args.generate):
                new_password += random.choice(wordlist)
            # if the entry is not empty, make space for the new password
            if existing_entry != "":
                existing_entry += "\n\n"
            # append the new password to the entry for editing
            existing_entry += new_password
            logging.info("Passphrase generated successfully")
        # get entry data from user
        logging.info("Preparing file at /tmp/passport.tmp for editing...")
        os.system("touch /tmp/passport.tmp")
        os.system("chmod 600 /tmp/passport.tmp")
        os.system("echo '"+existing_entry+"' > /tmp/passport.tmp")
        logging.info("File prepared, launching vim...")
        # launch vi to edit the entry
        # but lock the screen session after 30 seconds
        os.system("screen -c "+
                sys.path[-1]+"/passport/screenrc vi /tmp/passport.tmp")
        password_database[account_name] = open(
                "/tmp/passport.tmp","r").read().strip("\n")
        os.system("rm /tmp/passport.tmp")
        logging.info("Editing complete, temporary file removed")
        # encrypt the database and write it to disk
        logging.info("Encrypting database and writing to file...")
        encrypt_and_write(password_database,
                database_name,
                database_password=database_password)
        output = "Updated information for '"+account_name+"'"
        logging.info("Wrote encrypted database successfully, exiting")
    elif args.choice == "search":
        # read and decrypt password database
        logging.info("User selected 'search' subcommand")
        logging.info("Reading and decrypting password database '"+
                args.database+"'...")
        password_database, database_password = read_and_decrypt(args.database)
        logging.info("Read and decrypted '"+args.database+"' successfully")
        # compile the regex
        logging.info("Searching database...")
        regex = re.compile(args.query)
        # loop over the database and find all matching entries and titles
        matches = []
        for key in password_database.keys():
            entry = password_database[key]
            if regex.search(key) or regex.search(entry):
                matches.append(key)
        logging.info("Search complete, reporting results")
        if matches == []:
            print("No matches in '"+
                    args.database+"' for query '"+args.query+"'")
        else:
            print('\n'.join(matches))
        logging.info("Results printed, exiting")
    elif args.choice == "display":
        logging.info("User selected 'display' subcommand")
        logging.info("Reading and decrypting password database '"+
                args.database+"'...")
        password_database, database_password = read_and_decrypt(args.database)
        logging.info("Read and decrypted '"+args.database+"' successfully")
        # confirm that the account exists in the database
        logging.info("Accessing and displaying entry under '"+
                args.account+"'...")
        account_name = args.account
        database_name = args.database
        if account_name not in password_database.keys():
            print("'"+account_name+"' does not exist in '"+database_name+"'")
        # if it does, then display the password for the account specified
        else:
            # write entry to disk so it can be read by less later on
            os.system("echo '' > /tmp/passport.tmp")
            os.system("chmod 600 /tmp/passport.tmp")
            os.system("echo '"+
                    password_database[account_name]+"' > /tmp/passport.tmp")
            # launch less to display the entry
            # but lock the screen session after 30 seconds
            os.system("screen -c "+
                    sys.path[-1]+"/passport/screenrc less /tmp/passport.tmp")
        logging.info("Display closed by user, exiting")
    elif args.choice == "remove":
        account_name = args.account
        database_name = args.database
        # decrypt password database
        logging.info("User selected 'remove' subcommand")
        logging.info("Reading and decrypting password database '"+
                args.database+"'...")
        password_database, database_password = read_and_decrypt(database_name)
        logging.info("Read and decrypted '"+args.database+"' successfully")
        # check to make sure the account exists in the database
        if account_name not in password_database.keys():
            logging.info("No account under the name '"+
                    account_name+"', notifying user and exiting")
            print("'"+account_name+"' does not exist in '"+database_name+"'")
        # otherwise, proceed with confirmation of deletion
        else:
            # confirm that the user really wants to delete the account
            logging.info("Account found under name '"+
                    account_name+"', confirming deletion with user...")
            response = ""
            while response not in ["y","Y","n","N"]:
                response = input("Are you sure you want to delete '"+
                        account_name+"'? (y/n) ")
            if response in ["y","Y"]:
                logging.info("Deletion of '"+
                        account_name+"' confirmed, deleting...")
                # delete the account
                del password_database[account_name]
                # encrypt and write new password database to disk
                logging.info("Deletion complete, encrypting and writing...")
                encrypt_and_write(password_database,
                        database_name,
                        database_password=database_password)
                print("Removed account '"+account_name+"'")
                logging.info("Encrypting and writing completed successfully"+
                        ", exiting")
            else:
                logging.info("Deletion of '"+account_name+"' aborted, exiting")
                print("Aborted")
    elif args.choice == "changepw":
        # decrypt password database
        logging.info("User selected 'changepw' subcommand")
        logging.info("Reading and decrypting password database '"+
                args.database+"'...")
        password_database, database_password = read_and_decrypt(args.database)
        logging.info("Read and decrypted '"+args.database+"' successfully")
        # encrypt the database with a new password and write it to disk
        logging.info("Prompting user for new password before encrypting and"+
                " writing...")
        encrypt_and_write(password_database, args.database)
        logging.info("Password changed successfully")
        print("Database password updated successfully")
