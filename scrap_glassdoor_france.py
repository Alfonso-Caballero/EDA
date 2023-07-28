from functools import reduce
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re
import pandas as pd
from selenium.common.exceptions import *

"""
The same code as 'scrap_glassdoor_spain', with few changes, like the format of the strings we get from the french page.
"""


def clean_salary(list_of_salaries):
    for index in range(len(list_of_salaries)):
        if "k" and "-" in list_of_salaries[index]:
            bad_format_salary = []
            split_salary = list_of_salaries[index].split(" ")
            for group in split_salary:
                if group.isdigit():
                    group = int(group)
                    group *= 1000
                    bad_format_salary.append(group)
            good_format_salary = ((bad_format_salary[0] + bad_format_salary[1]) / 2)
            list_of_salaries[index] = int(good_format_salary)
        else:
            list_of_salaries[index] = re.sub("[^0-9]", "", list_of_salaries[index])

    return list_of_salaries


def set_browser():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
    driver = webdriver.Chrome(chrome_options)

    return driver


def check_pages_main_page(pages):
    pages_list = re.split('[- ]', pages.text)
    pages_list = [x for x in pages_list if x[0].isdigit()]
    pages_list = set(pages_list)
    if len(pages_list) == 3:
        return True
    else:
        return False


def check_company_pages(pages):
    pages_list = re.split('[  ]', pages.text)
    pages_list = [x for x in pages_list if x.isdigit()]
    if len(pages_list) == 4:
        pages_list[2:4] = [''.join(pages_list[2:4])]
    pages_list = set(pages_list)
    if len(pages_list) == 3:
        return True
    else:
        return False


def get_company_info(driver):
    string_company_list, string_ratings_list, string_sector_list = [], [], []
    company = driver.find_elements(By.TAG_NAME, 'h2')
    del company[0]
    company_rating = driver.find_elements(By.TAG_NAME, 'b')
    company_rating_list = [e for e in company_rating if e.text[0].isdigit() or e.text == "N/A"]
    sector = driver.find_elements(By.CLASS_NAME, 'css-56kyx5')
    del sector[0:4]
    clean_sector_list = sector[::3]
    for index in range(len(clean_sector_list)):
        string_company_list.append(company[index].text)
        string_ratings_list.append(company_rating_list[index].text)
        string_sector_list.append(clean_sector_list[index].text)

    return string_company_list, string_ratings_list, string_sector_list


def get_company_df(driver, company_name, rating, sector):
    df_list, job_list, salary_list = [], [], []
    door = True
    while door:
        try:

            job_info = driver.find_elements(By.CLASS_NAME, 'css-1flyc9m')
            for salary_job in job_info:
                match = re.search('€/an$', salary_job.text)
                if match is not None:
                    salary_list.append(salary_job.text)
                else:
                    job_list.append(salary_job.text)

            salary_list = clean_salary(salary_list)

            for index in range(len(salary_list)):
                data = {'Empresa': company_name,
                        'Sector': sector,
                        'Salario': salary_list[index],
                        'Empleo': job_list[index],
                        'Rating': rating
                        }
                df_list.append(data)
            df = pd.DataFrame(df_list)
            door = False

            return df

        except StaleElementReferenceException:
            time.sleep(3)


def set_company_salary_page(driver, company_name, url):
    door1 = True
    while door1:
        try:

            driver.get(url)
            search = driver.find_element(By.ID, 'companyAutocomplete-companyDiscover-employerSearch')
            search_button = driver.find_element(By.CLASS_NAME, 'css-14xfqow')
            search.send_keys(company_name)
            search_button.click()
            door1 = False

        except NoSuchElementException:
            driver.refresh()
            time.sleep(10)

    time.sleep(2)
    variable_xpath = '//*[@id="MainCol"]/div/div[1]/div/div[2]/div/div[2]/a/span[1]'
    door2 = True
    tries = 0
    while door2:
        try:

            if tries == 3:
                door2 = False
                return tries
            else:
                salary_button = driver.find_element(By.XPATH, variable_xpath)
                salary_button.click()
                door2 = False
                return tries

        except NoSuchElementException:
            tries += 1
            variable_xpath = '//*[@id="EmpLinksWrapper"]/div[2]/div/div[1]/a[3]'


def set_page_to_get_companies_info(driver):
    time.sleep(5)
    points = driver.find_element(By.XPATH, '//*[@id="Explore"]/div[3]/div/div[4]/div[1]/div[1]/div/div[2]/div[5]/div[2]/div/div')
    points.click()
    time.sleep(5)
    points_selection = driver.find_element(By.XPATH, '//*[@id="option_4"]')
    points_selection.click()
    time.sleep(5)
    number_employees = driver.find_element(By.XPATH, '//*[@id="Explore"]/div[3]/div/div[4]/div[1]/div[1]/div/div[2]/div[6]/div[7]/div/label')
    number_employees.click()
    time.sleep(5)


if __name__ == '__main__':
    browser_driver = set_browser()
    page_url = "https://www.glassdoor.fr/Avis/index.htm"
    browser_driver.get(page_url)
    set_page_to_get_companies_info(browser_driver)
    company_list, rating_list, sector_list = [], [], []
    final_companies_list, final_ratings_list, final_sectors_list = [], [], []
    flag = True

    while flag:
        try:

            companies_names, companies_ratings, companies_sectors = get_company_info(browser_driver)
            company_list.append(companies_names)
            rating_list.append(companies_ratings)
            sector_list.append(companies_sectors)
            final_companies_list = reduce(lambda x, y: x + y, company_list)
            final_ratings_list = reduce(lambda x, y: x + y, rating_list)
            final_sectors_list = reduce(lambda x, y: x + y, sector_list)
            pages_num = browser_driver.find_element(By.XPATH, '//*[@id="Explore"]/div[3]/div/div[4]/div[1]/div[1]/div/div[1]/span/span')
            if check_pages_main_page(pages_num):
                continue_button = browser_driver.find_element(By.XPATH, '//*[@id="Explore"]/div[3]/div/div[4]/div[3]/div/div/div[1]/button[7]')
                continue_button.click()
                time.sleep(2)
            else:
                flag = False

        except IndexError:
            time.sleep(2)

    final_df_list = []

    for i in range(len(final_companies_list)):
        counter = set_company_salary_page(browser_driver, final_companies_list[i], page_url)
        time.sleep(2)
        if counter == 3:
            continue
        else:
            light = True
            dataframe_list = []
            while light:
                try:

                    dataframe = get_company_df(browser_driver, final_companies_list[i], final_ratings_list[i], final_sectors_list[i])
                    dataframe_list.append(dataframe)

                    try:

                        pages_num = browser_driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/main/div/div[3]/div/div[2]/span[1]')
                        if check_company_pages(pages_num):
                            continue_button = browser_driver.find_element(By.XPATH, '//*[@id="Container"]/div/div[2]/main/div/div[3]/div/div[1]/button[2]')
                            continue_button.click()
                            time.sleep(2)
                        else:
                            light = False
                            pre_dataframe = pd.concat(dataframe_list, ignore_index=True)
                            final_df_list.append(pre_dataframe)

                    except NoSuchElementException:
                        light = False

                except IndexError:
                    browser_driver.refresh()
                    time.sleep(10)

    final_df = pd.concat(final_df_list, ignore_index=True)
    final_df.to_csv('glassdoor_datasets(csv)/france_jobs_salaries_by_company.csv', index=False)
