import os
import time

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
    chrome_options = Options()
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--headless')
    # chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=chrome_options)
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'})
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.maximize_window()
    return driver


def wait(driver, xpath):
    element = WebDriverWait(driver, 300).until(ec.element_to_be_clickable((By.XPATH, xpath)))
    return element


def click(driver, xpath):
    btn = driver.find_element(By.XPATH, xpath)
    driver.execute_script("arguments[0].click();", btn)


def get_notas(login, password):
    if len(login) == 8:
        login = login[:2] + '.' + login[2:7] + '-' + login[7:] + '@maua.br'
    if len(login) == 10:
        login = login + '@maua.br'

    driver = startup()

    captch_solver = RecaptchaSolver(driver)

    driver.get('https://www2.maua.br/mauanet.2.0')

    wait(driver, "//input[@id='maua_email']")

    print("Logging in")

    username = driver.find_element(By.XPATH, "//input[@id='maua_email']")
    username.clear()
    username.send_keys(login)

    user_password = driver.find_element(By.XPATH, "//input[@id='maua_senha']")
    user_password.clear()
    user_password.send_keys(password)

    recaptcha_iframe = driver.find_element(By.XPATH, '//*[@id="form_mauanet_login"]/div/div/div/div/iframe')

    try:
        captch_solver.click_recaptcha_v2(iframe=recaptcha_iframe)
    except TimeoutException:
        print("Captcha passou direto")
    except RecaptchaException:
        print('Google ta boicotando, tentando novamente...')
        time.sleep(5)
        get_notas(login, password)

    click(driver, "//input[@id='maua_submit']")

    print("Logged in")

    driver.get('https://www2.maua.br/mauanet.2.0/boletim-escolar')

    wait(driver, "//a[@class='provas']")

    notas_prova = []
    notas_trabalho = []

    for i, row in enumerate(driver.find_elements(By.XPATH, '//*[@id="notas"]/tbody/tr')):
        materia_prova = [
            driver.find_element(By.XPATH, f'//*[@id="notas"]/tbody/tr[{i + 1}]/td[{1}]').text.split("-")[1].strip()
        ]
        for j in range(5, 11):
            nota = driver.find_element(By.XPATH, f'//*[@id="notas"]/tbody/tr[{i + 1}]/td[{j}]').text
            if nota not in ['', 'NC']:
                nota = (float(nota.replace(',', '.')))
            materia_prova.append(nota)
        notas_prova.append(materia_prova)

    click(driver, "//a[@class='trabalhos']")

    for i, row in enumerate(driver.find_elements(By.XPATH, '//*[@id="notas"]/tbody/tr')):
        materia_trabalho = [
            driver.find_element(By.XPATH, f'//*[@id="notas"]/tbody/tr[{i + 1}]/td[{1}]').text.split("-")[1].strip()
        ]
        for j in range(12, 20):
            nota = driver.find_element(By.XPATH, f'//*[@id="notas"]/tbody/tr[{i + 1}]/td[{j}]').text
            if nota not in ['', 'NE']:
                nota = (float(nota.replace(',', '.')))
            materia_trabalho.append(nota)
        notas_trabalho.append(materia_trabalho)

    n = [notas_prova, notas_trabalho]
    return solve(get_materias(n))


def get_materias(notas_tipo):
    notas_prova = notas_tipo[0]
    notas_trabalho = notas_tipo[1]
    materias = {}
    for materia in notas_prova:
        materias[materia[0]] = {
            'P1': materia[1],
            'P2': materia[2],
            'P3': materia[3],
            'P4': materia[4],
        }
    for materia in notas_trabalho:
        materias[materia[0]]['T1'] = materia[1]
        materias[materia[0]]['T2'] = materia[2]
        materias[materia[0]]['T3'] = materia[3]
        materias[materia[0]]['T4'] = materia[4]
        materias[materia[0]]['T5'] = materia[5]
        materias[materia[0]]['T6'] = materia[6]
        materias[materia[0]]['T7'] = materia[7]
        materias[materia[0]]['T8'] = materia[8]
    return materias


if __name__ == '__main__':
    load_dotenv()
    login = os.getenv("LOGIN")
    senha = os.getenv("SENHA")
    print(get_notas(login, senha))
