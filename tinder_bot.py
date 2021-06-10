from selenium import webdriver
from time import sleep
import re
import requests
import shutil
from datetime import datetime

import cv2
import dlib
import torch
import argparse
import torchvision
import numpy as np
import torch.nn as nn
from skimage.transform import resize

from secrets import email, password
from strings import *

class TinderBot():
    def __init__(self):
        self.options = webdriver.FirefoxOptions()
        self.options.set_preference("dom.webnotifications.enabled", False)
        self.options.set_preference("geo.enabled", True)
        self.options.set_preference("geo.provider.use_corelocation", True)
        self.options.set_preference("geo.prompt.testing", True)
        self.options.set_preference("geo.prompt.testing.allow", True)
        self.driver = webdriver.Firefox(executable_path= r"./geckodriver", options=self.options)

    def exists(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
            return True
        except:
            return False

    def clickBtn(self, xpath):
        try:
            btn = self.driver.find_element_by_xpath(xpath)
            btn.click()
        except:
            print("Button NOT FOUND == " + xpath)

    def enterField(self, xpath, text):
        try:
            field = self.driver.find_element_by_xpath(xpath)
            field.send_keys(text)
        except:
            print("Entry Field NOT FOUND == " + xpath + " Text: " + text)

    def getProfileImage(self, xpath):
        if self.exists(xpath):
            profileImage = self.driver.find_element_by_xpath(profileImageDiv)
            style = profileImage.get_attribute("style")
            m = re.match('background-image: url\("(.+?)"\)', style)
            if m:
                imageUrl = m.group(1)
                
                r = requests.get(imageUrl, stream = True)
                if r.status_code == 200:
                    r.raw.decode_content = True

                    filename = './photos/' + datetime.now().strftime("%d-%m-%Y%-H:%M:%S.jpg")

                    with open(filename, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)

                    return filename
        return ""




    def login(self):
        self.driver.get('https://tinder.com')

        sleep(2)

        self.clickBtn(loginBtn)

        sleep(2)
        
        self.clickBtn(facebookOptionBtn)

        sleep(2)

        base_window = self.driver.window_handles[0]
        fb_popup = self.driver.switch_to.window(bot.driver.window_handles[1])

        self.enterField(fbEmailEntryField, email)
        self.enterField(fbPasswordEntryField, password)
        self.clickBtn(fbLoginBtn)

        self.driver.switch_to.window(base_window)

        sleep(2)

    def setup(self):
        self.clickBtn(allowSomething1Btn)
        self.clickBtn(allowSomething2Btn)
        self.clickBtn(allowSomething3Btn)

        sleep(2)

    def swipRight(self):
        self.clickBtn(swipRightBtn)

    def swipLeft(self):
        self.clickBtn(swipLeftBtn)

    def swipRightAll(self):
        while True:
            sleep(1)
            if self.exists(closeMatchBtn):
                self.closeMatch()
            elif self.exists(premiumBtn):
                self.clickBtn(premiumBtn)
                break
            else:
                rating = self.rateProfile()
                if rating > 4.3:
                    print("SWIPING right with rating of " + str(rating))
                    self.swipRight()
                else:
                    print("SWIPING left with rating of " + str(rating))
                    self.swipLeft()

    def closeMatch(self):
        self.clickBtn(closeMatchBtn)

    def rateProfile(self):
        img = self.getProfileImage(profileImageDiv)
        if img != "":
            try:
                return ratePhoto(img, modelPath)
            except:
                return -1
        return -1

    def sendMessage(self):
        #//*[@id="c-1465866392"]
        print('NEED to implement')


def ratePhoto(image_path, model_path):
    use_cuda = torch.cuda.is_available()
    model = torchvision.models.resnet18()
    model.fc = nn.Linear(in_features=512, out_features=1, bias=True)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    if use_cuda:
        model = model.cuda()
    FloatTensor = torch.cuda.FloatTensor if use_cuda else torch.FloatTensor
    detector = dlib.get_frontal_face_detector()
    image = cv2.imread(image_path)
    b, g, r = cv2.split(image)
    image_rgb = cv2.merge([r, g, b])
    rects = detector(image_rgb, 1)
    if len(rects) >= 1:
        rating = 0
        for rect in rects:
            lefttop_x = rect.left()
            lefttop_y = rect.top()
            rightbottom_x = rect.right()
            rightbottom_y = rect.bottom()
            face = image_rgb[lefttop_y: rightbottom_y, lefttop_x: rightbottom_x] / 255.
            face = resize(face, (224, 224, 3), mode='reflect')
            face = np.transpose(face, (2, 0, 1))
            face = torch.from_numpy(face).float().resize_(1, 3, 224, 224)
            face = face.type(FloatTensor)
            rating += round(model(face).item(), 2)
        return rating / len(rects)
    print('ERROR while rating photo: ' + image_path + ' using model: ' + model_path)
    return -1

bot = TinderBot()
bot.login()
bot.setup()
bot.swipRightAll()




