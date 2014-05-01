__author__ = 'Sumit.S'

import re
import optparse
import sqlite3
import sys
import os

def read_file(filepath):
    open_file = open(filepath, "rb")
    return "".join("{:02x}".format(int(ord(c))) for c in open_file.read(50))

def file_size(filepath):
    try:
        size = float(os.path.getsize(filepath))
        return_size = ""
        count = 0
        sizes = ["bytes", "KB", "MB", "GB", "TB"]
        while size > 1024:
            size /= 1024
            count += 1
        return_size = "{:0.2f} {}".format(size, sizes[count])
    except MemoryError:
        return_size = "Size too large"
    return return_size

def read_database(database_file):
    return_data = None
    try:
        con = sqlite3.connect(database_file)
        cur = con.cursor()
        cur.execute("SELECT * FROM signature")
        return_data = cur.fetchall()
    except sqlite3.Error, e:
        print "[-] ERROR : {}".format(e.args[0])
        sys.exit(1)
    finally:
        if con:
            con.close()
    return return_data

def match_type(filepath):
    file_data = read_file(filepath)
    db_data = read_database("signatures.sqlite")
    sign_regex = []
    ext_regex = []
    count = 0
    for row in db_data:
        sign_regex.append(row[1])
        ext_regex.append(row[0])
    match_flag = False
    extension = ""
    description = ""
    status = ""
    file_split = filepath.split(".")
    ext = file_split[len(file_split) - 1]
    if db_data:
        for regex in sign_regex:
            sg_re = re.compile("^" + regex)
            if sg_re.search(file_data):
                match_flag = True
                if db_data[count][0] == "*":
                    description = db_data[count][2]
                    status = "File Extension Check Pass"
                    extension = ext
                    break
                else:
                    if str(db_data[count][0]).lower() == str(ext).lower():
                        description = db_data[count][2]
                        status = "File Extension Check Pass"
                        extension = ext
                        break
                    else:
                        description = db_data[count][2]
                        status = "File Extension Check Fail"
                        extension = ""
                        pass
            count += 1

    return_data = ""
    if match_flag:
        return_data = "[+] Found \n\tFilenanme : " + filepath + "\n\tSize : " + file_size(filepath) + "\n\tDescription : " + description + "\n\tExtension : " + extension + "\n\tVerification : " + status
    else:
        return_data = "[-] Nothing known found\n\tFilenanme : " + filepath + "\n\tSize : " + file_size(filepath)

    return return_data

def main():
    optparser = optparse.OptionParser("%prog [OPTIONS]\n\rThis script is used to analyse files for their extension changes.")
    optparser.add_option("-f", "--file", dest="filename", type="string", help="File to analyse")
    (options, args) = optparser.parse_args()

    if not options.filename:
        optparser.print_help()
        exit(1)
    else:
        print (match_type(options.filename))

if __name__ == "__main__":
    main()