import threading
import time

import requests
from bs4 import BeautifulSoup
from lxml import etree
import math
from pymongo import MongoClient

def fetch_and_parse_html(url, headers):
    """Fetch page content from a given URL and parse the HTML."""
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        dom = etree.HTML(str(soup))
        return dom
    else:
        raise Exception(f"Failed to retrieve data, status code: {response.status_code}")

def get_number_of_pages(dom):
    """Extract total number of jobs and calculate number of pages."""
    jobs_number_text = dom.xpath('string(//*[@id="app"]/div/div[3]/div/div/div[3]//*[@class="css-8neukt"])')
    jobs_number = int(jobs_number_text.split(" ")[-1])
    return math.ceil(jobs_number / 15)

def extract_data(dom,job_search):
    """Extract job data from the page and return as a list of dictionaries."""
    all_jobs = dom.xpath('//*[@id="app"]/div/div[3]/div/div/div[2]/div')

    job_list = []
    for job in all_jobs:

        Job_Title = job.xpath('string(div/div/h2/a)')
        job_link = job.xpath('string(div/div/h2/a/@href)')
        Company_Name=job.xpath('string(div/div/div/a)')
        Location= job.xpath('string(div/div/div/span)')
        Job_Date = job.xpath('string(div/div/div/div)')
        Type_Time=job.xpath('string(div/div[2]/div//*[@class="css-1ve4b75 eoyjyou0"])')
        Type_Site=job.xpath('string(div/div[2]/div//*[@class="css-o1vzmt eoyjyou0"])')
        Experience_Type= job.xpath('string(div/div[2]/div[2]/a[1])')
        Experience_Year =job.xpath('string(div/div[2]/div[2]/span)').replace('·', '').strip()

        job_data = {
            'user_words_search':job_search,
            'Job_Title': Job_Title,
            'Company_Name':Company_Name ,
            'Location': Location ,
            'Job_Date': Job_Date,
            'Type_Time':Type_Time ,
            'Type_Site': Type_Site,
            'Experience_Type':Experience_Type ,
            'Experience_Year': Experience_Year,
            'job_link':job_link
        }
        job_list.append(job_data)
    return job_list

def save_to_mongodb(job_list, db_name, collection_name):
    """Save job data to MongoDB."""
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    collection = db[collection_name]
    collection.insert_many(job_list)

def thread_worker(job_search, i, headers, db_name, collection_name):
    page_url = f'https://wuzzuf.net/search/jobs/?a=navbl&q={job_search}&start={i}'
    page_dom = fetch_and_parse_html(page_url, headers)
    job_list = extract_data(page_dom, job_search)
    save_to_mongodb(job_list, db_name, collection_name)

def main():
    job_search = input('Enter job to search on it: ')
    source_url = f'https://wuzzuf.net/search/jobs/?a=navbl&q={job_search}&start=0'
    headers = {}
    dom = fetch_and_parse_html(source_url, headers)
    job_list = extract_data(dom,job_search)
    page_number = get_number_of_pages(dom)
    save_to_mongodb(job_list, 'test', 'Wuzzuf_Jobs')


    #using multithreading
    threads = []
    start_time = time.time()
    for i in range(1, page_number):
        thread = threading.Thread(target=thread_worker, args=(job_search, i, headers, 'test', 'Wuzzuf_Jobs'))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


    # without using multithreading

    # for i in range(1, page_number):
    #     page_url = f'https://wuzzuf.net/search/jobs/?a=navbl&q={job_search}&start={i}'
    #     page_dom = fetch_and_parse_html(page_url, headers)
    #     job_list = extract_data(page_dom,job_search)
    #     save_to_mongodb(job_list, 'Test', 'Wuzzuf_Jobs')

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total execution time: {total_time:.2f} seconds")

if __name__ == '__main__':
    main()
