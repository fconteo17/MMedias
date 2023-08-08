# -*- coding: utf-8 -*-
"""Modulo para resgatar as notas do MauaNet."""

import logging
import os
import sys

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium_recaptcha_solver import RecaptchaSolver
from selenium_recaptcha_solver.exceptions import RecaptchaException
from webdriver_manager.chrome import ChromeDriverManager

from util.solver import solve


def startup():
    """Inicia o driver do selenium e retorna o objeto.

    :return:
    """
    chrome_options = Options()
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--headless')
    # chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 4.0; WOW64) '
                     'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'})
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.maximize_window()
    return driver


def wait(driver, xpath):
    """Espera até que o elemento esteja visível na tela.

    :param driver:
    :param xpath:
    :return:
    """
    element = WebDriverWait(driver, 300).until(ec.element_to_be_clickable((By.XPATH, xpath)))
    return element


def click(driver, xpath):
    """Clica no elemento com o xpath passado.

    :param driver:
    :param xpath:
    :return:
    """
    btn = driver.find_element(By.XPATH, xpath)
    driver.execute_script("arguments[0].click();", btn)


def format_username(username):
    """Formata o username para o formato correto.

    :param username: str
    :return: str
    """
    if len(username) == 8:
        username = username[:2] + '.' + username[2:7] + '-' + username[7:] + '@maua.br'
    if len(username) == 10:
        username = username + '@maua.br'
    return username


def get_notas(login, password, tries=0):
    """Retorna as notas do MauaNet.

    :param login:
    :param password:
    :param tries:
    :return:
    """
    login = format_username(login)

    driver = startup()

    captcha_solver = RecaptchaSolver(driver)

    driver.get('https://www2.maua.br/mauanet.2.0')

    wait(driver, "//input[@id='maua_email']")

    logging.info("Logging in as: %s", login)

    username = driver.find_element(By.XPATH, "//input[@id='maua_email']")
    username.clear()
    username.send_keys(login)

    user_password = driver.find_element(By.XPATH, "//input[@id='maua_senha']")
    user_password.clear()
    user_password.send_keys(password)

    recaptcha_iframe = driver.find_element(
        By.XPATH, '//*[@id="form_mauanet_login"]/div/div/div/div/iframe'
    )

    try:
        captcha_solver.click_recaptcha_v2(iframe=recaptcha_iframe)
    except TimeoutException:
        logging.info("Captcha passou direto")
    except RecaptchaException:
        if tries >= 5:
            logging.error('Captcha Bloqueado, tente novamente mais tarde')
            sys.exit()
        tries += 1
        logging.warning('Captcha Bloqueado, tentando novamente...')
        get_notas(login, password, tries)

    click(driver, "//input[@id='maua_submit']")

    logging.info("Logged in as: %s", login)

    driver.get('https://www2.maua.br/mauanet.2.0/boletim-escolar')

    wait(driver, "//a[@class='provas']")

    notas_prova = get_prova(driver, [])

    click(driver, "//a[@class='trabalhos']")

    notas_trabalho = get_trabalho(driver, [])

    return solve(get_materias([notas_prova, notas_trabalho]))


def get_prova(driver, notas_prova):
    """Retorna as notas das provas.

    :param driver:
    :param notas_prova:
    :return:
    """
    for i, _row in enumerate(driver.find_elements(By.XPATH, '//*[@id="notas"]/tbody/tr')):
        materia_prova = [
            driver.find_element(
                By.XPATH, f'//*[@id="notas"]/tbody/tr[{i + 1}]/td[{1}]'
            ).text.split("-")[1].strip()
        ]
        for j in range(5, 11):
            nota = driver.find_element(By.XPATH, f'//*[@id="notas"]/tbody/tr[{i + 1}]/td[{j}]').text
            if nota not in ['', 'NC']:
                nota = (float(nota.replace(',', '.')))
            if nota == 'NC':
                nota = 0
            materia_prova.append(nota)
        notas_prova.append(materia_prova)
    return notas_prova


def get_trabalho(driver, notas_trabalho):
    """Retorna as notas dos trabalhos.

    :param driver:
    :param notas_trabalho:
    :return:
    """
    for i, _row in enumerate(driver.find_elements(By.XPATH, '//*[@id="notas"]/tbody/tr')):
        materia_trabalho = [
            driver.find_element(
                By.XPATH, f'//*[@id="notas"]/tbody/tr[{i + 1}]/td[{1}]'
            ).text.split("-")[1].strip()
        ]
        for j in range(12, 28):
            nota = driver.find_element(By.XPATH, f'//*[@id="notas"]/tbody/tr[{i + 1}]/td[{j}]').text
            if nota not in ['', 'NE']:
                nota = (float(nota.replace(',', '.')))
            if nota == 'NE':
                nota = 0
            materia_trabalho.append(nota)
        notas_trabalho.append(materia_trabalho)
    return notas_trabalho


def get_materias(notas_tipo):
    """Retorna as matérias.

    :param notas_tipo:
    :return:
    """
    notas_prova, notas_trabalho = notas_tipo
    materias = {}
    for materia in notas_prova:
        materias[materia[0]] = {
            'p1': materia[1],
            'p2': materia[2],
            'p3': materia[4],
            'p4': materia[5],
        }
    for materia in notas_trabalho:
        for i in range(1, 17):
            materias[materia[0]][f't{i}'] = materia[i]

    return materias


if __name__ == '__main__':
    load_dotenv()
    login_default = os.getenv("LOGIN")
    senha_default = os.getenv("SENHA")
    print(get_notas(login_default, senha_default))
