import sys, os, requests, calendar, arrow
from pathlib import Path

unsave = False
user = 'kr0bat'
password = ''
key = ''
secret = ''
subs = ['']
scrub = []

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

if 'error' in d.keys():
    print(d['error'])
    exit()

token = d['token_type'] +' '+ d['access_token']
headers = {'Authorization': token, 'User-Agent': 'RSO.py by kr0bat'}
# I'm not requesting the raw Json, is data being scrubbed?
response = requests.get(f'https://oauth.reddit.com/user/{user}/saved?raw_json=1&limit=100', headers=headers)
count = 0
print(response)

while (True):
    for post in response.json()['data']['children']:
        subreddit = post['data']['subreddit']
        
        
        # 'kind' must be checked before 'is_self', only t3 posts have an 'is_self' attribute
        if (post['kind'] == 't3' and post['data']['is_self']):
            if(len(subs)):
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
            
            title = title.replace('/', '')
            title = title.replace('\\', '')
            title = title.replace(':', '')
            title = title.replace('*', '')
            title = title.replace('?', '')
            title = title.replace('"', '')
            title = title.replace('<', '')
            title = title.replace('>', '')
            title = title.replace('|', '')
                        
            try:
                # Make this less stupid pls
                # Truncate the title only if the filename is near windows character limit
                filePath = Path(subreddit) / f"{title[:25]}"                
                fileNum = 1
                
                
                
                
                
                
                # This block of code should only run if the files are proven to be a different post, otherwise the post should be ignored/overwritten
                # If the files have the same name, author, and time, and the filesize is different create a new file called "{title} (edit)"
                # If the contents are the same leave the old file unedited and skip over the post
                
                
                if ((subreddit / Path(filePath.name + ".txt")).is_file()):
                    oldPost = open(os.path.abspath(filePath) + ".txt", encoding='utf-8')
                    
                    """
                    print(oldPost.read())
                    print('\n----------------\n')
                    print(content)
                    """
                    
                    hSize = len(header.encode('utf-8'))
                    cSize = len(content.encode('utf-8'))
                    oSize = os.stat(oldPost.name).st_size
                    
                    if (header == oldPost.read(hSize)):
                        oldPost.seek(0)     
                        if (content.encode() == oldPost.read().encode() or cSize == oSize):
                            print("SAME FILE")
                            continue
                    else:
                        while ((subreddit / Path(filePath.name + ".txt")).is_file()):
                            filePath = Path(subreddit) / f"{title[:25]}_{fileNum}"
                            if ((subreddit / Path(filePath.name + ".txt")).is_file()):
                                fileNum += 1
                    oldPost.close()
                filePath = Path(os.path.abspath(filePath) + ".txt")
                print(filePath)
                

                file = open(filePath, 'w', encoding="utf-8")               
                file.write(content)
                file.close()
            except Exception as e:
                print(e)
                print(f"Error, couldn't save: '{title}'")
                file.close()
                exit()
  
    # go to next page
    if (response.json()['data']['after'] == None):
        break
    else:
        count += 100
        after = response.json()['data']['after']
        response = requests.get(f'https://oauth.reddit.com/user/{user}/saved?raw_json=1&limit=100&count={count}&after={after}', headers=headers)
        
if(unsave):
    print(scrub)
    for id in scrub:
        print(requests.post(f'https://oauth.reddit.com/api/unsave?id={id}', headers=headers))
    