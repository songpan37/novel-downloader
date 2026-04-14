"""Utility functions for novel downloader"""

import re


def sanitize_filename(name: str) -> str:
    """移除或替换文件名中的非法字符"""
    illegal_chars = '\\/:*?"<>|'
    for char in illegal_chars:
        name = name.replace(char, '_')
    return name.strip()


def remove_duplicate_chapter_prefix(title: str) -> str:
    """
    如果章节名完全以'第x章 '开头，则去掉重复的前缀部分

    例如: "第1章 黄皮葫芦" -> "黄皮葫芦"
    但: "第1章黄皮葫芦" (无空格) 保持不变
    """
    pattern = r'^第(\d+)章\s+'
    match = re.match(pattern, title)
    if match:
        return title[match.end():]
    return title
