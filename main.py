import requests
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from datetime import datetime

# 
# Written By Rafaq, me@rafaq.ca
# 

###################################
CCID = "CCID"
CCPass = "CCPASS"
UofAID = "UOFAID"
email = CCID + "@ualberta.ca"
log_attempts = 1
###################################

r = requests.Session()

#The login process requires 3 POST requests which are injected using the requests library via `payload` with fabricated headers
#Hidden input values are extracted through BeautifulSoup for some POST requests
#BeautifulSoup parses everything after to get watchlist data

#Watchlist variable set for Winter 2018 semester

headers = {
    "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
}
url = "https://www.beartracks.ualberta.ca/uahebprd/signon.html"

pull = r.get(url, headers=headers)

bs = BeautifulSoup(pull.text, "html.parser")
aState = bs.input["value"] 

payload = {
    "username": CCID,
    "password": CCPass,
    "AuthState": aState,
    "raa": "continue"
}


pull = r.post(pull.url, data=payload, headers=headers)

if(pull.status_code != 200):
    quit("Error at inital login step")

#inital post completed and now we should have some cookies to use
cookies = pull.cookies

action = "https://www.beartracks.ualberta.ca/simplesaml/module.php/saml/sp/saml2-acs.php/spprodbt"
bs = BeautifulSoup(pull.text, "html.parser")
param = list()

for input in bs.find_all("input"):
    param.append(input.get("value"))

payload = {
    "SAMLResponse": param[1],
    "RelayState": param[2]
}

pull = r.post(action, data=payload, headers=headers, cookies=cookies)

if(pull.status_code != 200):
    quit("Error at SAMLResponse step, this usually means you entered the wrong user credentials")

action = "https://www.beartracks.ualberta.ca/psp/uahebprd/EMPLOYEE/HRMS/c/ZSS_STUDENT_CENTER.ZSS_BT_HOMEPAGE.GBL?cmd=login"
payload = {
    "userid": "PUBCOOKIE",
    "pwd": "PUBCOOKIE"
}

pull = r.post(action, data=payload, headers=headers, cookies=cookies)

watchlist = "https://www.beartracks.ualberta.ca/psc/uahebprd/EMPLOYEE/HRMS/c/ZSS_STUDENT_CENTER.ZSS_WATCH_LIST.GBL?Page=ZSSP_WATCH_LIST&Action=A&ACAD_CAREER=UGRD&EMPLID=" + UofAID  + "&INSTITUTION=UOFAB&STRM=1620"
pull = r.get(watchlist, headers=headers, cookies=cookies)

if(pull.status_code != 200):
    quit("Error at pubcookie step")

bs = BeautifulSoup(pull.text, "html.parser")

wtable = bs.find(id="ZSSV_WATCH_LIST$scroll$0")
wrows = wtable.find_all("tr")

i = 2 #first 2 rows are headers so no need to processs those
l = len(wrows)

# there's probably a better way to do this, but I never used python before lol
# Is there such thing as a multi dimension array in python? lol
courses = list()
opn = list()
stat = list()

#Load up smtp service
mail = smtplib.SMTP('smtp.gmail.com', 587)
mail.starttls()
mail.login(email, CCPass)

enrollattempt = "Not Tried"

while i < l:
    wcols = wrows[i].find_all("span", class_="PSEDITBOX_DISPONLY")

    courses.append( wcols[0].string )
    opn.append( wcols[4].string )

    if wcols[4].string[0] != 0:
        
        stat.append("No Opening")
        mail.quit()

    else: 
        stat.append("Opening")

        # SWAP CIV E 315 If there is an opening
        # Modify for your own course

        action = "https://www.beartracks.ualberta.ca/psc/uahebprd/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSR_SSENRL_SWAP.GBL?Page=SSR_SSENRL_SWAP&Action=A&ACAD_CAREER=UGRD&ENRL_REQUEST_ID=0000000000&INSTITUTION=UOFAB&STRM=1620"

        pull = r.get(action, headers=headers, cookies=cookies)

        bs = BeautifulSoup(pull.text, "html.parser")

        ICStateNum = bs.find(id="ICStateNum").get("value")
        ICSID = bs.find(id="ICSID").get("value")

        payload = {
            "ICAJAX": "1",
            "ICNAVTYPEDROPDOWN": "0",
            "ICType": "Panel",
            "ICElementNum": "0",
            "ICStateNum": ICStateNum,
            "ICAction": "DERIVED_REGFRM1_LINK_ADD_ENRL",
            "ICXPos": "0",
            "ICYPos": "470",
            "ResponsetoDiffFrame": "-1",
            "TargetFrameName": "None",
            "FacetPath": "None",
            "ICFocus": "",
            "ICSaveWarningFilter": "0",
            "ICChanged": "-1",
            "ICResubmit": "0",
            "ICSID": ICSID,
            "ICActionPrompt": "false",
            "ICFind": "",
            "ICAddCount": "",
            "ICAPPCLSDATA": "",
            "STDNT_ENRL_SSV1$sels$0" :"1",
            "DERIVED_REGFRM1_SSR_CLS_SRCH_TYPE$247$": "06",
            "DERIVED_REGFRM1_CLASS_NBR$7$": "",
            "SSR_REGFORM_VW$sels$0": "0",
        }

        pull = r.post(action, data=payload, cookies=cookies, headers=headers)

        payload = {
            "ICAJAX": "1",
            "ICNAVTYPEDROPDOWN": "0",
            "ICType": "Panel",
            "ICElementNum": "0",
            "ICStateNum": str(int(ICStateNum)+1),
            "ICAction": "DERIVED_REGFRM1_SSR_PB_SUBMIT",
            "ICXPos": "0",
            "ICYPos": "380",
            "ResponsetoDiffFrame": "-1",
            "TargetFrameName": "None",
            "FacetPath": "None",
            "ICFocus": "",
            "ICSaveWarningFilter": "0",
            "ICChanged": "-1",
            "ICResubmit": "0",
            "ICSID": ICSID,
            "ICActionPrompt": "false",
            "ICFind": "",
            "ICAddCount": "",
            "ICAPPCLSDATA": "",
        }

        pull = r.post("https://www.beartracks.ualberta.ca/psc/uahebprd/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSR_SSENRL_SWAP.GBL", data=payload, cookies=cookies, headers=headers)

        if ("Error" in pull.text):
            enrollattempt = "Tried but failed"
        else:
            enrollattempt = "Tried and succeeded"
        
        content = "There is an opening for " + wcols[0].string + " specifically " + wcols[4].string + " as of " + str(datetime.now())
        content += "\n I tried to enroll you and I " + enrollattempt
        msg = MIMEText(content)
        
        msg['Subject'] = "Course Opening For " + wcols[0].string
        msg['From'] = email
        msg['To'] = email

        mail.send_message(msg)
        msg['To'] = "rafaqali@gmail.com"
        mail.send_message(msg)
        mail.quit()

    i = i+1

if log_attempts == 1:
    i = 0
    l = len(courses)
    log = open("log.txt", "a")

    while i < l:
        log.write( stat[i] + 
                    " | " + 
                    courses[i] + 
                    " | " + 
                    opn[i] + 
                    " | " +  
                    enrollattempt + 
                    " | " + 
                    str(datetime.now()) + "\n" )
        i = i + 1 

    log.write("\n")
    log.close
