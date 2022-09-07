# -*- coding: utf-8 -*-
"""Twitter API

# Send requests to Twitter API v2 and save them as CSV file

Inspired by [medium](https://towardsdatascience.com/an-extensive-guide-to-collecting-tweets-from-twitter-api-v2-for-academic-research-using-python-3-518fcb71df2a)'s post by Andrew Edward

Import Libraries
"""

import requests
from dotenv import dotenv_values
import json
import csv
import time
import datetime
import dateutil.parser

"""## Take your bearer_token"""

config = dotenv_values("../.env")
bearer_token = config["BEARER_TOKEN"]

"""## Function Bearer Token"""

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2TweetLookupPython"
    return r

"""## Function Connect to Endpoint"""

def connect_to_endpoint(url, params, next_token = None):
    params['next_token'] = next_token 
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

"""## Function Create URL"""

def create_url(username, start_time, end_time, max_results):

    search_url = "https://api.twitter.com/2/tweets/search/recent"
    # Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
    # expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
    query_params = {'query': f'from:{username}',
                    'tweet.fields': 'lang,author_id,created_at,public_metrics,possibly_sensitive', 
                    'user.fields': f'description',
                    'max_results': f'{max_results}',
                    'next_token': {}}
    params =  {'start_time': f'{start_time}',
               'end_time': f'{end_time}'
               }
    return (search_url, query_params)

"""## Function to csv

Function very important as it converts json to csv file go check Andrew Edward post on medium for a more complete version
"""

def append_to_csv(json_response, fileName):

    #A counter variable
    counter = 0

    #Open OR create the target CSV file
    csvFile = open(fileName, "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)

    #Loop through each tweet
    for tweet in json_response['data']:
        
        # We will create a variable for each since some of the keys might not exist for some tweets
        # So we will account for that

        # 1. Author ID
        author_id = tweet['author_id']

        # 2. Time created
        created_at = dateutil.parser.parse(tweet['created_at'])

        # 3. Tweet ID
        tweet_id = tweet['id']

        # 4. Language
        lang = tweet['lang']

        # 5. Tweet metrics
        retweet_count = tweet['public_metrics']['retweet_count']
        reply_count = tweet['public_metrics']['reply_count']
        like_count = tweet['public_metrics']['like_count']
        quote_count = tweet['public_metrics']['quote_count']

        # 6. posibility_sensitive
        possibly_sensitive = tweet['possibly_sensitive']

        # 7. Tweet text
        text = tweet['text']
        
        # Assemble all data in a list
        res = [author_id, created_at, tweet_id, lang, like_count, quote_count, reply_count, retweet_count, possibly_sensitive, text]
        
        # Append the result to the CSV file
        csvWriter.writerow(res)
        counter += 1

    # When done, close the CSV file
    csvFile.close()

    # Print the number of tweets for this iteration
    print("# of Tweets added from this response: ", counter) 


    time.sleep(6)

"""#### Fetch results from twitter"""

#Inputs for tweets
max_results = 100
start_date = '2022-08-28T07:00:00Z'
end_date = datetime.datetime.utcnow().isoformat()

#Total number of tweets we collected from the loop
total_tweets = 0


# Create file
csvFile = open("data.csv", "a", newline="", encoding='utf-8') #3 entries for csv
csvWriter = csv.writer(csvFile)

#Create headers for the data you want to save
csvWriter.writerow(['author id', 'created_at', 'id', 'lang', 'like_count', 'quote_count', 'reply_count','retweet_count','possibly_sensitive', 'text'])
csvFile.close()

# I am working on a list of name called famous_list and iterating over each name and storing them in a csv file
for i in range(0,len(famous_list)):

    # Inputs
    count = 0 # Counting tweets per time period
    max_count = 100 # Max tweets per time period
    flag = True
    next_token = None

    # Check if flag is true
    while flag:
        # Check if max_count reached
        if count >= max_count:
            break
        print("-------------------")
        print("Token: ", next_token)
        url = create_url(famous_list[i], start_date, end_date, max_results)
        json_response = connect_to_endpoint(url[0], url[1], next_token) #url[0] is data and url[1] is meta
        result_count = json_response['meta']['result_count']

        if 'next_token' in json_response['meta']:
            # Save the token to use for next call
            next_token = json_response['meta']['next_token']
            print("Next Token: ", next_token)
            if result_count is not None and result_count > 0 and next_token is not None:
                print("Famous Name: ", famous_list[i])
                append_to_csv(json_response, "data.csv")
                count += result_count
                total_tweets += result_count
                print("Total # of Tweets added: ", total_tweets)
                print("-------------------")
                time.sleep(10)                
        # If no next token exists
        else:
            if result_count is not None and result_count > 0:
                print("-------------------")
                print("Famous Name: ", famous_list[i])
                append_to_csv(json_response, "data.csv")
                count += result_count
                total_tweets += result_count
                print("Total # of Tweets added: ", total_tweets)
                print("-------------------")
                time.sleep(10)

            flag = False
            next_token = None
        time.sleep(60)
    print("Total number of results: ", total_tweets)