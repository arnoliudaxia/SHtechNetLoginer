import argparse

from utli.openwrtGetIp import get_vwan_ips
from netloginer_openwrt_mutliwan import NetAuthenticator

# 定义命令行参数解析
parser = argparse.ArgumentParser(description="OpenWRT后台自动登录并获取接口IP")
parser.add_argument("--gateway", required=True, help="OpenWRT 网关的 IP 地址，例如 192.168.15.1")
args = parser.parse_args()

# 调用 get_vwan_ips 函数，获取接口信息
vwan_ips = get_vwan_ips(args.gateway)

accountsPools= [
    {"user":"####","passwd":"#####", "times":3},
 ]

for _, ip in vwan_ips.items():
    authenticator = NetAuthenticator(ip,accountsPools[0]['user'],accountsPools[0]['passwd'])
    authenticator.perform_login()

    accountsPools[0]['times']=accountsPools[0]['times']-1
    if accountsPools[0]['times']==0:
        accountsPools.pop(0)
    assert len(accountsPools)>0