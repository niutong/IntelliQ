
# Prompt扩写
## 介绍
基于LLM对话系统的Prompt扩写项目，利用意图识别和自动询问补齐意图，以及词槽填充技术，提升用户意图理解深度，同时通过专家任务prompt增强，提升教研领域任务执行能力。

## 安装和使用

确保您已安装 git、python3。然后执行以下步骤：
```
# 安装步骤

pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 修改配置
配置项在 config/__init__.py
GPT_URL: 可修改为OpenAI的代理地址
API_KEY: 修改为ChatGPT的ApiKey

# 启动
python app.py

# 可视化调试可以浏览器打开 demo/user_input.html 或 127.0.0.1:5000
```
