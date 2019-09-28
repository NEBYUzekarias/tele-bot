
from selenium import webdriver
 
from selenium.webdriver.common.by import By
 
from selenium.webdriver.support.ui import WebDriverWait
 
from selenium.webdriver.support import expected_conditions as EC
import time 


def scrap():
    start_time = time.time()
    id =  317857
    for i in range(1, 4):
        browser = webdriver.PhantomJS('/Users/apple/Downloads/phantomjs')
        # browser = webdriver.Chrome('/Users/apple/Downloads/chromedriver')      
        browser.get("http://portal.neaea.gov.et/Home/Student")
        user =browser.find_element_by_id("AdmissionNumber")  
        user.send_keys(id) 
        browser.find_element_by_id("AdmissionNumber").send_keys(u'\ue007') 
        bla= browser.find_element_by_id("StudentDetail")
        bla.find_element_by_tag_name("button").send_keys(u'\ue007')
        litsofun = browser.find_element_by_id("StudentInstituteChoice")
        id +=1

    # browser.find_element_
    # res = browser.find_element_by_tag_name("table")
    # browser.close()
    return print("--- %s seconds ---" % (time.time() - start_time))

scrap()