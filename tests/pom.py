# Selenium recommends separating the "page object model" (POM) from the
# tests.  This allows us to change just one class if the UI changes,
# instead of changing all the tests that touch that page
# (https://seleniumhq.github.io/docs/best.html).
#
# This means that classes and methods in the POM should not themselves
# be tests.  For example, read_search_results() should just retrieve the
# results from the page.  A different function will compare those
# results to the ones expected in the sample data.
#
# To run this script, you should have Selenium and a Chrome webdriver
# installed.

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
import time

class StreetcrmLogin():

    def start_app(self, url):
        driver = webdriver.Chrome()
        driver.get(url)
        # TODO: return false if this fails
        return
    

    def login_routine(self, url, username, password):
        """
        Log into an instance of StreetCRM using the credentials supplied in main().
        """
        usernameElement = driver.find_element_by_id("id_username")
        passwordElement = driver.find_element_by_id("id_password")
        
        usernameElement.send_keys(username)
        passwordElement.send_keys(password)
        
        # will this submit the form?
        usernameElement.submit()

        # should return true if login was successful and false otherwise
        return

class BasicSearch():
    def do_basic_search(self, driver, keyword):
        """
        Complete a basic search for the KEYWORD from the search bar at the
        top right.
        """
        searchbarElement = driver.find_element_by_name("q")
        searchbarElement.send_keys(keyword)
        searchbarElement.submit()
        return
    
    def read_search_results(self, driver):
        """
        Return the list of search results for KEYWORD.
        """
        return

    

