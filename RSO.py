import sys, os, requests, calendar, arrow
from pathlib import Path
from enum import Enum

unsave = False
user = 'KageyKay'
password = ''
key = ''
secret = ''
subs = []
scrub = []
count = 0

class PostValue(Enum):
    # The two posts are entirely different
    UNIQUE = 1
    # The two posts share a title and nothing else
    TITLE = 2
    # The two posts share a title, and were posted at the same time, in the same place, by the same author
    EDIT = 3
    # The two posts are identical
    DUPLICATE = 4
    
        
def nextPage():
    global response, count
    if (response.json()['data']['after'] == None):
        return 0
    else:
        count += 100
        after = response.json()['data']['after']
        response = requests.get(f'https://oauth.reddit.com/user/{user}/saved?raw_json=1&limit=100&count={count}&after={after}', headers=headers)
        return 1
    
#returns ABSOLUTE Filepath of saved post
def namePost(title, subreddit):
    title = title.replace('/', '')
    title = title.replace('\\', '')
    title = title.replace(':', '')
    title = title.replace('*', '')
    title = title.replace('?', '')
    title = title.replace('"', '')
    title = title.replace('<', '')
    title = title.replace('>', '')
    title = title.replace('|', '')
                
    name = Path.cwd() / Path(subreddit) / title
    name = os.path.dirname(name)
    if(len(name) < 250):
        return Path(name)
    else:
        name = name[:250]
        return Path(name)

def checkContent(filePath):
    if ((filePath / ".txt").is_file()):
        oldPost = open(filePath / ".txt", encoding='utf-8')
        hSize = len(header.encode('utf-8'))
        cSize = len(content.encode('utf-8'))
        oSize = os.stat(oldPost.name).st_size
                        
        if (header == oldPost.read(hSize)):
            oldPost.seek(0)
            # content.encode() == oldPost.read().encode()
            if (cSize == oSize):
                oldPost.close()
                return PostValue.DUPLICATE
            else:
                return PostValue.EDIT
        else:
            oldPost.close()
            return PostValue.TITLE   
    else:
        return PostValue.UNIQUE
    
def savePost():
    while (True):
        for post in response.json()['data']['children']:
            # 'kind' must be checked before 'is_self', only t3 posts have an 'is_self' attribute
            if (post['kind'] == 't3' and post['data']['is_self']):
                print(post['data']['title'])
                subreddit = post['data']['subreddit']
                if(len(subs)):
                    print(len(subs))
                    print(type(subs))
                    if(subreddit.lower() not in subs):
                        continue
                scrub.append(post['data']['name'])
                
                if(not Path(subreddit).is_dir()):
                    os.makedirs(subreddit)
                    
                title = post['data']['title']
                selftext = post['data']['selftext']
                author = post['data']['author']
                link = post['data']['permalink']
                dateUTC = arrow.get(post['data']['created'])
                dateLocal = dateUTC.to('local')
                time = f"Posted: {dateLocal.format('MMMM DD, YYYY')} at {dateLocal.format('HH:mm')}"
                header = f"{title}: by {author}\n\n{time}"
                footer = f"Permalink:{link}"
                content = header+"\n\n\n"+selftext+"\n\n\n"+footer
                   
                # This is where I save the posts
                # Duplicate = ignore
                # Title = rename and check again
                # Edited = rename and check again
                # Unique = save post to computer
                try:
                    fileNum = 1
                    filePath = namePost(title, subreddit)
        
                    filePath = Path(os.path.abspath(filePath) + ".txt")
                    print(filePath)
                    
                    #use enum.name.value
                    
                    

                    file = open(filePath, 'w', encoding="utf-8")               
                    file.write(content)
                    file.close()
                except Exception as e:
                    print(e)
                    print(f"Error, couldn't save: '{title}'")
                    file.close()
                    exit()
                    
        if(nextPage()):
            break
        
if (len(sys.argv) > 1):
    for arg in sys.argv[1:]:
        if arg == "-unsave":
            unsave = True
        else:
            subs.append(arg)
    for i, name in enumerate(subs):
        subs[i] = name.lower()
print((subs))


data = {'grant_type': 'password', 'username': user, 'password': password}
auth = requests.auth.HTTPBasicAuth(key, secret)
r = requests.post('https://www.reddit.com/api/v1/access_token', data=data, headers={'user-agent':'RSO.py by kr0bat'}, auth=auth)
d = r.json()

print(checkContent(Path('test')))

if 'error' in d.keys():
    print(d['error'])
    exit()

token = d['token_type'] +' '+ d['access_token']
headers = {'Authorization': token, 'User-Agent': 'RSO.py by kr0bat'}
# I'm not requesting the raw Json, is data being scrubbed?
response = requests.get(f'https://oauth.reddit.com/user/{user}/saved?raw_json=1&limit=100', headers=headers)

print(response)

savePost()
  

        
if(unsave):
    print(scrub)
    for id in scrub:
        print(requests.post(f'https://oauth.reddit.com/api/unsave?id={id}', headers=headers))
    