# RasaCALM操作手册
## 项目介绍
本项目基于rasapro，操作步骤如下

💡 文件说明 💡

# 基于RASAPRO的中文任务型机器人

![Rasaro](https://img.shields.io/badge/rasapro-3.10.7-blue) 
![Python](https://img.shields.io/badge/python-3.10.15-green)
![TensorFlow](https://img.shields.io/badge/tensorflow-2.14.1-orange)

![Openai](https://img.shields.io/badge/openai-1.47.1-red)
![Rasa](https://img.shields.io/badge/rasa-3.10.0-blue) 

💡 基本使用 💡

### 训练
rasa train --domain domain

### 多线程训练   
rasa train --domain domain --num-threads 12

### 开启 action 服务器   
rasa run actions   
rasa run -p 5011 --enable-api --cors "*" 

### 使用
通过命令行界面启动 action 服务器后，即可按照以下步骤进行对话
#### 1.使用网页对话
rasa inspect

![聊天界面](.\\image\\1.png "相对路径演示,下一级目录")

#### 2.通过postman测试

![postman界面](.\\image\\2.png "相对路径演示,下一级目录")


将文件紫云创语音下单接口.postman_collection.json与文件RASA.postman_collection.json导入postman，通过连续对话窗口进行对话，测试
