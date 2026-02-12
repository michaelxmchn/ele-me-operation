#!/usr/bin/env python3
"""
饿了么商家版 ADB 操作脚本
用于自动化控制手机上的饿了么商家版App
"""

import subprocess
import time
import os

class ElemeADB:
    """饿了么商家版 ADB 控制"""
    
    def __init__(self):
        self.device = None
        
    def connect(self, device_id: str = None):
        """连接设备"""
        cmd = ["adb", "devices"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        devices = [line.split()[0] for line in result.stdout.split('\n')[1:] if line.strip()]
        
        if not devices:
            print("❌ 未找到设备")
            return False
        
        self.device = devices[0] if not device_id else device_id
        print(f"✅ 已连接: {self.device}")
        return True
    
    def install_app(self, apk_path: str):
        """安装App"""
        if not os.path.exists(apk_path):
            print(f"❌ 文件不存在: {apk_path}")
            return False
        
        cmd = ["adb", "-s", self.device, "install", "-r", apk_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if "Success" in result.stdout:
            print(f"✅ 安装成功: {apk_path}")
            return True
        else:
            print(f"❌ 安装失败: {result.stdout}")
            return False
    
    def screenshot(self, filename: str = "screenshot.png"):
        """截图"""
        cmd = ["adb", "-s", self.device, "exec-out", "screencap", "-p", f"/sdcard/{filename}"]
        subprocess.run(cmd)
        
        pull_cmd = ["adb", "-s", self.device, "pull", f"/sdcard/{filename}", filename]
        result = subprocess.run(pull_cmd, capture_output=True)
        
        if os.path.exists(filename):
            print(f"📸 截图: {filename}")
            return filename
        return None
    
    def tap(self, x: int, y: int):
        """点击坐标"""
        cmd = ["adb", "-s", self.device, "shell", "input", "tap", str(x), str(y)]
        subprocess.run(cmd)
        print(f"👆 点击: {x}, {y}")
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300):
        """滑动"""
        cmd = ["adb", "-s", self.device, "shell", "input", "swipe", 
              str(x1), str(y1), str(x2), str(y2), str(duration)]
        subprocess.run(cmd)
        print(f"👆 滑动: {x1},{y1} -> {x2},{y2}")
    
    def input_text(self, text: str):
        """输入文字"""
        # 需要先点击输入框
        cmd = ["adb", "-s", self.device, "shell", "input", "text", text]
        subprocess.run(cmd)
        print(f"⌨️ 输入: {text}")
    
    def open_app(self, package_name: str):
        """打开App"""
        cmd = ["adb", "-s", self.device, "shell", "monkey", "-p", package_name, "-c", "android.intent.action.MAIN", "1"]
        subprocess.run(cmd)
        print(f"📱 打开: {package_name}")
        time.sleep(2)
    
    def get_app_version(self, package_name: str) -> str:
        """获取App版本"""
        cmd = ["adb", "-s", self.device, "shell", "dumpsys", "package", package_name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        for line in result.stdout.split('\n'):
            if "versionName" in line:
                version = line.split('=')[-1].strip()
                print(f"📱 {package_name} 版本: {version}")
                return version
        return None


def main():
    """主函数"""
    adb = ElemeADB()
    
    print("=== 饿了么商家版 ADB 控制 ===")
    
    if not adb.connect():
        return
    
    print("\n可用命令:")
    print("  install <apk>  - 安装App")
    print("  screenshot [文件] - 截图")
    print("  tap x y       - 点击")
    print("  swipe x1 y1 x2 y2 - 滑动")
    print("  open <包名>    - 打开App")
    print("  version <包名> - 查看版本")
    print("  exit          - 退出")
    
    while True:
        cmd = input("\n> ").strip().split()
        if not cmd:
            continue
            
        if cmd[0] == "exit":
            break
        elif cmd[0] == "install" and len(cmd) > 1:
            adb.install_app(cmd[1])
        elif cmd[0] == "screenshot":
            filename = cmd[1] if len(cmd) > 1 else "screenshot.png"
            adb.screenshot(filename)
        elif cmd[0] == "tap" and len(cmd) > 2:
            adb.tap(int(cmd[1]), int(cmd[2]))
        elif cmd[0] == "swipe" and len(cmd) > 4:
            adb.swipe(int(cmd[1]), int(cmd[2]), int(cmd[3]), int(cmd[4]))
        elif cmd[0] == "open" and len(cmd) > 1:
            adb.open_app(cmd[1])
        elif cmd[0] == "version" and len(cmd) > 1:
            adb.get_app_version(cmd[1])


if __name__ == "__main__":
    main()
