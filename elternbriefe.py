from twill.commands import *
from login_stuff import secrets
import requests
import urllib.parse
import re
import os
import random
import pickle

# login_stuff.py
# secrets = {
# 'username': '',
# 'password': '',
# 'school': '',
# }

output_folder = 'files'
main = f'https://{secrets['school']}.eltern-portal.org/'


def sanitize_filename(name):
    print(name)
    # Replace invalid characters with underscores
    name = re.sub(r'[\\/*?:"<>| ]+', '_', name)

    # Remove leading and trailing underscores
    name = re.sub(r'^_+|_+$', '', name)

    # Fix encoding badly but kinda works
    name = name.replace('Ã¤', 'ä').replace('Ã¶', 'ö').replace('Ã¼', 'ü').replace(
        'ÃŸ', 'ß').replace('Ã„', 'Ä').replace('Ã–', 'Ö').replace('Ãœ', 'Ü')

    # Limit the length to a reasonable value (e.g., 100 characters)
    name = name[:100]
    return name


def download_file(browser, url, name=None, main_page=main):
    url = main + url
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get cookies from twill
    cookies = requests.utils.dict_from_cookiejar(browser.cookies().jar)

    response = requests.get(url, stream=True, cookies=cookies, headers={
                            'User-Agent': browser.user_agent})

    if name is None:
        if 'Content-Disposition' in response.headers:
            # Extract the filename from the Content-Disposition header
            header_filename = requests.utils.requote_uri(
                response.headers['Content-Disposition'].split('filename=')[-1].strip('\''))
            header_filename = urllib.parse.unquote(header_filename)
            name = sanitize_filename(header_filename)
        else:
            print(f'{url} : File name not found, using random file name.')
            # Gen random number and save file as pdf as best guess
            name = f'{random.random()}.pdf'[2:]

    name = sanitize_filename(name)

    with open(os.path.join(output_folder, name), 'wb') as handle:

        if not response.ok:
            raise Exception('Could not get file from ' + url)

        for block in response.iter_content(1024):
            handle.write(block)

        print(f'Saved \'{name}\' to {output_folder}.')


go(main)


assert 'Eltern-Portal' in browser.html

fv('1', 'username', secrets['username'])
fv('1', 'password', secrets['password'])

submit('0')

go(main+'aktuelles/elternbriefe')

links = []

for link in browser.links:
    if 'get_file' in link[1]:
        links.append(link[1])

# print(links)

old_links = []

try:
    with open('old_links.pkl', 'rb') as file:
        try:
            old_links = pickle.load(file)
        except EOFError as e:
            print(e)
except FileNotFoundError:
    print('no old links found')

# Check that only new links get downloaded by stripping all with a ?repo=xxxx that have already been scraped
new_links = [link for link in links if link[25:29]
             not in [repo[25:29] for repo in old_links]]

if len(new_links) == 0:
    print('no new entries')

for file in new_links:
    download_file(browser, file)

with open('old_links.pkl', 'wb') as file:
    pickle.dump(links, file, pickle.HIGHEST_PROTOCOL)
