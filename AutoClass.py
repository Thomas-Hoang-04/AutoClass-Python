import os, numbers, sys, re
from time import sleep
from hashlib import sha3_512 as SHA512, sha3_256 as SHA256
from stat import S_IRUSR, S_IRWXU
from base64 import b64encode as b_enc, b64decode as b_dec
from pwinput import pwinput
from Crypto.Cipher import AES
from pynput.keyboard import Key, Controller as KB
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from twocaptcha import TwoCaptcha

exe_file = sys.executable
exe_parent = os.path.dirname(exe_file)
dotenv_path = os.path.join(exe_parent, ".env")
load_dotenv(dotenv_path=dotenv_path)

url = os.environ["TEST_URL"]

solver = TwoCaptcha(apiKey=os.environ["API_KEY"])

keyboard = KB()

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
options.add_experimental_option("excludeSwitches", ["enable-logging"])


class UserManagement:
    def __init__(self) -> None:
        self.counter = 1

    def NewUserVerify(self):
        try:
            with open("ENCRYPT_KEY.bin", "rb") as f_key:
                index = f_key.readlines()
                f_key.close()
            if len(index) == 1:
                with open("USER_DATA.bin", "x") as f_usr:
                    f_usr.close()
                os.chmod("USER_DATA.bin", S_IRUSR)
                return True
            elif len(index) != 2:
                os.remove(".env")
                os.remove("ENCRYPT_KEY.bin")
                print("\n--Lỗi an ninh nghiêm trọng--")
                print("--Vui lòng liên hệ nhà phát hành để khắc phục--")
                print("\n--Đang tự hủy chương trình--")
                return "F"
        except:
            return False

    def createUser(self):
        print("\n--Cảm ơn bạn đã tin dùng dịch vụ của AutoClass--")
        print("Mời bạn đăng ký thông tin của mình dưới đây\n")
        name = input("Họ và tên: ")
        self.getUser()
        key_check = self.ActivationKeyVerify()
        while not key_check:
            key_check = self.ActivationKeyVerify()
        if key_check == "F":
            return key_check
        else:
            sleep(1)
            print("\n--Đang xử lý thông tin--")
            str_key = self.id + self.key
            AES_key = SHA256(bytes(str_key, "utf-8")).digest()
            os.chmod("ENCRYPT_KEY.bin", S_IRWXU)
            with open("ENCRYPT_KEY.bin", "ab") as fb:
                fb.writelines(
                    [
                        b"\n",
                        b_enc(AES_key),
                    ]
                )
                fb.close()
            os.chmod("ENCRYPT_KEY.bin", S_IRUSR)
            raw_data = "-".join((self.id, self.pwd))
            cipher = AES.new(AES_key, AES.MODE_GCM)
            enc_data, tag = cipher.encrypt_and_digest(bytes(raw_data, "utf-8"))
            os.chmod("USER_DATA.bin", S_IRWXU)
            with open("USER_DATA.bin", "ab") as f_usr:
                f_usr.writelines(
                    [
                        b_enc(bytes(name, "utf-8")),
                        b"\n",
                        b_enc(cipher.nonce),
                        b"\n",
                        b_enc(tag),
                        b"\n",
                        b_enc(enc_data),
                    ]
                )
                f_usr.close()
            os.chmod("USER_DATA.bin", S_IRUSR)
            sleep(2)
            print("\n--Đăng ký thông tin người dùng thành công--")
            sleep(0.5)
            print("\n", end="")
            for i in range(len("--- Xin chào, {} ---\n".format(name))):
                print("-", end="")
            print("\n--- Xin chào, {} ---".format(name))
            for i in range(len("--- Xin chào, {} ---\n".format(name))):
                print("-", end="")
            print("\n", end="")
            sleep(0.75)
            n = input("\nNhấn Enter để bắt đầu đăng ký lớp\n")
            if not n:
                classID = getClasses()
                return classID

    def getUser(self):
        id = input("Mã số sinh viên HUST: ")
        pwd = pwinput("Mật khẩu tài khoản SIS-HUST: ")
        if (
            not isinstance(int(id), numbers.Number)
            or len(id) != 8
            or re.search("^20", id) == None
        ):
            print("\n--Sai định dạng mã số sinh viên--")
            n = input("Vui lòng ấn Enter để thử lại")
            if not n:
                print("\n", end="")
                sleep(1)
                self.getUser()
        elif len(pwd) == 0 or pwd == None:
            print("\n--Mật khẩu quá ngắn hoặc không hợp lệ--")
            n = input("Vui lòng ấn Enter để thử lại")
            if not n:
                print("\n", end="")
                sleep(1)
                self.getUser()
        else:
            self.id = id
            self.pwd = pwd

    def ActivationKeyVerify(self):
        print("\n", end="")
        key = pwinput("Nhập mã kích hoạt phần mềm: ")
        key_hash = SHA512(bytes(key, "utf-8")).digest()
        with open("ENCRYPT_KEY.bin", "rb") as fb:
            key_data = b_dec(b_dec(fb.readlines()[0]))
            fb.close()
        sleep(2)
        if key_hash != key_data:
            print("\n--Mã kích hoạt không chính xác--")
            print("\n--Bạn còn {} lần thử--".format(5 - self.counter))
            if self.counter == 5:
                print("\n--Bạn đã thử kích hoạt quá số lần cho phép--")
                print("Chương trình sẽ tự hủy sau 5 giây")
                sleep(5)
                return "F"
            else:
                self.counter += 1
                n = input("Vui lòng ấn Enter để thử lại")
                if not n:
                    print("\n", end="")
                    sleep(1)
                    return
        else:
            sleep(2)
            print("--Xác nhận mã kích hoạt thành công--")
            self.key = key
            return "C"


