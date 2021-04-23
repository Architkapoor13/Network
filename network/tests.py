from django.test import TestCase
import pathlib
import os
import unittest

from selenium import webdriver

def file_uri(filename):
    return pathlib.Path(os.path.abspath(filename)).as_uri()

driver = webdriver.Chrome("D:/chromedriver.exe")

# Create your tests here.

class WebpageTests(unittest.TestCase):

    def test_newpost(self):
        driver.get(file_uri("templates/network/index.html"))
        textarea = driver.find_element_by_id("post-textarea")
        textarea.send_keys("hello this is a new post!")
        submit = driver.find_element_by_id("post-submit")
        submit.click()
        self.assertEqual(driver.find_element_by_id("post-alerts").text, "new post posted!")


if __name__ == "__main__":
    unittest.main()