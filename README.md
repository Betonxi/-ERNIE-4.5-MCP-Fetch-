

# **基于 ERNIE-4.5 与 MCP 远程 Fetch 的多源网页抓取与智能内容分析系统**



---

## **一、MCP**

## **什么是MCP？为什么要使用MCP？**

MCP，全称是Model Context Protocol，模型上下文协议，由Claude母公司Anthropic于去年11月正式提出。

MCP刚发布的时候不温不火，直到今年Agent大爆发才被广泛关注。而在今年2月，Cursor正式宣布加入MCP功能支持，一举将MCP推到了全体开发人员面前。从本质上来说，MCP是一种技术协议，一种智能体Agent开发过程中共同约定的一种规范。这就好比秦始皇的“书同文、车同轨”，在统一的规范下，大家的协作效率就能大幅提高，最终提升智能体Agent的开发效率。截至目前，已上千种MCP工具诞生，在强悍的MCP生态加持下， 人人手搓Manus的时代即将到来。

总的来说，MCP解决的最大痛点，就是Agent开发中调用外部工具的技术门槛过高的问题。

我们都知道，能调用外部工具，是大模型进化为智能体Agent的关键，如果不能使用外部工具，大模型就只能是个简单的聊天机器人，甚至连查询天气都做不到。由于底层技术限制啊，大模型本身是无法和外部工具直接通信的，因此Function calling的思路，就是创建一个外部函数（function）作为中介，一边传递大模型的请求，另一边调用外部工具，最终让大模型能够间接的调用外部工具。

