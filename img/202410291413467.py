#! /usr/bin/python3

import os
import sys
import time
import configparser
import hashlib
import json
from paramiko import SSHClient, AutoAddPolicy

none = "\033[0m"
red = "\033[1;31;40m"
green = "\033[1;32;40m"
passwd = "asdjkl1234"
minion_path = "/data/home/mobile/mobileagent"


def clear():
    os.system("clear")


def connect2remote(remoteip, port=20022, username="mobile"):
    ssh = SSHClient()
    # 允许连接不在know_hosts文件中的主机。
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(remoteip, port, username)
    return ssh


def confirm():
    res = input("\n\n 请输入Yes/No确认操作: ")
    if res == "Yes":
        return True
    else:
        return False


def display_load():
    config = configparser.ConfigParser()
    cfg_path = pub_path + "/ipList.ini"
    config.read(cfg_path)
    groups = config.sections()
    for group in groups:
        print("\n" + group)
        ips = config.options(group)
        for ip in ips:
            print(ip)
    res = input("\n请选择Load组: ")
    if ("Load" + res) not in groups:
        return []
    return config.options("Load" + res)


def welcome():
    clear()
    os.chdir(pub_path)
    print("\n\n欢迎进入MobileAgent管理脚本\n")
    print("  " + green + "1.", none + "文件管理\n")
    print("  " + green + "2.", none + "服务管理\n")
    print("  " + green + "3.", none + "服务器部署\n")
    print("  " + green + "4.", none + "退出\n")
    res = input("  请输入您的选择：")
    print(res)
    if res == "1":
        clear()
        print("\n\n欢迎进入MobileAgent管理脚本\n")
        print("  " + green + "1.", none + "同步mobileagent服务\n")
        print("  " + green + "2.", none + "同步动态配置文件\n")
        print("  " + green + "3.", none + "同步静态配置文件\n")
        print("  " + green + "4.", none + "同步脚本\n")
        print("  " + green + "5.", none + "同步所有文件\n")
        print("\n\n  " + red + "0.", none + "回到首页\n")
        sub_res = input("  请选择您要同步的文件: ")
        clear()
        if sub_res == "0":
            return
        elif sub_res not in "12345":
            print("\n\n  键入错误，即将回到主页，请重新输入")
            time.sleep(1)
            return
        print("\n\n  " + green + "1.", none + "每组前一半服务器")
        print("\n\n  " + green + "2.", none + "每组后一半服务器")
        print("\n\n  " + green + "3.", none + "所有服务器")
        print("\n\n  " + green + "4.", none + "选择Load组")
        choice = input("\n 请选择执行的对象:")
        if choice == "1":
            ip_todo = first_group
        elif choice == "2":
            ip_todo = last_group
        elif choice == "3":
            ip_todo = all_ip
        elif choice == "4":
            ip_todo = display_load()
            if len(ip_todo) == 0:
                print("\n\n  错误，即将回到主页，请重新输入")
                time.sleep(1)
                return
        if not confirm():
            print("\n 取消操作")
            time.sleep(1)
            return
        for ele in ip_todo:
            print(none + "\n\n连接 " + ele)
            c = Connection(ele, passwd)
            if sub_res == "1":
                c.distribute_service()
            elif sub_res == "2":
                c.distribute_dynamic_conf()
            elif sub_res == "3":
                c.distribute_static_conf()
            elif sub_res == "4":
                c.distribute_shells()
            elif sub_res == "5":
                c.distribute_service()
                c.distribute_dynamic_conf()
                c.distribute_static_conf()
                c.distribute_shells()
            c.close()
    elif res == "2":
        clear()
        print("\n\n欢迎进入MobileAgent管理脚本\n")
        print("  " + green + "1.", none + "更新服务\n")
        print("  " + green + "2.", none + "重启服务\n")
        print("  " + green + "3.", none + "停止服务\n")
        print("  " + green + "4.", none + "校验md5\n")
        print("\n\n  " + red + "0.", none + "回到首页\n")
        sub_res = input("  请输入您要执行的操作: ")
        clear()
        if sub_res == "0":
            return
        elif sub_res not in "1234":
            print("\n\n  键入错误，即将回到主页，请重新输入")
            time.sleep(1)
            return
        print("\n\n  " + green + "1.", none + "每组前一半服务器")
        print("\n\n  " + green + "2.", none + "每组后一半服务器")
        print("\n\n  " + green + "3.", none + "所有服务器")
        print("\n\n  " + green + "4.", none + "选择Load组")
        choice = input("\n 请选择执行的对象:")
        if choice == "1":
            ip_todo = first_group
        elif choice == "2":
            ip_todo = last_group
        elif choice == "3":
            ip_todo = all_ip
        elif choice == "4":
            ip_todo = display_load()
            if len(ip_todo) == 0:
                print("\n\n  错误，即将回到主页，请重新输入")
                time.sleep(1)
                return
        if not confirm():
            print("\n 取消操作")
            time.sleep(1)
            return
        if sub_res == "4":
            source_md5 = get_md5(pub_path + "/service/mobileagent")
            contents = []
            for ele in ip_todo:
                c = Connection(ele, passwd)
                print("\n连接 " + ele)
                remote_md5 = c.excute_cmd(
                    "md5sum " + minion_path + "/mobileagent"
                ).split()[0]
                if remote_md5 != source_md5:
                    contents.append(ele)
            print("\n发布机上服务MD5为: ", source_md5)
            print(str(len(contents)) + "台服务器与发布机不一致,具体如下: ")
            for content in contents:
                print(content)
        else:
            for ele in ip_todo:
                print(none + "\n连接 " + ele)
                c = Connection(ele, passwd)
                if sub_res == "1":
                    print("升级服务")
                    c.update_service()
                elif sub_res == "2":
                    print("重启服务")
                    c.restart_service()
                elif sub_res == "3":
                    print("停止服务")
                    c.stop_service()
                c.close()
    elif res == "3":
        clear()
        print("\n\n欢迎进入MobileAgent管理脚本\n")
        print("  " + green + "1.", none + "部署新机器\n")
        print("  " + green + "2.", none + "设定定时任务\n")
        print("  " + green + "3.", none + "Filebeat部署/更新\n")
        print("  " + green + "4.", none + "Filebeat1启动\n")
        print("  " + green + "5.", none + "Filebeat2启动\n")
        print("\n\n  " + red + "0.", none + "回到首页\n")
        sub_res = input("  请输入您要执行的操作: ")
        clear()
        if sub_res == "0":
            return
        elif sub_res not in "12345":
            print("\n\n  键入错误，即将回到主页，请重新输入")
            time.sleep(1)
            return
        print("\n\n  " + green + "1.", none + "每组前一半服务器")
        print("\n\n  " + green + "2.", none + "每组后一半服务器")
        print("\n\n  " + green + "3.", none + "所有服务器")
        print("\n\n  " + green + "4.", none + "选择Load组")
        choice = input("\n 请选择执行的对象:")
        if choice == "1":
            ip_todo = first_group
        elif choice == "2":
            ip_todo = last_group
        elif choice == "3":
            ip_todo = all_ip
        elif choice == "4":
            ip_todo = display_load()
            if len(ip_todo) == 0:
                print("\n\n  错误，即将回到主页，请重新输入")
                time.sleep(1)
                return
        if not confirm():
            print("\n 取消操作")
            time.sleep(1)
            return
        for ele in ip_todo:
            print("\n\n连接 " + ele)
            c = Connection(ele, passwd)
            if sub_res == "1":
                print("机器部署中")
                c.excute_cmd('sudo /bin/bash -c "mkdir -m 777 /data/logbk"', True)
                c.excute_cmd(
                    'sudo /bin/bash -c "mkdir -m 777 /data/logbk/gamelog"', True
                )
                c.distribute_dynamic_conf()
                c.distribute_static_conf()
                c.distribute_shells()
                c.distribute_service()
                c.set_auto_start()
                c.set_filebeat()
                c.set_crontab()
                c.excute_cmd("mkdir " + minion_path + "/log")
                c.excute_cmd("mkdir " + minion_path + "/log/gamelog")
                c.excute_cmd("mkdir " + minion_path + "/log/errorlog")
                c.excute_cmd("cp " + minion_path + "/adm/mobileagent ../")
            elif sub_res == "2":
                print("定时任务设定中")
                c.set_crontab()
            elif sub_res == "3":
                print("Filebeat部署中")
                c.set_filebeat()
            elif sub_res == "4":
                print("Filbeat1启停中")
                c.control_filebeat(1)
            elif sub_res == "5":
                print("Filbeat2启停中")
                c.control_filebeat(2)
            c.close()
    elif res == "4":
        sys.exit()
    else:
        print("\n\n  键入错误，请重新输入")
        time.sleep(1)
        return
    input(none + "\n\n  执行结束，键入任意键回到首页")


