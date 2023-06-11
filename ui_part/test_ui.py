import json
import time
import pytest
from requests import Response
from selene import have, be
from selene.core import command
from selene.support.shared import browser
import allure
from allure_commons.types import Severity
from allure import step
import requests

from models.ui_model import UserMessage
from ui_part.conftest import setup_browser
from ui_part.pages.message_page import MessagePage


def test_send_message(setup_browser):
    message_page = MessagePage()

    user_data = UserMessage.message_data()
    user = UserMessage(name=user_data.get("name"),
                       email=user_data.get("email"),
                       phone=user_data.get("phone"),
                       subject=user_data.get("subject"),
                       message=user_data.get("message"))

    message_page.open(setup_browser)

    message_page.fill_message_form(user=user)

    message_page.assert_reply_with_data(name=user.name, subject=user.subject)


def test_admin_create_rooms(setup_browser):
    with step("Open Admin panel"):
        browser = setup_browser
        browser.open("/#/admin")
        time.sleep(3)

    with step("Login to Admin panel"):
        browser.element('#username').should(be.visible).type('admin')
        browser.element('#password').should(be.visible).type('password')
        browser.element('#doLogin').click()
        time.sleep(5)

    with step("Remove preset room"):
        browser.element('.fa.fa-remove.roomDelete').click()

    with step("Create room"):
        browser.element('#roomName').should(be.visible).type(102)
        browser.element('#type').click()
        type = "Twin"
        browser.element(f'[value = {type}]').should(
            be.visible).click()  # Single, Twin, Double, Family, Suite
        browser.element('#accessible').click()
        browser.element('[value = "true"]').should(be.visible).click()  # false
        browser.element('#roomPrice').type(200)
        browser.element('#wifiCheckbox').click()
        browser.element('#refreshCheckbox').click()
        browser.element('#safeCheckbox').click()
        browser.element('#viewsCheckbox').click()
        browser.element('#createRoom').should(be.visible).click()

        time.sleep(5)
    with step("Check created room"):
        browser.element('#frontPageLink').click()
        time.sleep(5)
        browser.element('.col-sm-7').perform(command.js.scroll_into_view)
        browser.all('.col-sm-7').should(have.texts(
            'Twin\nPlease enter a description for this room\nWiFi\nRefreshments\nSafe\nViews\nBook this room'))
        time.sleep(5)


def test_open_browser_with_cookie(setup_browser):
    # Данные для HTTP-запроса
    url = "https://restful-booker.herokuapp.com/auth"
    headers = {"Content-Type": "application/json",
               "Accept": "application/json",
               'Authorization': 'Basic YWRtaW46cGFzc3dvcmQxMjM='
               }

    payload = {
        "username": "admin",
        "password": "password123"
    }
    data = json.dumps(payload)
    # Отправить HTTP-запрос для открытия страницы
    response: Response = requests.post(url, headers=headers, data=data)
    assert response.status_code == 200

    token = response.json()['token']
    print("ЭТО ТОКЕН", token)
    #
    browser.open("/#/admin")
    browser.driver.add_cookie({"name": "token", "value": token})
    browser.open("/#/admin")
    time.sleep(3)

    # Открыть страницу в браузере Selene
    # browser.driver().get(url)
    browser.element('.col-sm-10').perform(command.js.scroll_into_view)
    browser.element('.col-sm-10').should(have.text(
        'Welcome to Shady Meadows, a delightful Bed & Breakfast nestled in the hills on Newingtonfordburyshire. A place so beautiful you will never want to leave. All our rooms have comfortable beds and we provide breakfast from the locally sourced supermarket. It is a delightful place.'))
    time.sleep(3)