class AutoClass:
    def __init__(self, usr_ID, usr_pass, classID, driver) -> None:
        self.usr_ID = usr_ID
        self.usr_pass = usr_pass
        self.classID = classID
        self.driver = driver

    def captcha_solver(self):
        print("\n--Dang giải Captcha--")
        try:
            capt = self.driver.find_element(By.ID, "ccCaptcha_IMG")
            capt.screenshot("./image.png")
            sleep(0.75)
            id = solver.send(file="./image.png")
            sleep(7)
            code = solver.get_result(id)
            if not isinstance(int(code), numbers.Number):
                raise TypeError("Inaccurate Captcha format")
            else:
                inp_capt = self.driver.find_element(By.ID, "ccCaptcha_TB_I")
                inp_capt.send_keys(code)
                print("\n--Giải Captcha thành công--")
                os.remove("./image.png")
                sleep(0.5)
        except:
            print(
                "\n--Giải Captcha không thành công. Đang khởi động lại quá trình đăng ký--"
            )
            print("---AutoClass xin lỗi vì sự bất tiện này---")
            os.remove("./image.png")
            self.driver.quit()
            return "capt_err"

    def login(self):
        print("\n--Đang đăng nhập--")
        try:
            usr = self.driver.find_element(By.ID, "tbUserName")
            usr.click()
            usr.send_keys(self.usr_ID)
            sleep(0.5)
            keyboard.press(Key.tab)
            keyboard.type(self.usr_pass)
            sleep(0.5)
            login_btn = self.driver.find_element(By.NAME, "submit")
            login_btn.click()
            sleep(0.75)
        except:
            print("\n--Đăng nhập thất bại. Vui lòng thử lại--")
            return "err"

    def register(self):
        try:
            for i in range(len(self.classID)):
                classID = self.driver.find_element(By.ID, os.environ["INP_ID"])
                confirm = self.driver.find_element(By.ID, os.environ["BTN_ID_1"])
                classID.click()
                classID.send_keys(self.classID[i])
                sleep(0.25)
                confirm.click()
                sleep(0.4)
            send = self.driver.find_element(By.ID, os.environ["BTN_ID_2"])
            send.click()
            sleep(0.3)
            confirm = self.driver.find_element(By.ID, os.environ["BTN_ID_3"])
            confirm.click()
            sleep(1)
            print("\n--Đăng ký các mã lớp thành công--")
            print("--Vui lòng kiểm tra lại danh sách lớp đã đăng kí--")
            n = input(
                "\n--Nhấn Enter để xác thực thông tin và kết thúc quá trình đăng ký--"
            )
            if not n:
                print("\n--AutoClass cảm ơn quý khách đã sử dụng dịch vụ--")
                return "C"
        except:
            print("\n--Đăng ký các mã lớp thất bại. Vui lòng thử lại sau 15 phút--")
            print("---AutoClass xin lỗi vì sự bất tiện này---\n")
            return "reg_err"


def WelcomeMenu():
    print("AutoClass - Đăng ký lớp học tự động cho sinh viên HUST")
    curr_usr = UserManagement()
    new_usr_check = curr_usr.NewUserVerify()
    if new_usr_check:
        sleep(1)
        return curr_usr.createUser()
    elif new_usr_check == "F":
        return new_usr_check
    else:
        with open("USER_DATA.bin", "rb") as f_usr:
            data = f_usr.readlines()
            name = b_dec(data[0])
            f_usr.close()
        sleep(1.5)
        print("\n", end="")
        for i in range(len("--- Xin chào, {} ---\n".format(name.decode("utf-8")))):
            print("-", end="")
        print("\n--- Xin chào, {} ---".format(name.decode("utf-8")))
        for i in range(len("---  Xin chào, {} ---\n".format(name.decode("utf-8")))):
            print("-", end="")
        print("\n", end="")
        sleep(0.75)
        n = input("\nNhấn Enter để bắt đầu đăng ký lớp\n")
        if not n:
            classID = getClasses()
            return classID


