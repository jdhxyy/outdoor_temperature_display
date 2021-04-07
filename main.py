"""
Copyright 2021-2021 The jdh99 Authors. All rights reserved.
室外温度显示
Authors: jdh99 <jdh821@163.com>
"""

import tziot
import time
import ssd1306py as lcd
import machine

# 本节点地址和密码
IA = 0x2141000000010002
PWD =

# WIFI账号密码
WIFI_SSID = 'JDHOME_MASTER'
WIFI_PWD =

# 服务号
# 读取NTP网络时间
RID_GET_TIME = 1

# 读取温度
RID_GET_TEMP = 1

# 通信管道
pipe = 0


def main():
    global pipe

    # 初始化OLED屏
    init_oled()
    # 连接wifi
    connect_wifi()

    pipe = tziot.bind_pipe_net(IA, PWD, '0.0.0.0', 12025)
    tziot.run(app)


def init_oled():
    lcd.init_i2c(22, 21, 128, 64)
    lcd.text('start system', 0, 0, 16)
    lcd.text('please wait...', 0, 20, 16)
    lcd.show()


def connect_wifi():
    print('connect wifi')
    ok = tziot.connect_wifi(WIFI_SSID, WIFI_PWD)
    if ok is False:
        print('connect wifi failed')
        machine.reset()
    print('connect wlan success')


def app():
    """业务程序.每分钟获取ntp时间和温度值"""
    global pipe

    # 连接物联网
    fail_num = 0
    while True:
        if fail_num >= 10:
            print('connect too many.reset!')
            machine.reset()

        if not tziot.is_conn():
            fail_num += 1
            time.sleep(10)
            continue
        break
    print('connect ok')
    lcd.clear()
    lcd.text('connect ok', 0, 20, 16)
    lcd.show()

    # 周期业务
    fail_num = 0
    run_time = 0
    while True:
        if fail_num >= 10:
            print('fail too many.reset!')
            machine.reset()

        lcd.clear()
        # 获取ntp网络时间
        resp, err = tziot.call(pipe, 0x2141000000000004, RID_GET_TIME, 5000, bytearray())
        if err != 0:
            fail_num += 1
            continue
        lcd.text(tziot.bytearray_to_str(resp), 0, 0, 8)

        # 获取南京室外温度
        resp, err = tziot.call(pipe, 0x2141000000010001, RID_GET_TEMP, 5000, bytearray())
        if err != 0 or len(resp) != 2:
            fail_num += 1
            continue
        fail_num = 0
        temp = (resp[0] << 8) + resp[1]
        if temp >= 0x8000:
            temp = 0x10000 - temp
        temp = temp / 10
        lcd.text('%.1f' % temp, 30, 20, 32)
        lcd.show()
        time.sleep(60)

        # 每半小时定时复位
        run_time += 60
        if run_time >= 1800:
            print('reset system!')
            machine.reset()


if __name__ == '__main__':
    main()
