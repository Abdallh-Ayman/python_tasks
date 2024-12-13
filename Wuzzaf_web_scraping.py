import requests
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd
import math

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

def extract_data(dom):
    """Extract job data from the page and return as a list of dictionaries."""
    all_jobs = dom.xpath('//*[@id="app"]/div/div[3]/div/div/div[2]/div')
    job_list = []
    for job in all_jobs:
        job_data = {
            'Job Title': job.xpath('string(div/div/h2/a)'),
            'Company Name': job.xpath('string(div/div/div/a)'),
            'Location': job.xpath('string(div/div/div/span)'),
            'Job Date': job.xpath('string(div/div/div/div)'),
            'Type Time': job.xpath('string(div/div[2]/div//*[@class="css-1ve4b75 eoyjyou0"])'),
            'Type Site': job.xpath('string(div/div[2]/div//*[@class="css-o1vzmt eoyjyou0"])'),
            'Experience Type': job.xpath('string(div/div[2]/div[2]/a[1])'),
            'Experience Year': job.xpath('string(div/div[2]/div[2]/span)').replace('·', '').strip()
        }
        job_list.append(job_data)
    return job_list

def save_to_excel(job_list, file_path):
    """Save job data to an Excel file."""
    new_jobs_df = pd.DataFrame(job_list)
    try:
        old_jobs_df = pd.read_excel(file_path)
        combined_jobs_df = pd.concat([old_jobs_df, new_jobs_df], ignore_index=True)
    except FileNotFoundError:
        combined_jobs_df = new_jobs_df
    combined_jobs_df.to_excel(file_path, index=False)

def main():
    job_search = input('Enter job to search on it: ')
    source_url = f'https://wuzzuf.net/search/jobs/?a=navbl&q={job_search}&start=0'
    excel_path = 'jobs_data.xlsx'
    headers = {}
    dom = fetch_and_parse_html(source_url, headers) # it return xml
    job_list = extract_data(dom)
    page_number = get_number_of_pages(dom)
    save_to_excel(job_list, excel_path)

    for i in range(1,page_number):
        page_url = f'https://wuzzuf.net/search/jobs/?a=navbl&q={job_search}&start={i}'
        page_dom = fetch_and_parse_html(page_url, headers)
        job_list = extract_data(page_dom)
        save_to_excel(job_list, excel_path)

if __name__ == '__main__':
    main()