def getClasses():
    classes = input("Nhập vào số lớp mà bạn muốn đăng ký: ")
    while not classes or not isinstance(int(classes), numbers.Number):
        print("\n--Số lượng lớp không hợp lệ--")
        n = input("--Vui lòng nhấn Enter để thử lại--")
        if not n:
            print("\n", end="")
            classes = input("Nhập vào số lớp mà bạn muốn đăng ký: ")
    classID = list()
    for i in range(int(classes)):
        c_ID = input("Nhập mã lớp thứ {}: ".format(i + 1))
        while not isinstance(int(c_ID), numbers.Number) or len(c_ID) != 6:
            print("\n--Mã lớp không hợp lệ. Vui lòng nhập lại--\n")
            c_ID = input("Nhập mã lớp thứ {}: ".format(i + 1))
        classID.append(c_ID)
    return classID


def main(classID):
    with open("USER_DATA.bin", "rb") as f_usr:
        data = f_usr.readlines()
        nonce = b_dec(data[1])
        usr = b_dec(data[3])
        tag = b_dec(data[2])
        f_usr.close()

    with open("ENCRYPT_KEY.bin", "rb") as f_key:
        key = b_dec(f_key.readlines()[1])
        f_key.close()

    try:
        cipher = AES.new(key, AES.MODE_GCM, nonce)
        dec_data = cipher.decrypt_and_verify(usr, tag)
        usr_ID, usr_pass = tuple(dec_data.decode("utf-8").split("-"))
        sleep(1)
        print("\nĐang khởi động quá trình đăng ký...")
        sleep(0.5)
        driver = webdriver.Chrome(
            options=options, service=Service(ChromeDriverManager().install())
        )
        driver.get(url)
        sleep(1.25)
        driver.refresh()
        sleep(1)
        controller = AutoClass(usr_ID, usr_pass, classID, driver)
        captcha = controller.captcha_solver()
        if captcha == "capt_err":
            return
        else:
            login_result = controller.login()
            if login_result == "err":
                n = input("--Vui lòng nhấn Enter để thử lại--")
                if not n:
                    print("\n", end="")
                    return
            if driver.current_url == os.environ["TEST_URL"]:
                try:
                    print("\n--Đã có lỗi xảy ra--\n")
                    err_note = driver.find_element(By.ID, "lbStatus")
                    if err_note.text == "Mật khẩu hoặc tài khoản không đúng.":
                        print(err_note.text)
                        raise ValueError("Critical Failure")
                    else:
                        print("Thông báo từ hệ thống:", end=" ")
                        print(err_note.text)
                        print("\n", end="")
                        n = input(
                            "Nhấn bất kì phím nào để thử lại hoặc nhập 'q' hoặc 'Q' để thoát chương trình: "
                        )
                        if n.lower() != "q":
                            return
                        else:
                            print("\n--AutoClass cảm ơn quý khách đã sử dụng dịch vụ--")
                            print("--Chương trình sẽ tự thoát sau 5 giây--")
                            return "E"
                except ValueError:
                    print(
                        "\n---Thông tin người dùng được lưu trữ không còn đáng tin cậy---"
                    )
                    print("--Vui lòng liên hệ nhà phát hành để khắc phục--")
                    return "E"
                except:
                    print("Unknown Error")
                finally:
                    sleep(2)
                    driver.quit()
            else:
                driver.refresh()
                try:
                    elem = WebDriverWait(driver=driver, timeout=3600, poll_frequency=1)
                    elem.until(
                        EC.element_to_be_clickable((By.ID, os.environ["INP_ID"]))
                    )
                    sleep(1)
                    reg_result = controller.register()
                    if reg_result == "reg_err" or reg_result == "C":
                        return "E"
                except:
                    print("--Có lỗi xảy ra. Đang khởi động lại quá trình đăng ký--")
                    return
    except ValueError:
        print("\n---Thông tin người dùng được lưu trữ không còn đáng tin cậy---")
        print("--Vui lòng liên hệ nhà phát hành để khắc phục--")
        return "E"


if __name__ == "__main__":
    classID = WelcomeMenu()
    if classID == "F":
        os.chmod("USER_DATA.bin", S_IRWXU)
        os.remove("USER_DATA.bin")
        try:
            os.startfile("self_destruct.exe")
            sys.exit(0)
        except:
            pass
        finally:
            sys.exit(0)
    else:
        app = main(classID)
        while not app:
            app = main(classID)
        if app == "E":
            print("\n--Đang thoát khỏi chương trình--")
            sleep(4)
            sys.exit(0)
