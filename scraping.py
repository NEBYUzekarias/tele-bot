
from selenium import webdriver
 
from selenium.webdriver.common.by import By
 
from selenium.webdriver.support.ui import WebDriverWait
 
from selenium.webdriver.support import expected_conditions as EC

def scrap(id):
    # 271658
    # browser = webdriver.PhantomJS()
    browser = webdriver.Chrome('/home/neba/Downloads/chromedriver')      
    browser.get("http://twelve.neaea.gov.et/")
    user =browser.find_element_by_id("Registration_Number")  
    user.send_keys("" + id) 
    browser.find_element_by_id("Registration_Number").send_keys(u'\ue007') 
    res = browser.find_element_by_tag_name("table")
    return res.text