def get_md5(fname):
    f = open(fname, "rb")
    f_md5 = hashlib.md5()
    f_md5.update(f.read())
    return f_md5.hexdigest()


def modify_static_conf(fname, port_value):
    with open(fname, "r", encoding="utf-8") as f:
        data = json.load(f)
        data["NetSettings"]["UDPPort"] = port_value
    content = json.dumps(data, ensure_ascii=False, indent=4)
    f = open(fname, "w", encoding="utf8")
    f.write(content)
    f.close()


def know_ip_list():
    """
    读取服务器列表配置文件将服务器分2组
    """
    ip_all = []
    ip_first_half = []
    ip_last_half = []
    config = configparser.ConfigParser()
    path = pub_path + "/ipList.ini"
    config.read(path)
    groups = config.sections()
    for group in groups:
        ips = config.options(group)
        total = len(ips)
        for i, ele in enumerate(ips):
            ip_all.append(ele)
            if i < total // 2:
                ip_first_half.append(ele)
            else:
                ip_last_half.append(ele)
    return ip_first_half, ip_last_half, ip_all


class Connection:
    """连接实例"""

    def __init__(self, remoteip, passwd, port=20022, username="mobile"):
        self.remoteip = remoteip
        self.passwd = passwd
        self.conn = connect2remote(remoteip, port, username)
        self.transferer = self.conn.open_sftp()

    def excute_cmd(self, cmd, needSudo=False, needRes=True):
        needSudo = False
        if needSudo:
            stdin, stdout, stderr = self.conn.exec_command(cmd, get_pty=True)
            time.sleep(2)
            stdin.write(self.passwd + "\n")
            stdin.flush()
            # print(stdout.read().decode('utf-8'))
        else:
            stdin, stdout, stderr = self.conn.exec_command(cmd)
        if needRes:
            return stdout.read().decode("utf-8")
        else:
            return

    def send_file(self, source_path, remote_path):
        # source_md5 = get_md5(source_path)
        if not os.path.exists(source_path):
            print("指定本地目录不存在")
            sys.exit()
        try:
            self.transferer.stat(remote_path)
        except IOError:
            remote_dir = os.path.split(remote_path)[0]
            self.mkdir_p(remote_dir)
        finally:
            self.transferer.put(source_path, remote_path)
            # remote_md5 = self.excute_cmd('md5sum ' + remote_path)
            # if source_md5 != remote_md5.split()[0]:
            #    print('传输文件损坏')

    def __list_local_files(self, path):
        file_list = []
        files = os.listdir(path)
        for ele in files:
            filename = os.path.join(path, ele)
            if os.path.isdir(ele):
                file_list.append(self.__list_local_files(filename))
            else:
                file_list.append(filename)
        return file_list

    def mkdir_p(self, path):
        try:
            self.excute_cmd("mkdir -p " + path)
        except IOError:
            print("创建文件夹错误，3秒后退出程序")
            time.sleep(3)
            sys.exit()

    def send_dir(self, source_path, remote_path):
        if not os.path.exists(source_path):
            print("指定本地目录不存在")
            sys.exit()
        try:
            self.transferer.stat(remote_path)
        except IOError:
            self.transferer.mkdir(remote_path)
        finally:
            if source_path[-1] == "/":
                source_path = source_path[0:-1]
            if remote_path[-1] == "/":
                remote_path = remote_path[0:-1]
            files = self.__list_local_files(source_path)
            for ele in files:
                filename = os.path.split(ele)[-1]
                remote_filename = remote_path + "/" + filename
                print(filename, "传输中...")
                self.send_file(ele, remote_filename)

    def distribute_dynamic_conf(self):
        print("动态配置文件传输中...")
        self.send_file(
            pub_path + "/conf/dynamic_config.json", minion_path + "/dynamic_config.json"
        )
        self.send_file(
            pub_path + "/conf/linker_config.json", minion_path + "/linker_config.json"
        )


    def distribute_static_conf(self):
        # idc = self.remoteip.split(".")[1]
        # if idc != "141":
        #     basic = 30000
        #     plus = int(self.remoteip.split(".")[-1])
        #     if plus < 100:
        #         basic = 30300
        #     port = basic + plus
        # else:
        #     port = 30300
        # modify_static_conf(pub_path + "/conf/static_config.json", port)
        print("静态配置文件传输中...")
        self.send_file(
            pub_path + "/conf/static_config.json", minion_path + "/static_config.json"
        )
        self.send_file(pub_path + "/conf/CountryIP.dat", minion_path + "/CountryIP.dat")
        self.send_file(pub_path + "/conf/TKIPQuery.dat", minion_path + "/TKIPQuery.dat")

    def distribute_service(self):
        print("MobileAgent服务传输中...")
        self.send_file(
            pub_path + "/service/mobileagent", minion_path + "/adm/mobileagent"
        )

    def distribute_shells(self):
        source_path = pub_path + "/script/"
        remote_path = minion_path + "/"
        self.send_dir(source_path, remote_path)
        self.excute_cmd("chmod +x " + remote_path + "*.sh")

    def set_filebeat(self):
        print("Filebeat部署该功能已废弃")
        return
        res = self.excute_cmd('grep "filebeat.sh" /etc/rc.d/rc.local')
        if res == "":
            self.excute_cmd(
                'sudo /bin/bash -c "echo "/etc/filebeat/filebeat.sh" >> /etc/rc.d/rc.local"',
                True,
            )
        self.excute_cmd('sudo /bin/bash -c "chmod +x /etc/rc.d/rc.local"', True)
        self.send_file(
            pub_path + "/auto/filebeat_conn_mig.yml",
            minion_path + "/filebeat_conn_mig.yml",
        )
        self.send_file(
            pub_path + "/auto/filebeat_conn_mig2.yml",
            minion_path + "/filebeat_conn_mig2.yml",
        )
        self.send_file(pub_path + "/auto/filebeat.sh", minion_path + "/filebeat.sh")
        self.excute_cmd("chmod +x " + minion_path + "/filebeat.sh")
        self.excute_cmd(
            'sudo /bin/bash -c "mv ' + minion_path + '/filebeat.sh /etc/filebeat"', True
        )
        self.excute_cmd(
            'sudo /bin/bash -c "mv '
            + minion_path
            + '/filebeat_conn_mig.yml /etc/filebeat"',
            True,
        )
        self.excute_cmd(
            'sudo /bin/bash -c "mv '
            + minion_path
            + '/filebeat_conn_mig2.yml /etc/filebeat"',
            True,
        )
        self.excute_cmd(
            'sudo /bin/bash -c "chown root /etc/filebeat/filebeat_conn_mig.yml"', True
        )
        self.excute_cmd(
            'sudo /bin/bash -c "chgrp root /etc/filebeat/filebeat_conn_mig.yml"', True
        )
        self.excute_cmd(
            'sudo /bin/bash -c "chmod go-w /etc/filebeat/filebeat_conn_mig.yml"', True
        )
        self.excute_cmd(
            'sudo /bin/bash -c "chown root /etc/filebeat/filebeat_conn_mig2.yml"', True
        )
        self.excute_cmd(
            'sudo /bin/bash -c "chgrp root /etc/filebeat/filebeat_conn_mig2.yml"', True
        )
        self.excute_cmd(
            'sudo /bin/bash -c "chmod go-w /etc/filebeat/filebeat_conn_mig2.yml"', True
        )
        res = self.excute_cmd("ll /etc/filebeat | grep filebeat_con")
        print(res)
        res = self.excute_cmd("ll /etc/filebeat | grep filebeat.sh")
        print(res)

    def control_filebeat(self, order):
        if order == 1:
            pid = self.excute_cmd(
                "ps -fe| grep filebeat_conn_mig.yml|grep -v grep| awk '{print $2}'"
            )[:-1]
            if pid != "":
                self.excute_cmd('sudo /bin/bash -c "kill ' + pid + '"', True)
            # self.excute_cmd(
            #     'sudo  /bin/bash -c "nohup /usr/share/filebeat/bin/filebeat -path.home /usr/share/filebeat -path.config /etc/filebeat -path.data /var/lib/filebeat -path.logs /var/log/filebea -c /etc/filebeat/filebeat_conn_mig.yml &"',
            #     True,
            #     False,
            # )
        if order == 2:
            pid = self.excute_cmd(
                "ps -fe| grep filebeat_conn_mig2.yml|grep -v grep| awk '{print $2}'"
            )[:-1]
            if pid != "":
                self.excute_cmd('sudo /bin/bash -c "kill ' + pid + '"', True)
            # self.excute_cmd(
            #     'sudo  /bin/bash -c "nohup /usr/share/filebeat/bin/filebeat -path.home /usr/share/filebeat -path.config /etc/filebeat -path.data /var/lib/filebeat -path.logs /var/log/filebea -c /etc/filebeat/filebeat_conn_mig2.yml &"',
            #     True,
            #     False,
            # )

    def set_auto_start(self):
        print("设置MobileAgent自启动...")
        self.send_file(
            pub_path + "/auto/mobileagent.service", minion_path + "/mobileagent.service"
        )
        self.excute_cmd(
            'sudo /bin/bash -c "mv '
            + minion_path
            + '/mobileagent.service /usr/lib/systemd/system"',
            True,
        )
        self.excute_cmd('sudo /bin/bash -c "systemctl daemon-reload"', True)
        self.excute_cmd('sudo /bin/bash -c "systemctl enable mobileagent"', True)
        # self.excute_cmd('sudo /bin/bash -c "systemctl start mobileagent"', True)

    def set_crontab(self):
        print("设置定时任务...")
        res = self.excute_cmd(
            'sudo grep "checkmobileagent.sh" /var/spool/cron/mobile', True
        )
        if "checkmobileagent" not in res:
            self.excute_cmd(
                '''sudo /bin/bash -c "echo '0-59/2 * * * * /data/home/mobile/mobileagent/checkmobileagent.sh' >> /var/spool/cron/mobile"''',
                True,
            )
        res = self.excute_cmd('sudo grep "backlog.sh" /var/spool/cron/mobile', True)
        if "backlog" not in res:
            self.excute_cmd(
                '''sudo /bin/bash -c "echo '00 00 * * * /data/home/mobile/mobileagent/backlog.sh' >> /var/spool/cron/mobile"''',
                True,
            )
        self.excute_cmd('''sudo /bin/bash -c "systemctl restart crond"''', True)

    def update_service(self):
        self.excute_cmd(minion_path + "/updateService.sh")

    def restart_service(self):
        self.excute_cmd('sudo /bin/bash -c "systemctl restart mobileagent"', True)

    def stop_service(self):
        self.excute_cmd('sudo /bin/bash -c "systemctl stop mobileagent"', True)

    def check_md5(self, source_file, remote_file):
        source_md5 = get_md5(source_file)
        remote_md5 = self.excute_cmd("md5sum " + remote_file).split()[0]
        if source_md5 != remote_md5:
            print(
                self.remoteip
                + " 上 "
                + source_file.split("/")[-1]
                + " 与发布机版本不一致"
            )
        else:
            print(remote_md5)

    def check_service(self):
        self.check_md5(pub_path + "/service/mobileagent", minion_path + "/mobileagent")

    def get_tourney(self):
        res = self.excute_cmd(
            "awk '{print $2}' " + minion_path + "/tnydata.dump | grep -w 2970  | wc -l"
        )
        res = res.strip()
        if res == "1":
            return True
        else:
            return False

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    try:
        pub_path = os.getcwd()
        first_group, last_group, all_ip = know_ip_list()
        while True:
            welcome()
    except KeyboardInterrupt:
        pass
