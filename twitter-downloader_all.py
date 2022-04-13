# -*- coding: utf-8 -*-
import configparser
from tweepy import OAuthHandler, API, Stream
import wget
import sys
import os
import io
import json

def main():
    # config
    cf = configparser.ConfigParser()
    cf.read("config.txt")
    CONSUMER_KEY = cf.get("API", "CONSUMER_KEY")
    CONSUMER_SECRET = cf.get("API", "CONSUMER_SECRET")
    ACCESS_TOKEN = cf.get("API", "ACCESS_TOKEN")
    ACCESS_TOKEN_SECRET = cf.get("API", "ACCESS_TOKEN_SECRET")
    user = configparser.ConfigParser()
    user.read("user.conf")
    proxy=cf.get("Proxy","http_proxy")
    #auth
    api = authentication(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN,ACCESS_TOKEN_SECRET)
 #   print('\n\nTwitter Image And Video Downloader:\n========================\n')
 #   username = input("\nEnter the twitter Account(For Example:@abc123): ")
    #proxy
  #  os.environ['http_proxy'] =proxy
  #  os.environ['https_proxy'] =proxy
    useList = getUser(api)
    max_tweets = 3200 ##user_timeline can only return up to 3,200 of a user’s most recent Tweets.
    black_list = []
    with open("black_list", "r") as f:
        for line in f.readlines():
                black_list.append(line.strip())
    for userid in useList:
        print userid
        tweetset,username,last_id = getTweetsUser(userid, max_tweets, api, user, black_list)
        if tweetset !=False:
            if username in black_list:
                continue
            media_URLs = getTweetMediaURL(tweetset)
            downloadFiles(media_URLs, username)
            user.set("user", username, str(last_id))
            print(user.get("user", username))
            os.chdir('../../')
            user.write(open("user.conf", "w"))
    print('\n\nFinished Downloading.\n')

def getUser(api):
    nameList = []
    myFriends = api.friends_ids()
    for friend in myFriends:
        nameList.append(friend)
    return nameList
def getTweetsUser(userid, max_tweets, api, user_config, black_list):
    # get all tweets from 'username'
    try:
        raw_tweets = api.user_timeline(id=userid, include_rts=False, exclude_replies=True, count=1)
    except Exception as e:
        print(e)
        return False,False,False
    if len(raw_tweets) == 0 :
        return False,False,False
    user = getattr(raw_tweets[0], 'user')
    if user.followers_count < 1000:
        return False,False,False
    print user.screen_name
    username = user.screen_name
    if username in black_list:
        return False,False,False
    last_tweet_id = int(raw_tweets[-1].id - 1)
    real_last_tweet_id = int(raw_tweets[-1].id - 1)
    begin_id = 0
    if user_config.has_option('user', username.lower()):
        begin_id = user_config.getint('user', username.lower())
    i = 0
    print("begin_id:%d" % begin_id)
    print("end_id:%d" % last_tweet_id)
    print('\ngetting tweets.....')
    while begin_id < last_tweet_id and i < max_tweets:
        sys.stdout.write("\rTweets count: %d" % len(raw_tweets))
        sys.stdout.flush()
        temp_raw_tweets = api.user_timeline(screen_name=username, max_id=last_tweet_id, include_rts=False,
                                            exclude_replies=True)

        if len(temp_raw_tweets) == 0:
            break
        else:
            last_tweet_id = int(temp_raw_tweets[-1].id - 1)
            raw_tweets = raw_tweets + temp_raw_tweets
            i = i + 1

    print('\nFinished getting ' + str(min(len(raw_tweets), max_tweets)) + ' Tweets.')

    return raw_tweets,username,real_last_tweet_id
def getTweetMediaURL(tweetset):
    #get all images' and videos' url
    print('\nCollecting Media URLs.....')
    tweets_with_media = set()
    for tweet in tweetset:
        if hasattr(tweet, 'extended_entities'):
            media = tweet.extended_entities.get('media', [])
            if (len(media) > 0):
                # Videos
                if 'media' in tweet.extended_entities:
                    for videomedia in tweet.extended_entities['media']:
                        if 'video_info' in videomedia:
                            #get best video
                            video_size = 0
                            video_url = ''
                            for vi in videomedia['video_info']['variants']:
                                if str(vi['url']).find('.m3u8')==-1:
                                    if vi['bitrate'] > video_size:
                                        video_size = vi['bitrate']
                                        video_url = vi['url']
                            print video_url
                            tweets_with_media.add(video_url)
                            sys.stdout.write("\rMedia Links fetched: %d" % len(tweets_with_media))
                            sys.stdout.flush()
                        else:
                        # images
                            for imagemedia in tweet.extended_entities['media']:
                                tweets_with_media.add(imagemedia['media_url'])
                                print imagemedia['media_url']
                                sys.stdout.write("\rMedia Links fetched: %d" % len(tweets_with_media))
                                sys.stdout.flush()

    print('\nFinished fetching ' + str(len(tweets_with_media)) + ' Links.')

    return tweets_with_media


def downloadFiles(media_url, username):
    #download
    print('\nDownloading......')
    try:
        os.mkdir('tweetmedia')
        os.chdir('tweetmedia')
    except:
        os.chdir('tweetmedia')
    try:
        os.mkdir(username)
        os.chdir(username)
    except:
        os.chdir(username)
    for url in media_url:
        try:
            wget.download(url)
        except Exception as e:
            print("error url:%s" % url)
            continue
    print('\nAll Finished......')


def authentication(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN,ACCESS_TOKEN_SECRET):
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = API(auth)
    return api


if __name__ == '__main__':
    main()
