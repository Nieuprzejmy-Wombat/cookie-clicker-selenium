from itertools import takewhile
from string import ascii_letters

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from util import find


class Buyable:
    def __init__(self, elem: WebElement):
        self.elem = elem
        self.id = int(elem.get_attribute("id").lstrip(ascii_letters))

    def __str__(self):
        return f"id: {self.id}"

    def __repr__(self):
        return str(self)

    def is_enabled(self) -> bool:
        return "enabled" in self.elem.get_attribute("class")

    def is_unlocked(self) -> bool:
        return "unlocked" in self.elem.get_attribute("class")

    def buy(self) -> None:
        self.elem.click()


class Product(Buyable):
    @property
    def owned(self) -> int:
        inner = self.elem.find_element(By.ID, f"productOwned{self.id}").get_attribute("innerHTML")
        return int(inner) if inner else 0


class CookieClicker:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        wait = WebDriverWait(driver, 10)
        driver.get("https://orteil.dashnet.org/cookieclicker/")

        # get rid of the cookie consent banner
        wait.until(ec.element_to_be_clickable(
            (By.CLASS_NAME, "fc-cta-consent"))).click()

        wait.until(ec.element_to_be_clickable((By.ID, "langSelect-PL"))).click()

        wait.until(ec.invisibility_of_element((By.ID, "loader")))
        self.cookie_btn = wait.until(ec.element_to_be_clickable((By.ID, "bigCookie")))
        self.products = [Product(p) for p in driver.find_elements(By.CLASS_NAME, "product")]

    def step(self) -> None:
        # constant clicking makes using the UI annoying
        # disable it after buying first grandma
        if not self.products[1].owned:
            self.cookie_btn.click()

        # try to buy the first upgrade
        try:
            Buyable(self.driver.find_element(By.ID, "upgrade0")).buy()
        except NoSuchElementException:
            pass

        # buy the last product we can afford and we own less than 10 of
        unlocked = list(takewhile(lambda x: x.is_unlocked(), self.products))
        find(lambda p: p.is_enabled() and p.owned < 10, reversed(unlocked)).map(lambda x: x.buy())


if __name__ == "__main__":
    with webdriver.Firefox() as driver:
        cc = CookieClicker(driver)
        while True:
            cc.step()
