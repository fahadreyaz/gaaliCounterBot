from dotenv import load_dotenv
import os
import praw
import re

load_dotenv()

reddit = praw.Reddit(
    client_id = os.getenv('CLIENT_ID'),
    client_secret = os.getenv('CLIENT_SECRET'),
    username = os.getenv('USERNAME'),
    password = os.getenv('PASSWORD'),
    user_agent = 'gaalicounter'
)

auth_user = reddit.user.me()

wordsDict = {}
with open('words.txt', 'r') as f:
    for line in f.readlines():
        wordsDict[line.strip()] = 0

while True:
    try:
        notifications = reddit.inbox.unread(limit=None)
        for comment in notifications:
            body = comment.body.lower()
            if auth_user.name.lower() not in body:
                continue
            
            if 'self' in body:
                target = comment.author
            else:
                wordList = body.strip().split()
                mentions = []
                for word in wordList:
                    if word.startswith('u/') and len(word)>=4 and auth_user.name.lower() not in word:
                        word = word.replace('u/','')
                        mentions.append(word)
                if mentions:
                    target = reddit.redditor(mentions[0])
                else:
                    is_reply = not comment.parent_id.startswith('t3')
                    if is_reply:
                        target = reddit.comment(comment.parent_id).author
                    else:
                        target = comment.author

            if target.name.lower() == auth_user.name.lower():
                target = comment.author
    
            user_comments = target.comments.new(limit=800)
            comment_count = 0
            for user_comment in user_comments:
                comment_count+=1
                wordList = re.sub(r'[^\w\s]','', user_comment.body.lower().strip()).split()
                for word in wordList:
                    if word in list(wordsDict.keys()):
                        wordsDict[word]+=1
                
            for key in list(wordsDict.keys()):
                if wordsDict[key] == 0:
                    del wordsDict[key]

            intro_text = f"Beep Boop! I am here to check hindi profanity usage of u/{target}\n\n"
            stat_str = f"Congratulations! You haven't used any hindi slangs in your recent {comment_count} comments"
            if not wordsDict == {}:
                stat_str = f"Here's their profanity usage from their last {comment_count} comments:\n\n| Word | Count |\n| --- | --- |\n"
                for key in list(wordsDict.keys()):
                    stat_str+=f"| {key} | {wordsDict[key]} |\n"

            link = "\n\n^([github](https://github.com/fahadreyaz/gaaliCounterBot))"
            reply = intro_text + stat_str + link
            comment.reply(body=reply)
            comment.mark_read()
            
    except Exception as e:
        print(e)
        continue
