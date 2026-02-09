# import requests 
import sys


# Step 1: Read in wordlists for username and password
# Step 2: take in the requested url as an input parameter
# Step 3: set up data needed for sending POST or get request (starting off with POST)
# Step 4: User enumeration
# Step 5: Password Brute force using the username found within step 4

def read_wordfile(wordfile):
    # open passed wordfile file
    file = open(wordfile)

    # read file
    wordfile_list = file.readlines()
    
    # close file
    file.close()
        
    return wordfile_list


def enumerate_usernames(url):
    return


def main():
    if len(sys.argv) != 4:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com file/path/1 file/path/2" % sys.argv[0])
        sys.exit(-1)
    usernames = read_wordfile(sys.argv[2])
    print(usernames[:2])
    passwords = read_wordfile(sys.argv[3])
    print(passwords)

if __name__ == "__main__":
    main()