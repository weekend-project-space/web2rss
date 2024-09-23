# web2rss

> 输入网址输出 rss

- [x] 支持私有化部署

- [x] 支持 AI

- [x] 支持 rss 源代理

- [x] local router (pull) -> remote router -> save local

- [x] local router (push) -> remote router -> save remote

- [x] fetch (error) -> proxy

## 在线体验

[web2rss](https://web2rss.cc/)

## 使用

**直接运行**

- 下载项目

- 命令行 pip install -f ./requirements.txt

- 修改 config.txt 中的 gpt 参数

- 命令行 python3 ./app.py

- 打开浏览器

**docker 运行**

- 下载项目

- 命令行 docker build -t web2rss .

- 命令行 docker run -p 3390:3390 web2rss

- 打开浏览器
