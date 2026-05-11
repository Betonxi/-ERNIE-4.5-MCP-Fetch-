# -*- coding: utf-8 -*-
"""
网页抓取助手
使用百度 AI Studio API 和 MCP Fetch 服务器进行网页内容抓取和分析
"""

import json
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any
from openai import OpenAI
import requests
from urllib.parse import urlparse, quote
from bs4 import BeautifulSoup
from markdownify import markdownify as md


class WebScraperAssistant:
    """网页抓取助手类"""
    
    def __init__(self, api_key: str, base_url: str = "https://aistudio.baidu.com/llm/lmapi/v3", output_dir: str = "output"):
        """
        初始化助手
        
        Args:
            api_key: 百度 AI Studio API Key
            base_url: API 基础 URL
            output_dir: 输出文件保存目录
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.mcp_fetch_url = "https://mcp.api-inference.modelscope.net/bd6089df8e0d43/mcp"
        self.output_dir = output_dir
        
        # 创建输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
    def fetch_webpage_direct(self, url: str) -> Optional[Dict[str, Any]]:
        """
        直接使用 requests 抓取网页 HTML 内容（备用方案）
        
        Args:
            url: 要抓取的网页 URL
            
        Returns:
            网页内容字典，包含原始 HTML
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            
            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题
            title = soup.title.string if soup.title else ""
            
            # 返回原始 HTML 和解析后的 soup 对象
            return {
                "title": title,
                "html": response.text,
                "soup": soup,
                "url": url
            }
        except Exception as e:
            return {"error": f"直接抓取失败: {str(e)}"}
    
    def html_to_markdown(self, html: str, soup: Optional[BeautifulSoup] = None) -> str:
        """
        将 HTML 转换为 Markdown 格式
        
        Args:
            html: HTML 内容
            soup: 可选的 BeautifulSoup 对象（如果已解析）
            
        Returns:
            Markdown 格式的内容
        """
        try:
            # 如果提供了 soup 对象，使用它；否则重新解析
            if soup is None:
                soup = BeautifulSoup(html, 'html.parser')
            
            # 移除脚本和样式标签
            for script in soup(["script", "style", "noscript"]):
                script.decompose()
            
            # 移除注释
            from bs4 import Comment
            comments = soup.findAll(string=lambda text: isinstance(text, Comment))
            for comment in comments:
                comment.extract()
            
            # 转换为 Markdown
            markdown_content = md(
                str(soup),
                heading_style="ATX",  # 使用 # 格式的标题
                bullets="-",  # 使用 - 作为列表符号
                strip=['a'],  # 保留链接文本
            )
            
            # 清理多余的空白行
            lines = markdown_content.split('\n')
            cleaned_lines = []
            prev_empty = False
            for line in lines:
                is_empty = not line.strip()
                if not (is_empty and prev_empty):  # 不保留连续的空行
                    cleaned_lines.append(line)
                prev_empty = is_empty
            
            return '\n'.join(cleaned_lines).strip()
            
        except Exception as e:
            return f"转换 Markdown 时发生错误: {str(e)}"
    
    def save_to_file(self, content: str, filename: str, subdir: str = "") -> str:
        """
        保存内容到文件
        
        Args:
            content: 要保存的内容
            filename: 文件名
            subdir: 子目录（可选）
            
        Returns:
            保存的文件路径
        """
        try:
            # 创建子目录（如果指定）
            save_dir = os.path.join(self.output_dir, subdir) if subdir else self.output_dir
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # 确保文件名安全
            safe_filename = "".join(c for c in filename if c.isalnum() or c in ('-', '_', '.'))
            filepath = os.path.join(save_dir, safe_filename)
            
            # 保存文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return filepath
        except Exception as e:
            return f"保存文件失败: {str(e)}"
    
    def generate_filename(self, url: str, suffix: str = "", extension: str = "md") -> str:
        """
        根据 URL 生成文件名
        
        Args:
            url: 网页 URL
            suffix: 文件名后缀（如 "analysis"）
            extension: 文件扩展名
            
        Returns:
            生成的文件名
        """
        try:
            # 解析 URL
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            path = parsed.path.strip('/').replace('/', '_') if parsed.path else 'index'
            
            # 生成基础文件名
            if path == 'index' or not path:
                base_name = domain
            else:
                base_name = f"{domain}_{path}"
            
            # 添加时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 组合文件名
            if suffix:
                filename = f"{base_name}_{suffix}_{timestamp}.{extension}"
            else:
                filename = f"{base_name}_{timestamp}.{extension}"
            
            # 限制文件名长度
            if len(filename) > 200:
                filename = filename[:200] + f".{extension}"
            
            return filename
        except:
            # 如果生成失败，使用默认名称
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            suffix_part = f"_{suffix}" if suffix else ""
            return f"webpage{suffix_part}_{timestamp}.{extension}"
    
    def fetch_webpage(self, url: str, use_mcp: bool = True) -> Optional[Dict[str, Any]]:
        """
        使用 MCP Fetch 服务器或直接方式抓取网页内容
        
        Args:
            url: 要抓取的网页 URL
            use_mcp: 是否优先使用 MCP 服务器
            
        Returns:
            网页内容字典，包含标题、内容等信息
        """
        try:
            # 验证 URL 格式
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return {"error": "无效的 URL 格式"}
            
            # 优先尝试使用 MCP Fetch 服务器
            if use_mcp:
                try:
                    response = requests.post(
                        self.mcp_fetch_url,
                        json={
                            "method": "fetch",
                            "params": {
                                "url": url
                            }
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        # 如果 MCP 返回成功，直接返回
                        if "error" not in result:
                            return result
                except:
                    pass  # MCP 失败，尝试备用方案
            
            # 使用直接抓取作为备用方案
            return self.fetch_webpage_direct(url)
                
        except Exception as e:
            return {"error": f"抓取过程中发生错误: {str(e)}"}
    
    def analyze_content(self, content: str, question: str = "请总结这个网页的主要内容") -> str:
        """
        使用百度 AI Studio API 分析网页内容
        
        Args:
            content: 网页内容
            question: 要询问的问题
            
        Returns:
            AI 分析结果
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": "你是一名面向数据采集任务的专业网页内容分析助手，具备深入理解网页结构、定位关键信息块、识别动态渲染内容、判断噪声与有效文本、并提取结构化数据的能力。在接收到网页内容（HTML、文本或混合数据）后，你需要完成以下任务：1. 深入理解网页结构，包括HTML标签、CSS样式、JavaScript代码等；2. 定位关键信息块，包括标题、段落、列表、表格、图片等；3. 识别动态渲染内容，包括AJAX加载、异步渲染、滚动加载等；4. 判断噪声与有效文本，包括广告、导航栏、版权信息等；5. 提取结构化数据，包括标题、段落、列表、表格、图片等。"
                },
                {
                    "role": "user",
                    "content": f"{question}\n\n网页内容（Markdown 格式）：\n{content[:8000]}"  # 限制内容长度
                }
            ]
            
            chat_completion = self.client.chat.completions.create(
                model="ernie-4.5-21b-a3b",
                messages=messages,
                stream=True,
                extra_body={
                    "penalty_score": 1,
                    "max_completion_tokens": 8000
                },
                temperature=0.8,
                top_p=0.8,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            result = ""
            for chunk in chat_completion:
                if hasattr(chunk.choices[0].delta, "reasoning_content") and chunk.choices[0].delta.reasoning_content:
                    result += chunk.choices[0].delta.reasoning_content
                elif chunk.choices[0].delta.content:
                    result += chunk.choices[0].delta.content
                    
            return result
            
        except Exception as e:
            return f"分析过程中发生错误: {str(e)}"
    
    def scrape_and_analyze(self, url: str, question: str = "请总结这个网页的主要内容") -> Dict[str, Any]:
        """
        抓取网页，转换为 Markdown，然后进行智能分析
        
        Args:
            url: 要抓取的网页 URL
            question: 要询问的问题
            
        Returns:
            包含抓取结果、Markdown 内容和分析结果的字典
        """
        print(f"正在抓取网页: {url}")
        webpage_data = self.fetch_webpage(url)
        
        if "error" in webpage_data:
            return {
                "success": False,
                "error": webpage_data["error"],
                "url": url
            }
        
        # 提取 HTML 内容
        html_content = ""
        soup = None
        title = ""
        
        if isinstance(webpage_data, dict):
            # 优先使用原始 HTML
            html_content = webpage_data.get("html", "")
            soup = webpage_data.get("soup")
            title = webpage_data.get("title", "")
            
            # 如果没有 HTML，尝试从其他字段获取
            if not html_content:
                # 如果 MCP 返回的是其他格式，尝试提取
                html_content = webpage_data.get("content", "")
                if not html_content:
                    html_content = webpage_data.get("text", "")
                if not html_content:
                    # 如果 MCP 返回的是结构化数据，尝试转换为 HTML
                    html_content = json.dumps(webpage_data, ensure_ascii=False, indent=2)
        else:
            html_content = str(webpage_data)
        
        if not html_content:
            return {
                "success": False,
                "error": "未能提取到网页 HTML 内容",
                "url": url
            }
        
        print(f"HTML 内容已抓取，长度: {len(html_content)} 字符")
        print("正在将 HTML 转换为 Markdown...")
        
        # 转换为 Markdown（如果 soup 为 None，html_to_markdown 会重新解析）
        markdown_content = self.html_to_markdown(html_content, soup)
        
        if markdown_content.startswith("转换 Markdown 时发生错误"):
            return {
                "success": False,
                "error": markdown_content,
                "url": url
            }
        
        print(f"Markdown 转换完成，长度: {len(markdown_content)} 字符")
        print("正在使用 AI 分析内容...")
        
        # 使用 Markdown 内容进行分析
        analysis = self.analyze_content(markdown_content, question)
        
        # 保存 Markdown 文件
        markdown_filename = self.generate_filename(url, suffix="markdown", extension="md")
        markdown_filepath = self.save_to_file(markdown_content, markdown_filename, "markdown")
        
        # 保存分析结果文件
        analysis_content = f"""# AI 分析结果

## 网页信息
- **URL**: {url}
- **标题**: {title}
- **抓取时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 问题
{question}

## 分析结果

{analysis}

---
*此分析由百度 AI Studio ERNIE-4.5 模型生成*
"""
        analysis_filename = self.generate_filename(url, suffix="analysis", extension="md")
        analysis_filepath = self.save_to_file(analysis_content, analysis_filename, "analysis")
        
        return {
            "success": True,
            "url": url,
            "title": title,
            "html_length": len(html_content),
            "markdown_length": len(markdown_content),
            "markdown_preview": markdown_content[:500] + "..." if len(markdown_content) > 500 else markdown_content,
            "markdown_content": markdown_content,  # 保存完整的 Markdown 内容
            "markdown_filepath": markdown_filepath,
            "analysis": analysis,
            "analysis_filepath": analysis_filepath
        }


def main():
    """主函数"""
    # API Key - 请替换为您的实际 API Key
    API_KEY = "7b97b5e65d1248169aab2d56f67d2b0fbcb146a2"
    
    # 创建助手实例
    assistant = WebScraperAssistant(api_key=API_KEY)
    
    # 交互式使用
    print("=" * 60)
    print("网页抓取助手")
    print("=" * 60)
    print("输入 'quit' 或 'exit' 退出程序\n")
    
    while True:
        try:
            url = input("请输入要抓取的网页 URL: ").strip()
            
            if url.lower() in ['quit', 'exit', 'q']:
                print("再见！")
                break
            
            if not url:
                print("URL 不能为空，请重新输入。")
                continue
            
            # 可选：询问用户想要分析的问题
            question = input("请输入您的问题（直接回车使用默认问题）: ").strip()
            if not question:
                question = "请总结这个网页的主要内容，包括关键信息和要点。"
            
            # 抓取和分析
            result = assistant.scrape_and_analyze(url, question)
            
            print("\n" + "=" * 60)
            if result["success"]:
                print("✓ 抓取和分析完成！")
                print(f"URL: {result['url']}")
                if result.get('title'):
                    print(f"标题: {result['title']}")
                print(f"HTML 长度: {result['html_length']} 字符")
                print(f"Markdown 长度: {result['markdown_length']} 字符")
                print("\n" + "-" * 60)
                print("文件保存位置:")
                print(f"  Markdown: {result.get('markdown_filepath', 'N/A')}")
                print(f"  分析结果: {result.get('analysis_filepath', 'N/A')}")
                print("-" * 60)
                print("\nMarkdown 内容预览:")
                print(result['markdown_preview'])
                print("\n" + "-" * 60)
                print("AI 分析结果:")
                print("-" * 60)
                print(result['analysis'])
            else:
                print("✗ 抓取失败")
                print(f"错误: {result.get('error', '未知错误')}")
            print("=" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n程序已中断，再见！")
            break
        except Exception as e:
            print(f"\n发生错误: {str(e)}\n")


if __name__ == "__main__":
    main()

