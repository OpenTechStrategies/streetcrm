# Based on
# http://selenium-python.readthedocs.io/page-objects.html#test-case.

import unittest
from selenium import webdriver
import page

class BasicSearch(unittest.TestCase):
    """A test class to check whether search works in StreetCRM """

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000")

    def test_login(self):
        login_page = page.LoginPage(self.driver)
        login_page.username_element = "admin"
        login_page.password_element = "password"
        login_page.click_login()
        assert login_page.login_success(), True
        
    #def test_basic_search(self):
        """
        Tests StreetCRM's basic search feature. Searches for the character
        "G" and verifies that some results show up.  Note that it does
        not look for any particular text in search results page. This
        test verifies that the results were not empty.
        """
        
        # Load the main page. 
        #main_page = page.MainPage(self.driver)
        # Sets the text of search textbox to "pycon"
        #main_page.search_text_element = "G"
        #main_page.click_go_button()
        #search_results_page = page.SearchResultsPage(self.driver)
        # Verifies that the results page is not empty
        # I don't understand this line.
        #assert search_results_page.is_results_found(), "Sorry, there were no results for this search."

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
