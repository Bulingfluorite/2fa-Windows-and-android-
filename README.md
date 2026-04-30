---
# 本地离线2FA验证器（Windows + Android 双端）
完全离线的2FA验证码生成工具，所有密钥本地存储，无需联网验证，彻底规避在线工具密钥泄露风险，使用便捷开箱即用。

## ✨ 核心特性
- 🔒 完全离线运行：全程无网络请求，密钥仅保存在本地设备，安全可靠
- 📦 多端覆盖：支持Windows客户端、免安装网页版、Android客户端三种使用形式
- 🚀 开箱即用：无需复杂配置，录入密钥即可生成实时验证码
- 💾 自动持久化：录入的密钥自动保存，重启无需重复录入

---

## 🖥️ Windows 客户端
基于 Python + PyQt 框架开发，打包为单EXE可执行文件，无需安装依赖、无需配置环境，下载后直接双击即可运行。
![Windows端界面](https://github.com/user-attachments/assets/f59668ac-2437-4056-9901-2007935abeb3)

---

## 🌐 免安装网页版
不想下载安装客户端的用户可以使用纯网页版本，代码完全开源（安卓版移植了这个代码），为纯静态前端实现，本地打开即可使用，无需部署服务器。
> 网页版仓库地址：[lee11089/Totp-Generator](https://github.com/lee11089/Totp-Generator)

---

## 📱 Android 客户端
基于上述网页版的核心逻辑移植，采用 HBuilder uni-app 框架构建，适配安卓全系列机型。
- 直接输入密钥，不支持保存
- 实测存在约5秒的验证时间延迟，支持手动调整校准，支持0.5和5秒微调切换。

<img width="1200" height="2664" alt="03e167fb8877f077a5b2dc405988abc4" src="https://github.com/user-attachments/assets/cf433a47-38d1-4e75-be4f-b77995aa3f9a" />

---
