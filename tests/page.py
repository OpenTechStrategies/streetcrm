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
# See also http://selenium-python.readthedocs.io/page-objects.html
#
# To run this script, you should have Selenium and a Chrome webdriver
# installed.

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
import time

from element import BasePageElement
from locators import LoginPageLocators, MainPageLocators

class SearchTextElement(BasePageElement):
    """This class gets the search text from the specified locator"""

    #The locator for search box where search string is entered
    locator = 'q'

class UsernameElement(BasePageElement):
    """Why do I need a locator here when I have locators.py?"""

    #The locator for the username input
    locator = 'username'
    
class PasswordElement(BasePageElement):
    """Why do I need a locator here when I have locators.py?"""

    #The locator for the username input
    locator = 'password'

class BasePage(object):
    """Base class to initialize the base page that will be called from all pages"""

    def __init__(self, driver):
        self.driver = driver


class LoginPage(BasePage):
    """
    This is the only page visible when not logged in.  It is visible at /login.
    """

    username_element = UsernameElement()
    password_element = PasswordElement()
    
    def click_login(self):
        """ 
        Logs in the user given correct credentials.
        """
        submit_element = self.driver.find_element(*LoginPageLocators.LOGIN_BUTTON)
        submit_element.click()
        return MainPage(self.driver)

    def login_success(self):
        """
        Checks whether or not login was successful.  Returns true if it was and false if it was not.
        """
        return "<li>Home</li>" in self.driver.page_source

class MainPage(BasePage):
    """Home page action methods come here. I.e. Python.org"""

    #Declares a variable that will contain the retrieved text
    search_text_element = SearchTextElement()

    def click_go_button(self):
        """Triggers the search"""
        element = self.driver.find_element(*MainPageLocators.SEARCH_BUTTON)
        element.click()


class SearchResultsPage(BasePage):
    """Search results page action methods come here"""

    def is_results_found(self):
        # Probably should search for this text in the specific page
        # element, but as for now it works fine
        return "Sorry, there were no results for this search." not in self.driver.page_source
