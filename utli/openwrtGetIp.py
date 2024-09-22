import argparse
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 定义获取接口 IP 地址的函数
def get_vwan_ips(gateway_ip, username="admin", password="admin"):
    """
    访问 OpenWRT 网关，登录后台并获取所有 vwan* 接口的 IPv4 地址。

    :param gateway_ip: OpenWRT 网关的 IP 地址
    :param username: 登录用户名，默认为 'admin'
    :param password: 登录密码，默认为 'admin'
    :return: 字典，键为接口名称，值为对应的 IPv4 地址
    """
    # 登录 URL 和接口页面 URL
    login_url = f"http://{gateway_ip}/cgi-bin/luci"
    interface_url = f"http://{gateway_ip}/cgi-bin/luci/admin/network/network"

    # 初始化 Chrome 浏览器
    driver = webdriver.Chrome()

    try:
        # 访问登录页面
        driver.get(login_url)

        # 填写登录表单
        password_input = driver.find_element(By.ID, 'luci_password')
        password_input.send_keys(password)

        # 点击登录按钮
        login_button = driver.find_element(By.TAG_NAME, 'button')
        login_button.click()
        time.sleep(4)

        # 登录成功后，访问接口页面
        driver.get(interface_url)

        # 等待页面 JavaScript 执行，并等待 id="cbi-network-interface" 的 div 出现
        network_div = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'cbi-network-interface')))

        # 查找包含 class="table cbi-section-table" 的表格
        table = network_div.find_element(By.CLASS_NAME, 'cbi-section-table')

        # 查找所有表格行
        rows = table.find_elements(By.TAG_NAME, 'tr')

        vwan_ips = {}  # 存储接口名称和对应的IP地址

        for row in rows:
            try:
                # 找到 class="ifacebox-head" 的 div 并获取其文本
                ifacebox_head = row.find_element(By.CSS_SELECTOR, 'div.ifacebox-head')
                iface_name = ifacebox_head.text.strip()

                # 筛选以 'vwan' 开头的接口
                if iface_name.startswith('vwan'):
                    # 构造描述 div 的 ID，例如 "vwan1-ifc-description"
                    description_div_id = f"{iface_name}-ifc-description"

                    # 找到描述 div
                    description_div = row.find_element(By.ID, description_div_id)

                    # 在描述 div 中找到包含 "IPv4:" 的 span
                    ipv4_span = description_div.find_element(
                        By.XPATH, ".//span[strong[text()='IPv4: ']]"
                    )

                    ipv4_text = ipv4_span.text  # 例如 "IPv4: 10.19.127.218/22"

                    # 提取 IP 地址部分
                    ip_address = ipv4_text.split(': ')[1].split('/')[0]

                    # 存储结果
                    vwan_ips[iface_name] = ip_address

            except Exception as e:
                print(f"处理行时出错: {e}")

        return vwan_ips

    finally:
        # 确保浏览器在结束时关闭
        driver.quit()


# 如果作为主程序执行，处理命令行参数
if __name__ == "__main__":
    # 定义命令行参数解析
    parser = argparse.ArgumentParser(description="OpenWRT后台自动登录并获取接口IP")
    parser.add_argument("--gateway", required=True, help="OpenWRT 网关的 IP 地址，例如 192.168.15.1")
    args = parser.parse_args()

    # 调用 get_vwan_ips 函数，获取接口信息
    vwan_ips = get_vwan_ips(args.gateway)

    # 输出结果
    for iface, ip in vwan_ips.items():
        print(f"接口 {iface} 的 IPv4 地址是: {ip}")
