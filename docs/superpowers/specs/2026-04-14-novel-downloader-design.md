# Novel Downloader - 设计文档

## 1. 项目概述

**项目名称**: Novel Downloader（小说下载器）
**项目类型**: Python GUI 应用程序（PyQt/PySide6）
**核心功能**: 在多个小说网站搜索并下载小说，按统一格式存储到本地
**目标用户**: 喜欢阅读网络小说的用户

---

## 2. 架构设计

### 2.1 整体架构（方案 A：单窗口 + 多对话框）

```
┌─────────────────────────────────────────────────────────┐
│  MainWindow（主窗口）                                    │
│  - 搜索栏、类别选择、设置按钮                             │
│  - 结果卡片展示区                                        │
├─────────────────────────────────────────────────────────┤
│  DownloadDialog（下载弹窗，独立窗口）                     │
│  - 进度显示、章节列表、取消/暂停                          │
├─────────────────────────────────────────────────────────┤
│  SettingsDialog（设置弹窗）                              │
│  - 存储根目录设置、类别管理                               │
└─────────────────────────────────────────────────────────┘
```

### 2.2 插件系统

**插件注册机制**: 每个插件实现固定接口，主程序显式导入并注册到 `PluginRegistry`

**插件接口定义** (`core/plugin_interface.py`):

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

@dataclass
class SearchResult:
    title: str           # 书名
    author: str          # 作者
    status: BookStatus   # 状态（使用 BookStatus 枚举）
    url: str             # 书籍详情页URL
    plugin: str          # 来源插件名

@dataclass
class ChapterInfo:
    index: int       # 章节序号
    title: str       # 章节名（原始）
    url: str          # 章节URL

class NovelPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称，如 '3yt'"""
        pass

    @property
    @abstractmethod
    def domain(self) -> str:
        """网站域名，如 'https://www.3yt.org'"""
        pass

    @abstractmethod
    def search(self, keyword: str) -> List[SearchResult]:
        """根据关键字搜索小说"""
        pass

    @abstractmethod
    def get_chapter_list(self, book_url: str) -> List[ChapterInfo]:
        """获取书籍的章节列表"""
        pass

    @abstractmethod
    def get_chapter_content(self, chapter_url: str) -> str:
        """获取单个章节的纯文本内容（不含标题）"""
        pass
```

**插件注册器** (`core/plugin_registry.py`):

```python
class PluginRegistry:
    _instance = None

    def __init__(self):
        self._plugins = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, plugin: NovelPlugin):
        self._plugins[plugin.name] = plugin

    def get_plugin(self, name: str) -> NovelPlugin:
        return self._plugins.get(name)

    def list_plugins(self) -> List[str]:
        return list(self._plugins.keys())
```

### 2.3 核心模块

| 模块 | 路径 | 职责 |
|------|------|------|
| 主窗口 | `ui/main_window.py` | 搜索、卡片展示、发起下载 |
| 下载弹窗 | `ui/download_dialog.py` | 进度显示、章节下载管理 |
| 设置弹窗 | `ui/settings_dialog.py` | 存储目录、类别管理 |
| 插件注册器 | `core/plugin_registry.py` | 插件的注册和获取 |
| 插件接口 | `core/plugin_interface.py` | 抽象基类和数据结构 |
| 下载管理器 | `core/download_manager.py` | 断点续传、任务调度 |
| 配置管理 | `core/config.py` | 用户设置持久化 |

---

## 3. 数据结构

### 3.1 搜索结果

```python
class BookStatus(Enum):
    SERIALIZING = "连载"
    COMPLETED = "完结"
    UNKNOWN = "未知"

@dataclass
class SearchResult:
    title: str           # 书名
    author: str          # 作者
    status: BookStatus   # 状态（枚举值）
    url: str             # 书籍详情页URL
    plugin: str          # 来源插件名
```

> **注意**: 各网站返回的状态字符串不统一，插件层需转换为 `BookStatus` 枚举值。

### 3.2 章节信息

```python
@dataclass
class ChapterInfo:
    index: int       # 章节序号
    title: str       # 章节名（原始）
    url: str          # 章节URL
```

### 3.3 用户配置

```python
@dataclass
class UserConfig:
    root_dir: str                # 存储根目录
    categories: List[str]        # 已有类别列表
    last_category: str          # 上次使用的类别
```

**配置存储位置**: `config.json`（与应用同目录）

### 3.4 书籍信息（内存中）

```python
@dataclass
class BookInfo:
    title: str           # 书名
    author: str          # 作者
    url: str             # 详情页URL
    plugin: str          # 来源插件
    save_path: str       # 保存路径
```

---

## 4. 界面设计

### 4.1 主窗口布局

```
┌─────────────────────────────────────────────────────────┐
│ [设置] [刷新插件]                    存储: E:\novel     │
├─────────────────────────────────────────────────────────┤
│  类别: [玄幻 ▼] [+ 新增]                                │
│  书名: [_______________] [搜索]                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐               │
│  │ 书名    │  │ 书名    │  │ 书名    │               │
│  │ 作者    │  │ 作者    │  │ 作者    │               │
│  │ 状态    │  │ 状态    │  │ 状态    │               │
│  │ [来源]  │  │ [来源]  │  │ [来源]  │               │
│  └─────────┘  └─────────┘  └─────────┘               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 4.2 卡片样式

- 固定宽度: 200px
- 显示: 书名（加粗）、作者、状态、来源网站
- 双击: 打开下载弹窗

### 4.3 下载弹窗布局

```
┌─────────────────────────────────────────┐
│ 正在下载: 凡人修仙传                    │
├─────────────────────────────────────────┤
│ 进度: ████████░░░░░░░░ 45/120 章       │
│ 速度: 2.3 KB/s  预计: 3分钟            │
├─────────────────────────────────────────┤
│ 第1章 黄皮葫芦        ✓ 已完成          │
│ 第2章 葫芦里的...     ✓ 已完成          │
│ 第3章 初入江湖         下载中...        │
│ 第4章 ...              等待中           │
│ ...                                      │
├─────────────────────────────────────────┤
│              [取消]  [后台下载]          │
└─────────────────────────────────────────┘
```

### 4.4 设置弹窗布局

```
┌─────────────────────────────────────────┐
│ 设置                                  [X]│
├─────────────────────────────────────────┤
│ 存储目录:                               │
│ [E:\novel_______________] [浏览]       │
├─────────────────────────────────────────┤
│ 类别管理:                               │
│ ┌───────────────────────────┐          │
│ │ 玄幻                       │          │
│ │ 都市                       │          │
│ │ 科幻                       │          │
│ └───────────────────────────┘          │
│ [+ 新增] [删除]                         │
├─────────────────────────────────────────┤
│              [保存]  [取消]             │
└─────────────────────────────────────────┘
```

---

## 5. 存储格式

**目录结构**:
```
{root_dir}/
└── {category}/           # 用户选择的类别
    └── {book_name}/       # 书名
        ├── 第x章 {章节名1}.txt
        ├── 第x章 {章节名2}.txt
        └── ...
```

**示例**:
```
E:\novel\
└── 玄幻\
    └── 凡人修仙传\
        ├── 第1章 黄皮葫芦.txt
        ├── 第2章 葫芦里的秘密.txt
        └── ...
```

**章节命名规则**:
- 直接使用爬取的章节名
- **去重逻辑**: 如果章节名**完全以**"第x章"开头（如"第1章 黄皮葫芦"），则去掉重复的前缀部分，仅保留"黄皮葫芦"
- **文件名安全**: 移除非法字符 `\/:*?"<>|` 替换为下划线 `_`
- **文件编码**: UTF-8
- 文件扩展名: `.txt`

---

## 6. 下载流程

### 6.1 搜索流程

1. 用户输入书名关键字，选择插件（默认全部）
2. 调用各插件 `search(keyword)`
3. 聚合结果，渲染卡片列表

### 6.2 下载流程

1. 双击卡片 → 弹出 DownloadDialog
2. 调用 `plugin.get_chapter_list(url)` 获取章节列表
3. 显示章节列表，初始化进度
4. 逐章调用 `plugin.get_chapter_content(url)` 下载
5. 保存到 `{root}/{category}/{bookname}/第x章 {title}.txt`
6. 更新进度显示
7. 下载完成 → 关闭窗口

### 6.3 断点续传

- 在书名目录下创建 `.download_meta.json` 记录已下载章节
- 下载开始时读取，跳过已下载章节
- 下载完成后删除该文件

**元数据格式**:
```json
{
  "book_url": "https://...",
  "plugin": "3yt",
  "downloaded_chapters": {
    "1": "黄皮葫芦",
    "2": "葫芦里的秘密",
    "3": "初入江湖"
  },
  "total_chapters": 120,
  "last_updated": "2026-04-14T20:30:00"
}
```

---

### 6.4 文件名安全处理

```python
def sanitize_filename(name: str) -> str:
    """移除或替换文件名中的非法字符"""
    illegal_chars = '\\/:*?"<>|'
    for char in illegal_chars:
        name = name.replace(char, '_')
    return name.strip()
```

## 7. 错误处理

| 场景 | 处理方式 |
|------|----------|
| 网络请求失败 | 重试3次，间隔2秒，仍失败记录错误继续 |
| 网络超时 | 单次请求超时 30 秒 |
| 章节内容为空 | 跳过该章节，记录日志 |
| 磁盘空间不足 | 弹出警告，停止下载 |
| 插件加载失败 | 跳过该插件，提示用户 |
| 下载中断 | 保存进度，下次启动自动续传 |

---

## 8. 插件开发规范

### 8.1 插件文件结构

```
plugins/
├── __init__.py
├── base_plugin.py
├── plugin_3yt.py
├── plugin_69shuba.py
└── plugin_92yq.py
```

### 8.2 插件注册示例

```python
# plugins/plugin_3yt.py
from core.plugin_interface import NovelPlugin, SearchResult, ChapterInfo

class Plugin3yt(NovelPlugin):
    @property
    def name(self) -> str:
        return "3yt"

    @property
    def domain(self) -> str:
        return "https://www.3yt.org"

    def search(self, keyword: str) -> List[SearchResult]:
        # 实现搜索逻辑
        ...

    def get_chapter_list(self, book_url: str) -> List[ChapterInfo]:
        # 实现章节列表获取
        ...

    def get_chapter_content(self, chapter_url: str) -> str:
        # 实现章节内容获取
        ...

# 注册插件
from core.plugin_registry import PluginRegistry
PluginRegistry.get_instance().register(Plugin3yt())
```

### 8.3 主程序加载插件

**动态插件发现机制**:
```python
# main.py
import os
import importlib
from pathlib import Path

plugins_dir = Path(__file__).parent / "plugins"
for plugin_file in plugins_dir.glob("plugin_*.py"):
    module_name = f"plugins.{plugin_file.stem}"
    importlib.import_module(module_name)
```

**插件文件命名规范**: `plugin_{name}.py`，如 `plugin_3yt.py`、`plugin_69shuba.py`

**插件注册约定**: 每个插件文件在加载时必须调用 `PluginRegistry.get_instance().register(PluginXxx())`

---

## 9. 技术栈

| 组件 | 技术选择 |
|------|----------|
| GUI 框架 | PySide6 |
| HTTP 请求 | requests |
| HTML 解析 | BeautifulSoup4 |
| 配置存储 | JSON (config.json) |
| 日志 | logging + colorlog |

---

## 10. 目录结构

```
novel-downloader/
├── main.py                    # 应用入口
├── config.json                # 用户配置
├── requirements.txt           # 依赖
├── core/
│   ├── __init__.py
│   ├── plugin_interface.py    # 插件抽象接口
│   ├── plugin_registry.py     # 插件注册器
│   ├── download_manager.py    # 下载管理器
│   ├── config.py              # 配置管理
│   └── utils.py              # 工具函数（sanitize_filename 等）
├── ui/
│   ├── __init__.py
│   ├── main_window.py         # 主窗口
│   ├── download_dialog.py     # 下载弹窗
│   ├── settings_dialog.py     # 设置弹窗
│   └── card_widget.py         # 搜索结果卡片
├── plugins/
│   ├── __init__.py
│   ├── base_plugin.py
│   ├── plugin_3yt.py
│   ├── plugin_69shuba.py
│   └── plugin_92yq.py
└── docs/
    └── specs/
        └── 2026-04-14-novel-downloader-design.md
```

**requirements.txt 依赖**:
```
PySide6>=6.6.0
requests>=2.31.0
beautifulsoup4>=4.12.0
colorlog>=5.0.0
```