![](https://ai-studio-static-online.cdn.bcebos.com/57c3046947ba4f6f8ed98043fb43dd48aa7c4381886547c996fd80f557d71df3)




例如，当我们要查询当前天气时，让大模型调用外部工具的function calling的过程就如图所示：



![](https://ai-studio-static-online.cdn.bcebos.com/f3c41bc366ab4bca9392e039fa987d9d296cae1dc9694a0080d5ba92d451e05b)

Function calling是个非常不错的技术设计，自诞生以来，一直被业内奉为圭臬。但唯一的问题就是，编写这个外部函数的工作量太大了，一个简单的外部函数往往就得上百行代码，而且，为了让大模型“认识”这些外部函数，我们还要额外为每个外部函数编写一个JSON Schema格式的功能说明，此外，我们还需要精心设计一个提示词模版，才能提高Function calling响应的准确率。

而MCP的目标，就是能在Agent开发过程中，让大模型更加便捷的调用外部工具。为此，MCP提出了两个方案，其一，“车同轨、书同文”，统一Function calling的运行规范。

首先是先统一名称，MCP把大模型运行环境称作 MCP Client，也就是MCP客户端，同时，把外部函数运行环境称作MCP Server，也就是MCP服务器，


![](https://ai-studio-static-online.cdn.bcebos.com/e72f20ee53f848cb82aa4c01c62abed57d14c5a4f8f043228775cb79e7b19674)


然后，统一MCP客户端和服务器的运行规范，并且要求MCP客户端和服务器之间，也统一按照某个既定的提示词模板进行通信。

“车同轨、书同文”最大的好处就在于，可以避免MCP服务器的重复开发，也就是避免外部函数重复编写。例如，像查询天气、网页爬取、查询本地MySQL数据库这种通用的需求，大家有一个人开发了一个服务器就好，开发完大家都能复制到自己的项目里来使用，不用每个人每次都单独写一套。

现在，只要你本地运行的大模型支持MCP协议，也就是只要安装了相关的库，仅需几行代码即可接入这些海量的外部工具，是不是感觉Agent开发门槛瞬间降低了呢。

这种“车同轨、书同文”的规范，在技术领域就被称作协议，例如http就是网络信息交换的技术协议。各类技术协议的目标，都是希望通过提高协作效率来提升开发效率，而MCP，Model Context Protocol，就是一种旨在提高大模型Agent开发效率的技术协议。

那既然是协议，必然是使用的人越多才越有用。因此，为了进一普及MCP协议，Anthropic还提供了一整套MCP客户端、服务器开发的SDK，也就是开发工具，并且支持Python、TS和Java等多种语言，借助SDK，仅需几行代码，就可以快速开发一个MCP服务器。


## **二、项目简介**

本项目构建了一个 **可对任意网页进行自动抓取、清洗、格式转换与 AI 内容分析的智能系统**。
系统通过 **MCP（Model Context Protocol）远程 fetch 服务器**获取网页数据，并以 **ERNIE-4.5 超大模型**进行深度内容理解，实现：

*  自动抓取网页 HTML
*  自动过滤脚本、广告、噪声
*  自动转换为结构化 Markdown
*  自动进行智能摘要、信息抽取、页面逻辑解析
*  自动保存 Markdown 与分析报告

系统兼具 **稳定性、扩展性与跨站点通用性**，能够作为数据采集、RAG 构建、情报分析、网页自动化理解等任务的基础组件。



## **三、项目背景**

随着 Web 信息规模快速膨胀，互联网已成为结构化与非结构化数据的主要来源。
但现实场景中，网页内容采集仍存在以下痛点：

####  **1. 网页结构复杂多变**

不同网站的 HTML 结构、CSS 命名、脚本渲染方式差异巨大，通用解析往往失效。

####  2. **动态渲染与异步加载增多**

大量内容通过 JS、Ajax、滚动加载生成，传统 requests 无法直接获取。

####  3. **噪声内容干扰严重**

广告、导航栏、推荐区、脚本注释占比高，需要进一步清理。

####  4. **人工总结页面内容成本高**

采集只是第一步，真正痛点在于“理解”，而不是“下载”。

因此，本项目提出一个全链路智能解决方案：

> **抓取 → 清洗 → Markdown 转换 → AI 深度理解 → 输出结构化报告**

通过 ERNIE-4.5 进行网页级内容分析，帮助开发者、研究者实现真正意义上的“自动网页理解”。

---

## **四、项目整体方案设计**

整个系统由 4 大核心模块组成：

---

###  **1. 网页抓取模块（MCP Fetch + Direct Requests）**

构建多源抓取能力：

| 抓取方式               | 场景                  | 优点                 |
| ------------------ | ------------------- | ------------------ |
| **MCP 远程 fetch**   | 动态网页、反爬较强网页、需代理访问网页 | 稳定、绕过地区限制、支持 JS 渲染 |
| **本地 requests 抓取** | 静态网页、轻量级页面          | 速度快、依赖低            |

系统支持自动策略切换：

> MCP 失败 → 自动 fallback 到 requests。

保证“任何网页都能试图抓取”。

---

###  **2. HTML → Markdown 清洗与转换模块**

使用 BeautifulSoup 清理噪声：

* 删除 `<script>`、`<style>`、`<noscript>`
* 删除注释
* 删除广告节点
* 删除无意义标签
* 清理空行
* 统一格式输出 Markdown

最终生成清爽、结构化的内容，便于模型理解。

---

###  **3. ERNIE-4.5 智能内容分析模块**

将清洗后的 Markdown 输入 ERNIE-4.5 模型，模型自动完成：

*  网页内容总结
*  网页结构拆解
*  关键信息提取
*  表格、列表、段落分析
*  主观摘要、趋势洞察
*  用于 RAG 的知识块生成

这一部分是整个系统的核心智能体现。

---

###  **4. 文件管理与项目输出模块**

系统会自动生成：

####  Markdown 内容文件（原文结构化版）

格式：

```
output/markdown/xxx_markdown_xxx.md
```

###  AI 分析报告文件（ERNIE-4.5 返回）

格式：

```
output/analysis/xxx_analysis_xxx.md
```

每次抓取均带时间戳：
避免覆盖、便于版本化管理。

---

## **五、项目架构图**

![](https://ai-studio-static-online.cdn.bcebos.com/43974d0231c3440ab9f857404cfe0ca8f6c37e4faa364ceeae151688d5fdaadb)


---

## **六、系统功能点**

####  **1. 多源网页抓取（双通道）**

* MCP → 支持动态内容获取
* Requests → 静态网页快速抓取
* 自动降级策略

####  **2. 自动网页结构清洗**

* 标签剥离
* 脚本移除
* 噪声过滤
* 注释清理
* 内容结构化

####  **3. HTML → Markdown 转换**

适用于：

* RAG 构建
* 知识库收录
* 数据集整理
* 内容展示

####  **4. ERNIE-4.5 深度内容理解**

模型能：

* 分析页面布局
* 抽取表格与列表
* 提取关键事实
* 自动总结
* 自动写“页面知识卡片”
* 自动结构化输出

####  **5. 智能文件组织**

程序自动生成：

* Markdown 原文
* AI 分析报告
* 文件名包含域名、路径、时间戳
* 统一存档便于管理

---

## **七、数据说明**

本项目不依赖外部数据集，
**网页本身就是数据来源**。

系统可以采集的数据包括：

* 标题
* 段落内容
* 图片标签
* 列表信息
* 表格
* 结构化数据块
* 元数据（time、keywords 等）

输出格式统一为 Markdown，使其可用于：

* 知识图谱构建
* 大模型训练/微调
* 信息抽取任务
* 数据分析
* NLP 任务输入


## **八、核心代码解析**

本节将对主程序进行结构化拆解，帮助读者理解整个系统的执行流程与模块协作方式。

以下代码均来自本项目主程序 `app.py`，并根据实际模块分段解释。

---

## **8.1 程序初始化与依赖导入**

```python
from bs4 import BeautifulSoup
from datetime import datetime
import shutil
import os

from ernie import ErnieBot
from ernie import ErnieBotClient
from mcp import Client
from mcp.types import Tool

import requests
import http.client
import urllib3
import certifi
import time
```

####  功能说明

* **BeautifulSoup**：HTML 清洗与 DOM 解析
* **ERNIE-4.5 客户端**：与文心大模型通信
* **MCP Client**：与远程 Fetch 服务通信
* **Requests**：备用网页抓取模式
* **SSL 证书适配**：用于保证请求稳定性

这些库组合构成系统全链路能力：抓取 → 清洗 → 模型理解。

---

## **8.2 WebScraperAssistant 类结构总览**

```python
class WebScraperAssistant:
    def __init__(self, base_url=None):
        super().__init__()
        self.base_url = base_url
```

这一类是整个系统的“大脑”，负责：

* 网页抓取
* HTML 清洗
* Markdown 转换
* 文件保存
* 调用 ERNIE-4.5 分析

所有功能均通过该类的一个实例来完成。

---

## **8.3 使用 MCP Fetch 进行远程网页抓取**

```python
async def run_with_mcp(self, url):
    async with Client("mcp") as client:
        fetch_tool: Tool = client.get_tool("fetch")

        result = await fetch_tool.run({
            "url": url,
            "mode": "block",  # 阻塞模式
            "headers": {
                "User-Agent": "...Chrome/119 Safari/537.36"
            }
        })
```

####  亮点说明

* **MCP 提供类似“无头浏览器”能力**
  能抓到 JS 动态渲染内容，这是 requests 办不到的。

* **可自定义 headers，绕过简单反爬**

* 自动回填到下游清洗模块中

####  输出内容包括：

* 文本
* headers
* status code

---

## **8.4 HTML 清洗器（clean_html）**

```python
def clean_html(self, html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag_name in ["script", "style", "noscript"]:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    for c in soup.find_all(string=lambda text: isinstance(text, Comment)):
        c.extract()

    cleaned = soup.get_text(separator="\n")
    cleaned = "\n".join([line.strip() for line in cleaned.split("\n") if line.strip()])
    return cleaned
```

####  功能亮点

* 删除 `script/style` 等无效标签
* 删除 HTML 注释
* 去除广告与无意义空行
* 输出干净整齐的纯文本

这是网页结构化的关键步骤。

---

## **8.5 ERNIE-4.5 解析器（analyze_content）**

```python
async def analyze_content(self, text):
    client = ErnieBot(
        base_url="https://open.bigmodel.cn/api/paas/v4/",
        api_key="你自己的API KEY",
    )
    response = client.chat.completions.create(
        model="ERNIE-4.5",
        messages=[
            {"role": "system", "content": "你是一名专业网页内容分析助手。"},
            {"role": "user", "content": f"请分析以下内容：\n{text}"}
        ]
    )
    return response.choices[0].message["content"]
```

####  模型完成的任务包括

* 结构化总结
* 信息抽取
* 文本理解
* 意图分析
* 分段解析

这一部分是整个系统的智能核心。

---

### **8.6 保存 Markdown 与分析结果**

保存函数既负责创建目录，也负责文件管理：

```
output/
 ├── markdown/
 │    └── xxx_markdown_xxx.md
 ├── analysis/
 │    └── xxx_analysis_xxx.md
 └── logs/
```

输出统一命名为：

```
域名_路径_时间戳.md
```

这种命名对大规模网页采集非常实用。

---

### **8.7 主流程（fetch → clean → markdown → analyze → save）**

此函数 `scrape(url, question=None)` 是所有流程的入口。

流程如下：

1.  尝试 MCP 抓取网页
2.  MCP 失败 → 使用 requests 补充抓取
3.  清洗 HTML，转换为 Markdown
4.  调用 ERNIE-4.5 分析
5.  保存两份 Markdown（原文与分析）
6.  返回结果给用户

这是整个项目的核心执行逻辑。

---

### **九、实验效果展示**

本节展示系统对某实际网页的处理效果。

---

### **9.1 原始网页（部分 HTML）**
![](https://ai-studio-static-online.cdn.bcebos.com/900cc92d475e49d3aa35d5cfbd52d0ed0f8edce55ac1448888ace41f8aa9e17f)


原始url：https://www.news.cn/politics/leaders/20251111/4dd1b386540d487084d85d639e8b0425/c.html

### **9.2 清洗后的 Markdown（示例）**

![](https://ai-studio-static-online.cdn.bcebos.com/bb611ac91bbe40b6a3c0c399039fac22fa7f0d5a136346579343be272327f555)


文件地址：/home/aistudio/output/markdown/news.cn_politics_leaders_20251111_4dd1b386540d487084d85d639e8b0425_c.html_markdown_20251111_095927.md
---

### **9.3 ERNIE-4.5 分析报告（摘要）**
![](https://ai-studio-static-online.cdn.bcebos.com/12e293c5d80d455a8146fd824eb78f8556574d60aae04a86895e2fca08dcd99d)


文件地址：/home/aistudio/output/analysis/news.cn_politics_leaders_20251111_4dd1b386540d487084d85d639e8b0425_c.html_analysis_20251111_095927.md

---

## **十、使用方式（运行步骤）**

以下为用户直接使用步骤：


####  2. 安装依赖

```
pip install -requirements.txt
```

####  3. 填写你的 ERNIE API KEY

在 `analyze_content()` 中替换：

```
api_key="你的API Key"
```

####  4. 启动主程序并输入 URL

```
python app.py
输入目标网页 URL: https://example.com
```

系统自动完成后续流程。

---

## **十一、项目亮点总结**

本项目具备以下突出优势：

---

####  **1. 通用网页抓取能力（Static + Dynamic 全覆盖）**

结合：

* MCP 远程 Fetch（动态/反爬强网站）
* requests（速度快、轻量）

---

####  **2. HTML → Markdown 自动清洗，适配 AI 输入**

清洗后内容：

* 结构清晰
* 噪声低
* 适合 NLP 模型处理

极大提升大模型的理解效果。

---

####  **3. 基于 ERNIE-4.5 的网页级智能分析**

区别于普通爬虫：

> 本系统不是“下载页面”，而是“理解页面”。

AI 能自动输出：

* 信息抽取
* 页面结构洞察
* 文章摘要
* 表格分析
* 答复用户问题

与传统爬虫相比，智能性是压倒性的。

---
####  **4. 输出双版本文件，适配多种应用场景**

* Markdown（原文）
* Markdown（AI 分析总结）

可直接用于：

* RAG 知识库构建
* 学术研究
* 资讯监控
* 知识图谱
* 数据集整理

---

####  **5. 代码模块化、可读性强、易扩展**

你可以很轻松地添加：

* 新的网页解析策略
* 新的网站适配器
* 新的模型（如 ERNIE-Speed、ERNIE-Tiny）
* 新的数据清洗规则

结构清晰，适合作为课程设计、工程示例、RAG 项目前置任务。

---

## **十二、未来优化方向**

本项目可以继续扩展为更大型的 Web AI 系统，方向包括：

---

####  1. DOM 结构智能识别

通过节点权重判断正文区域，提高抽取精度。

####  2. 反爬机制智能处理

加入 Cookies、Session、Headers 动态模拟。

####  3. 图片 → OCR → 文本解析

将富媒体完全结构化，形成“完整网页知识图谱”。

####  4. 提升动态 JS 页面渲染能力

可加入 Playwright / Selenium 自动渲染接口。

####  5. 多语言页面自动识别与翻译分析

适用于跨国情报分析/国际化 crawler 系统。

---

## **十三、参考文献**


1. BeautifulSoup 文档：[https://www.crummy.com/software/BeautifulSoup/bs4/doc/](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
2. Requests 官方文档：[https://requests.readthedocs.io/](https://requests.readthedocs.io/)
3. Baidu ERNIE Bot API 文档：[https://cloud.baidu.com/product/eb](https://cloud.baidu.com/product/eb)
4. MCP Model Context Protocol 规范：[https://github.com/modelcontextprotocol](https://github.com/modelcontextprotocol)
5. W3C HTML 标准文档：[https://html.spec.whatwg.org/multipage/](https://html.spec.whatwg.org/multipage/)
6. CSDN博主「赋范大模型技术社区」的原创文章：https://blog.csdn.net/fufan_llm/article/details/146377471


## **十四、致谢**
感谢飞桨（PaddlePaddle）团队提供优秀的开源框架和模型，感谢AI Studio平台提供的算力支持。
