# This file comes from
# http://selenium-python.readthedocs.io/page-objects.html.
#

from selenium.webdriver.common.by import By

class LoginPageLocators(object):
    # StreetCRM's login button doesn't have an id.
    LOGIN_BUTTON = (By.XPATH, "//button[@type='submit']")

class MainPageLocators(object):
    """A class for main page locators. All main page locators should come here"""
    SEARCH_BUTTON = (By.ID, 'search-button')

class SearchResultsPageLocators(object):
    """A class for search results locators. All search results locators should come here"""
    pass

