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


def chinese_to_arabic(chinese_num: str) -> int:
    """
    将中文数字转换为阿拉伯数字

    支持: 零/〇, 一/壹, 二/贰, 三/叁, 四/肆, 五/伍,
          六/陆, 七/柒, 八/捌, 九/玖, 十, 百, 千, 万, 亿

    例如:
        "一千六百二十四" -> 1624
        "第一章" -> 1
        "第十章" -> 10
        "第二十三章" -> 23
        "第一百零五章" -> 105
    """
    if not chinese_num:
        return 0

    # 符号映射
    digit_map = {
        '零': 0, '〇': 0,
        '一': 1, '壹': 1, '幺': 1,
        '二': 2, '贰': 2,
        '三': 3, '叁': 3,
        '四': 4, '肆': 4,
        '五': 5, '伍': 5,
        '六': 6, '陆': 6,
        '七': 7, '柒': 7,
        '八': 8, '捌': 8,
        '九': 9, '玖': 9,
    }

    unit_map = {
        '十': 10,
        '百': 100,
        '千': 1000,
        '万': 10000,
        '亿': 100000000,
    }

    chinese_num = chinese_num.strip()

    # 处理纯阿拉伯数字的情况
    try:
        return int(chinese_num)
    except ValueError:
        pass

    # 从右到左解析
    result = 0
    temp = 0
    unit = 1

    i = len(chinese_num) - 1
    while i >= 0:
        char = chinese_num[i]

        if char in digit_map:
            val = digit_map[char]
            if val == 0:
                # 零直接跳过，但如果有待处理的temp值，先加上
                i -= 1
                continue
            temp += val * unit
        elif char in unit_map:
            u = unit_map[char]
            if u >= 10000:
                # 万或亿作为独立单元
                result += temp * u
                temp = 0
                unit = 1
            else:
                # 十百千乘以temp
                if temp == 0:
                    temp = 1  # 十 without preceding number means 10
                temp = temp * u
                unit = 1
        else:
            i -= 1
            continue

        i -= 1

    result += temp
    return result


def extract_chapter_number(title: str) -> int:
    """
    从章节标题中提取章号（仅支持阿拉伯数字格式）

    格式: 第x章
    例如: "第1章" -> 1, "第23章" -> 23
    """
    match = re.search(r'第(\d+)章', title)
    if match:
        return int(match.group(1))
    return 0
