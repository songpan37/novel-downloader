# 网站地址
https://www.bqg655.cc


# HTTP请求流程

## 搜索流程

调用API获取书本详情。 请求格式：

GET https://www.bqg655.cc/api/search?q={书名}

响应样例：
```json
{
  "data": [
    {
      "id": "144571",
      "title": "玄鉴仙族",
      "author": "季越人",
      "intro": "陆江仙熬夜猝死，残魂却附在了一面满是裂痕的青灰色铜镜上，飘落到了浩瀚无垠的修仙世界。凶险难测的大黎"
    }
  ],
  "title": "搜索结果"
}
```


# 下载流程

步骤1：获取书本详情：

请求格式：

GET https://www.bqg655.cc/api/book?id={书本ID}

其中：
`书本ID` 为上一步响应体中的 `id` 字段。

响应样例：
```json
{
  "id": "144571",
  "title": "玄鉴仙族",
  "sortname": "女生",
  "author": "季越人",
  "full": "连载",
  "intro": "陆江仙熬夜猝死，残魂却附在了一面满是裂痕的青灰色铜镜上，飘落到了浩瀚无垠的修仙世界。凶险难测的大黎",
  "lastchapterid": "1607",
  "lastchapter": "第1461章 恨此宫",
  "lastupdate": "2026-04-19",
  "dirid": "144571"
}
```


步骤2：下载章节内容

请求格式：

GET https://www.bqg655.cc/api/chapter?id={书本ID}&chapterid={章节序号}

`书本ID` 和上一步相同，`章节序号` 是从 1 开始，一直到上一步返回的 `lastchapterid` 字段值。例如，上一步返回的 `lastchapterid` 是 1607，那么说明有1607个章节，chapterid 就是 1 - 1607。

响应样例：
```json
{
  "id": "144571",
  "chapterid": "1",
  "dirid": "144571",
  
  "title": "玄鉴仙族",
  "author": "季越人",
  "chaptername": "第1469章 蝉雀（1+1\/2）（潜龙勿用加更45\/113）",
  "cs": 1607,
  "time": 0,
  "txt": "淅沥沥的小雨从灰色苍穹之上坠落，轻飘飘的淋在城市街道上。或者跳过本章点击下一章继续阅读……"
}

```

其中：
`chaptername` 表示章节名，`txt` 表示章节正文



---


# playwright 流程

## 搜索流程
直接打开搜索结果网站： https://www.bqg655.cc/s?q={书名等搜索关键字}

从如下节点，获取搜索结果：
```html

<div class="wrap">
    <div class="so_list bookcase">
        <h2>与“
            <script>document.writeln(q);</script>
            夜的命名术
            ”相关的小说 - <font size="2px">(最多显示100条)</font></h2>
        <div class="type_show">
            <div class="bookbox">
                <div class="box">
                    <div class="bookimg"><a href="/book/1000/"><img src="https://www.bqg655.cc/bookimg/3/3583.jpg"></a></div>
                    <div class="bookinfo"><h4 class="bookname"><a href="/book/1000/">夜的命名术</a></h4>
                        <div class="author">作者：会说话的肘子</div>
                        <div class="uptime">
                            　　蓝与紫的霓虹中，浓密的钢铁苍穹下，数据洪流的前端，是科技革命之后的世界，也是现实与虚幻的分界。　　钢铁与身体，过去与……
                        </div>
                    </div>
                </div>
            </div>
            <div class="bookbox">
                <div class="box">
                    <div class="bookimg"><a href="/book/90601/"><img src="https://www.bqg655.cc/bookimg/88/88098.jpg"></a></div>
                    <div class="bookinfo"><h4 class="bookname"><a href="/book/90601/">夜的命名术</a></h4>
                        <div class="author">作者：会说话的肘子著</div>
                        <div class="uptime">
                            笔趣阁提供会说话的肘子写的夜的命名术最新章节，并为您提供夜的命名术全文阅读，夜的命名术VIP章节以及阅读服务。……
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

需要提取出书本ID，书名，作者，简介，类别等信息，最重要的是a标签里面的链接：<a href="/book/1000/">，这个表示作品的详情页面，`/book/1000/`里面，book后面的数字1000表示书本ID。

## 下载流程

步骤1：获取章节列表
根据搜索结果获取到的a标签的链接，使用 HTTP GET 获取链接的HTML内容：
```
https://www.bqg655.cc/book/1000/
```

章节列表，在如下节点里：
```html
<div class="listmain">
	<dl>
		<dt>夜的命名术最新章节列表</dt>
		<dd><a href="/book/1000/1.html">1、想等的人</a></dd>
		<dd><a href="/book/1000/2.html">2、倒计时</a></dd>
	</dl>
</div>
```

步骤2：下载所有章节
获取到章节列表里面，每个章节的链接，如 https://www.bqg655.cc/book/1000/1.html 打开链接：
```
https://www.bqg655.cc/book/1000/1.html
```
获取HTML内容，在如下节点里，获取章节内容：
```html

<div id="chaptercontent" class="Readarea ReadAjax_content" style="font-size: 20px;">
    　　第一卷。<br><br>　　
    夜的第一章：奏鸣。<br><br>　　
    ……<br><br>　　2022年，秋。<br><br>　　
    淅沥沥的小雨从灰色苍穹之上坠落，轻飘飘的淋在城市街道上。
    <br><br>　　时值秋季，时不时还能看到没打伞的行人，用手挡在头顶匆匆而过。<br><br>　　
    狭窄的军民胡同里，正有一个十七八岁的少年，与一位老爷子对坐在超市小卖部旁边的雨棚下面。<br><br>　　
    雨棚之外的全世界灰暗，地面都被雨水沁成了浅黑色，只有雨棚下的地面还留着一片干燥地带，就像是整个世界都只剩下这一块净土。<br><br>　　
    他们面前摆着一张破旧的木质象棋盘，头顶上是红色的‘福来超市’招牌。<br><br>　　“将军，”少年庆尘说完便站起身来，留下头发稀疏的老头呆坐着。<br><br>　　
    少年庆尘看了对方一眼平静说道：“不用挣扎了。”<br><br>　　“我还可以……”老头不甘心的说道：“这才下到十三步啊……”<br><br>　　 
    请收藏本站：https://www.bqg78.com
    手机版：https://m.bqg78.com <br><br>
    <div class="readinline">
        <a class="ll" href="javascript:chapter_error(3583,1,'1、想等的人',1770999011)">『点此报错』</a>
        <a class="rr" href="javascript:addBookMark(3583,1,'夜的命名术','1、想等的人');">『加入书签』</a>
    </div>
</div>
```

## 清洗流程

获取到章节内容后，需要将带有 `请收藏本站：` 或 `手机版：` 关键字的段落删除。