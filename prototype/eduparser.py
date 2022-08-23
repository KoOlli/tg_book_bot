from time import sleep
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


def get_user_info(username: str, password: str):
    # Добавляем аргумент на отсутствие GUI
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    # Создаём драйвер гугла
    driver = webdriver.Chrome(options=options)

    def parse_info(source_code: str, username: str):
        result = {"username": username}
        if "Novosibirsk" in source_code:
            city = 1
        elif "Moscow" in source_code:
            city = 0
        elif "Kazan" in source_code:
            city = 2
        else:
            city = "чёё"
        result["city"] = city
        if "Core program" in source_code:
            result["role"] = 111
        elif "Survival" in source_code:
            result["role"] = 000
        else:
            result["role"] = 999
        return result

    # Логинимся под юзером на платформу
    username = username.lower()
    driver.get("https://edu.21-school.ru/")
    login = driver.find_element(by=By.NAME, value="username")
    login.send_keys(f"{username}@student.21-school.ru")
    passwd = driver.find_element(by=By.NAME, value="password")
    passwd.send_keys(password)
    passwd.send_keys(Keys.ENTER)

    # Ждём пока платформа подгрузится
    sleep(6)
    result = None
    if driver.current_url == "https://edu.21-school.ru/":
        result = parse_info(driver.page_source, username)
    return result


def main():
    username = input("Username: ")
    password = getpass()

    print(get_user_info(username, password))


if __name__ == "__main__":
    main()
