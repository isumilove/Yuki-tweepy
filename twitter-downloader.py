import configparser
from tweepy import OAuthHandler, API, Stream
import wget
import sys
import os

def main():
    # config
    cf = configparser.ConfigParser()
    cf.read("config.txt")
    CONSUMER_KEY = cf.get("API", "CONSUMER_KEY")
    CONSUMER_SECRET = cf.get("API", "CONSUMER_SECRET")
    ACCESS_TOKEN = cf.get("API", "ACCESS_TOKEN")
    ACCESS_TOKEN_SECRET = cf.get("API", "ACCESS_TOKEN_SECRET")
    proxy=cf.get("Proxy","http_proxy")
    #auth
    api = authentication(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN,ACCESS_TOKEN_SECRET)
    print('\n\nTwitter Image And Video Downloader:\n========================\n')
    username = input("\nEnter the twitter Account(For Example:@abc123): ")
    #proxy
    os.environ['http_proxy'] =proxy
    os.environ['https_proxy'] =proxy

    max_tweets = 3200  ##user_timeline can only return up to 3,200 of a user’s most recent Tweets.
    tweetset = getTweetsUser(username, max_tweets, api)
    media_URLs = getTweetMediaURL(tweetset)
    downloadFiles(media_URLs, username)
    print('\n\nFinished Downloading.\n')


def getTweetsUser(username, max_tweets, api):
    # get all tweets from 'username'
    try:
        raw_tweets = api.user_timeline(screen_name=username, include_rts=False, exclude_replies=True)
    except Exception as e:
        print(e)
        sys.exit()
    last_tweet_id = int(raw_tweets[-1].id - 1)
    print('\ngetting tweets.....')
    i = 0
    f = open("tweets.txt", "w", encoding='utf-8')
    while i < max_tweets:
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
    f.write(str(raw_tweets))
    f.close()
    return raw_tweets
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
                            for vi in videomedia['video_info']['variants']:
                                if str(vi['url']).find('.m3u8')==-1:
                                    tweets_with_media.add(vi['url'])
                                    sys.stdout.write("\rMedia Links fetched: %d" % len(tweets_with_media))
                                    sys.stdout.flush()
                        else:
                        # images
                            for imagemedia in tweet.extended_entities['media']:
                                tweets_with_media.add(imagemedia['media_url'])
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
        wget.download(url)
    print('\nAll Finished......')


def authentication(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN,ACCESS_TOKEN_SECRET):
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = API(auth)
    return api


if __name__ == '__main__':
    main()
