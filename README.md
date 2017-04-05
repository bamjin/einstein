# **Einstein**[![einstein](https://img.shields.io/badge/telegram-einstein-blue.svg)](https://telegram.me/einstein_emotion_bot)

This is Telegram messenger BOT which analyse faces to detect a range of feelings from a photo that user sent. 

## **Installation**

+ install python packages
```bash
$ pip install telepot
```
 and, it will be needed to add your bot token in *settings.json* file
 You should create your bot with @Botfather in telgram.
 Then, you can get your token using  */token*  message.
 *For more details: http://telepot.readthedocs.io/en/latest/*

Now, we should install opencv into the server. There are various way to install, but I recommend to follow this website which I use, 
*http://cyaninfinite.com/tutorials/installing-opencv-in-ubuntu-for-python-3/* 
**Most error are occurred related with cv2 which is opencv python package.**


```bash
$ sudo apt-get install python3-numpy
$ sudo apt-get install python3-matplotlib
```
or
```bash
$ pip install numpy matplotlib
```
These are python packages to use opencv properly.
```bash
$ pip install apscheduler	# To run as background
```
+ Edit setting.json 
```json
{
  "common": {
    "token": "123456789:blahblahblahYourBotToken",
    "key": "abcdefghizklmnopqrstuvwxyzYourMS_Emotion_key"
    }
}
```
**YOU SHOULD CHANGE THE NAME setting_example.json FILE TO setting.json**

**token** is your bot token which you got when you make a new bot using *@Botfather*

**key** is your Emotion API key. You can get from *https://www.microsoft.com/cognitive-services/en-us/emotion-api*

## **Run**
```bash
$ python3 enstein.py
``` 