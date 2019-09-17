import os, time
import gspread
import schedule as plan
from datetime import datetime
from InstagramAPI import InstagramAPI
from oauth2client.service_account import ServiceAccountCredentials as SAS

# Google Sheets functions
def archivePost(post, timestamp):
    future_posts = client.open("InstautoDB").sheet1
    past_posts = client.open("IGPostsDB").sheet1

    try:
        cell = future_posts.find(post['file'])
    except Exception as e:
        cell = future_posts.find(post)
    
        future_posts.delete_row(cell.row)

    row = [post, timestamp]
    index = 1
    past_posts.insert_row(row, index)

# IG functions
def loginIG():
    user = os.environ.get("IG_USER")
    passw = os.environ.get("IG_PASS")
    ig = InstagramAPI(user, passw)
    ig.login()
    return ig

def stageAlbum():
    print("Sheet opening...")
    
    time.sleep(1)
    
    set = client.open("InstautoAlbumDB").sheet1
    media = []
    caption = (set.col_values(2))[0]
    print("Setting up photos...")
    
    time.sleep(1)
    
    for photos in set.col_values(1):
        file = {
            'type':'photo',
            'file':photos
            }
        media.append(file)

    print("Album is staged\n")
    return [media, caption]

def uploadA():
    ig = loginIG()
    post = stageAlbum()
    ig.uploadAlbum(post[0], caption=post[1])
    for items in post[0]:
        item = logtime(items)
        archivePost(item[0],item[1])

def uploadP():
    ig = loginIG()
    # Find a workbook by name and open the first sheet
    posts = client.open("InstautoDB").sheet1

    post_count = 1
    for post in posts.get_all_values():
        photo = post[0]
        caption = post[1]
        ig.uploadPhoto(photo, caption=caption)
        post_and_time = logtime(photo)
        archivePost(post_and_time[0],post_and_time[1])
        print("post",post_count,"successfully uploaded!")
        post_count += 1

# Timestamp functions
def write_file(location, msg):
    with open(location, "a") as f:
        f.write(msg)

def read_file(location):
    with open(location, "r") as f:
        msg = f.read()
    return(msg)

def base(path):
    print(path)
    try:
        return os.path.basename(path['file'])
    except Exception as e:
        return os.path.basename(path)

def logtime(path):
    file = base(path).split('.')[0]
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    timestamp = "{} : {}\n".format(file, current_time)
    write_file("timestamps.txt",timestamp)
    print("timestamp written")
    print(timestamp)
    return [path, current_time]


# use creds to create a client to interact with the Google Drive API
scope = [
      'https://www.googleapis.com/auth/analytics.readonly',
      'https://www.googleapis.com/auth/drive',
      'https://www.googleapis.com/auth/spreadsheets'
    ]
creds = SAS.from_json_keyfile_name("client_secret.json", scope)
client = gspread.authorize(creds)