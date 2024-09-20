#!/usr/bin/env python

import ddddocr
import onnxruntime
import requests
from io import BytesIO
from urllib.parse import urlparse, parse_qs
import argparse

NET_AUTH_BASEURL = "https://net-auth.shanghaitech.edu.cn:19008"

class NetAuthenticator:
    def __init__(self, ip, usr,passwd):
        self.session = requests.Session()
        self.user_id = usr
        self.password = passwd
        assert ip is not None
        self.ip_address=ip
            

    def get_push_page_id_and_ssid(self):
        verify_url = f"{NET_AUTH_BASEURL}/portal?uaddress={self.ip_address}&ac-ip=0"
        print("Verify URL:", verify_url)
    
        redirected_verify = self.session.get(verify_url, allow_redirects=True)
        parsed_redirected_url = urlparse(redirected_verify.url)
        query_params = parse_qs(parsed_redirected_url.query)

        self.push_page_id = query_params.get("pushPageId", [None])[0]
        self.ssid = query_params.get("ssid", [None])[0]

        print("Get pushPageId:", self.push_page_id)
        print("Get ssid:", self.ssid)

    def get_verify_code(self):
        image_url = f"{NET_AUTH_BASEURL}/portalauth/verificationcode?uaddress={self.ip_address}"
        onnxruntime.set_default_logger_severity(3)

        response = self.session.get(image_url)
        img_bytes = BytesIO(response.content).read()

        ocr = ddddocr.DdddOcr()
        verify_code = ocr.classification(img_bytes)
        print("Verify code:", verify_code)
        return verify_code

    def perform_login(self):
        self.get_push_page_id_and_ssid()
    
        login_data = {
            "userName": self.user_id,
            "userPass": self.password,
            "uaddress": self.ip_address,
            "validCode": self.get_verify_code(),
            "pushPageId": self.push_page_id,
            "ssid": self.ssid,
            "agreed": "1",
            "authType": "1"
        }

        login_response = self.session.post(f"{NET_AUTH_BASEURL}/portalauth/login", data=login_data)
        response_data = login_response.json()

        if response_data.get("success") == True:
            print("Successfully logged in")
        else:
            print("Login was not successful, please check manually")


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="自动网络认证 ")
    parser.add_argument('--ip','-ip', type=str, help='要认证的ip地址',required=True)
    parser.add_argument('--user','-u', type=str, help='egate用户',required=True)
    parser.add_argument('--passwd','-p', type=str, help='egate密码',required=True)
    
    args = parser.parse_args()
    
    authenticator = NetAuthenticator(args.ip,args.user,args.passwd)
    authenticator.perform_login()