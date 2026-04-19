# 并发搜索与下载架构

## 需求背景

当前实现存在以下问题：

1. **搜索串行执行** - 多个插件的搜索是串行的，总耗时 = 所有插件耗时之和
2. **下载共用插件实例** - 所有下载共用同一个插件实例，导致共用同一个浏览器/HTTP连接
3. **下载窗口阻塞主界面** - 下载窗口使用模态对话框，阻塞主界面操作

## 目标

1. **搜索并发** - 多插件搜索同时进行，总耗时 = max(各插件耗时)
2. **下载完全独立** - 每本小说的下载使用独立的插件实例、独立的浏览器/连接
3. **界面保持可交互** - 主界面不阻塞，可同时进行搜索和多个下载

## 架构设计

### 当前架构

```
主界面 (阻塞等待)
├── 搜索 → 3yt搜索(串行) → 92yq搜索(串行)
│
└── 下载1 → Registry.get_plugin() → 共享单例插件 → 共享浏览器

问题：插件是单例，所有下载共用同一个浏览器实例
```

### 修改后架构

```
主界面 (可交互)
├── 搜索 → ThreadPoolExecutor → 3yt搜索线程(独立) + 92yq搜索线程(独立)
│                          ↓
│                     并发执行，互不阻塞
│
└── 下载1 → 新插件实例1 → 新浏览器1 → DownloadDialog1(独立窗口)
    下载2 → 新插件实例2 → 新浏览器2 → DownloadDialog2(独立窗口)
    下载3 → 新插件实例3 → 新浏览器3 → DownloadDialog3(独立窗口)

每个下载完全独立，窗口之间互不影响
```

## 实现方案

### 1. 搜索并发

使用 `concurrent.futures.ThreadPoolExecutor` 实现：

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def on_search(self):
    plugin_names = self.plugin_registry.list_plugins()

    with ThreadPoolExecutor(max_workers=len(plugin_names)) as executor:
        future_to_plugin = {
            executor.submit(plugin.search, keyword): plugin
            for plugin in self.plugin_registry.list_plugins()
        }

        for future in as_completed(future_to_plugin):
            plugin_name = future_to_plugin[future]
            try:
                results = future.result()
                # 处理结果
            except Exception as e:
                # 处理错误
```

### 2. 下载独立

每本小说的下载创建独立的插件实例：

```python
# MainWindow 中
def on_download_clicked(self, result):
    # 为这本小说创建独立的插件实例
    plugin = self._create_plugin_instance(result.plugin)

    dialog = DownloadDialog(
        result=result,
        download_manager=self.download_manager,
        config_manager=self.config_manager,
        plugin=plugin  # 传入独立插件实例
    )
    dialog.show()  # 非阻塞显示

# DownloadDialog 中
def __init__(self, result, download_manager, config_manager, plugin):
    self.plugin = plugin  # 保存独立插件实例

# DownloadWorker 中
def run(self):
    # 直接使用传入的插件实例，不从Registry获取
    plugin = self.plugin
```

### 3. 插件实例工厂

```python
def _create_plugin_instance(self, plugin_name):
    """为每本小说创建独立的插件实例"""
    if plugin_name == '3yt':
        return Plugin3yt(headless=False, slow_mo=100)
    elif plugin_name == '92yq':
        return Plugin92yq()
    # 其他插件...
```

### 4. 窗口非阻塞

```python
def on_download_clicked(self, result):
    dialog = DownloadDialog(...)
    dialog.show()  # 改为show()而非exec()
```

## 插件实例生命周期

### 3yt 插件
- 每个下载任务创建新的 `Plugin3yt` 实例
- 每个实例有独立的 Playwright 浏览器
- 下载完成后，关闭浏览器，清理实例

### 92yq 插件
- 每个下载任务创建新的 `Plugin92yq` 实例
- HTTP 请求是独立的，无需特殊处理

## 文件修改清单

| 文件 | 修改内容 |
|------|---------|
| `ui/main_window.py` | 1. 搜索改为并发执行<br>2. `on_download_clicked` 创建独立插件实例 |
| `ui/download_dialog.py` | 1. 接收独立插件实例<br>2. 传递给 DownloadWorker |
| `plugins/plugin_3yt.py` | 添加工厂方法 `create_instance()` |
| `plugins/plugin_92yq.py` | 添加工厂方法 `create_instance()` |

## 注意事项

1. **资源清理** - 下载完成后需关闭浏览器实例，避免资源泄露
2. **错误处理** - 并发任务需要有独立的错误处理机制
3. **窗口管理** - 多个下载窗口需要能独立管理
4. **线程安全** - UI更新需在主线程执行（使用信号槽机制）

## 进度展示

下载进度通过信号槽机制更新到各个窗口：
- `progress(int, int)` - 总进度
- `chapter_status(int, str)` - 章节状态
- `finished()` - 下载完成
- `error(str)` - 下载错误

每个 DownloadDialog 连接自己的信号槽，互不干扰。
