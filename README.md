# Chang Tips

## 概述
Chang Tips是一个使用Python开发，以企业微信为推送渠道的提醒推送工具，向同学们提供校内各项事务提醒服务。

## 主要功能
* 校内疫情打卡提醒：定时检测当日的打卡状态，重复提醒用户及时打卡，直至打卡完成后停止推送。
* 作业提醒：定时检查用户未完成的作业、讨论、考试，提前提醒；检查老师布置的新任务并及时通知；一键查看最近需要完成的任务。
* 看起来不怎么聪明的机器人：在微信就可以查阅天气、百科等实用信息。
* 更多功能正在新建文件夹中...

## 使用方法
1.使用微信扫一扫二维码，关注公众号（[点我获取二维码](https://changwebsite.azurewebsites.net/qrcode)）

2.关注后提示填写手机号验证身份，可任意输入11位数字，Chang Tips不会存储此信息

<img src="https://changwebsite.azurewebsites.net/static/index/step1.e6affd67208d.jpeg" width="50%">

<img src="https://changwebsite.azurewebsites.net/static/index/step2.7dc8deba6b04.jpeg" width="50%">

3.验证通过后，点击进入需要提醒的功能（如“莞工疫情打卡提醒”），点击下方菜单栏的“绑定账号”按钮，绑定账号后即可接收提醒

<img src="https://changwebsite.azurewebsites.net/static/index/step3.431fa29d2244.jpeg" width="50%">

4.Enjoy it!

## 帮助与支持
* 常见问题：https://changwebsite.azurewebsites.net/qa
* 反馈有礼：https://changwebsite.azurewebsites.net/feedback

## 工作原理
<img src="https://changwebsite.azurewebsites.net/static/index/modules.23ea0c9b6fbc.png">

项目网站使用Python Web框架Django开发，前端样式使用了同微信原生视觉体验一致的基础样式库WeUI。网站部署在云服务器，用户可以通过微信公众号菜单栏访问。  

用户进入绑定账号页面填写第三方平台账号信息，将账号信息交由相应模块处理，绑定成功后，将用户账号信息以及相应平台的cookie/token加密存储至数据库。  

定时提醒脚本模块使用Python编写。通过腾讯云函数服务可以定时触发“获取用户事务”模块，携带cookie/token向相应平台请求用户的事务。    

调用企业微信相应API，向用户推送提醒消息；用户即可在微信客户端接收提醒消息。  

用户可随时访问取消绑定页面，请求停止服务，并删除数据库中用户的账号信息。

<img src="https://changwebsite.azurewebsites.net/static/index/process.e39f5221231d.png">

## 引用的开源项目
WeUI：https://github.com/Tencent/weui

企业微信官方API：https://github.com/sbzhu/weworkapi_python

## 开源仓库
为保护用户的个人信息，部分功能代码相关细节恕不提供。开发者承诺该项目不会泄露用户个人信息以及将其用作其他用途。感谢您的理解、支持与信任！

GitHub：https://github.com/AChangAZha/ChangTips

如果你觉得Chang Tips还不错，不妨给我点个小星星吧！

## 特别声明
* 该项目及其代码仅用于测试和学习研究，禁止用于商业用途。
* 用户直接或间接使用或传播该项目及其代码，开发者均不对上述行为产生的任何后果负责。
* 该项目不会泄露用户个人信息以及将其用作其他用途。