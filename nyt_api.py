## Take data from API NYT
##Code derived from the [medium article](https://towardsdatascience.com/collecting-data-from-the-new-york-times-over-any-period-of-time-3e365504004) by Brienna Herold

#### Import libraries
"""

import os
import requests
import pandas as pd
import numpy as np
from dotenv import dotenv_values, load_dotenv
import time
import datetime
import dateutil
from dateutil.relativedelta import relativedelta

"""#### Pick the API keys in your dotenv file. The path can be modified"""

config = dotenv_values("../.env")
API_KEY = config["API_KEY"]

"""## Full code API NYT

set the date
"""

begin_date = 20220101   #format 20120101
end_date = 20220829

"""set the pages up to 1889 outputs"""

query = "stock"
page_begin = 1
page_end = 201

"""Define a function to pick the headlines, dates and so on...."""

def send_request(page_begin, page_end):
    data = {'headline': [],  
        'date': [], 
        'doc_type': [],
        'material_type': [],
        'section': [],
        'keywords': []}
    
    
    for page in np.arange(page_begin, page_end, 1).tolist():
        params_intra = {"fq" : f"{query}",
                "page":f"{page}",
                "begin_date": f"{begin_date}",
                "end_date": f"{end_date}",
                "api-key" : f"{API_KEY}",
         }
        url = f"https://api.nytimes.com/svc/search/v2/articlesearch.json?fq={query}&facet_fields=source&page={page}&facet=true&begin_date={begin_date}&end_date={end_date}&api-key={API_KEY}"
        response = requests.get(url, params=params_intra).json()
        time.sleep(6)
    
        articles = response['response']['docs'] 
        for article in articles: 
            date = dateutil.parser.parse(article['pub_date']).date()
            if type(article['headline']) == dict and 'main' in article['headline'].keys():
                data['date'].append(date)
                data['headline'].append(article['headline']['main']) 
                if 'section' in article:
                    data['section'].append(article['section_name'])
                else:
                    data['section'].append(None)
                    data['doc_type'].append(article['document_type'])
                if 'type_of_material' in article: 
                    data['material_type'].append(article['type_of_material'])
                else:
                    data['material_type'].append(None)
                keywords = [keyword['value'] for keyword in article['keywords'] if keyword['name'] == 'subject']
                data['keywords'].append(keywords)
    return pd.DataFrame(data)

"""ask the request"""

data = send_request(page_begin, page_end)

"""print csv"""

data.to_csv('testDF_NYT_headlines_full.csv', index=False)