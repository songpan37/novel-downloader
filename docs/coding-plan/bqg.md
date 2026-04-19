# 网站地址
https://www.bqgcp.cc/

# 搜索流程
直接打开搜索结果网站： https://www.bqgcp.cc/s?q={书名等搜索关键字}

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
                    <div class="bookimg"><a href="/book/1000/"><img src="https://www.bqgcp.cc/bookimg/3/3583.jpg"></a></div>
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
                    <div class="bookimg"><a href="/book/90601/"><img src="https://www.bqgcp.cc/bookimg/88/88098.jpg"></a></div>
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

需要提取出书名，作者，简介，类别等信息，最重要的是a标签里面的链接：<a href="/book/1000/">，这个表示作品的详情页面


# 下载流程

步骤1：获取章节列表
根据搜索结果获取到的a标签的链接，使用 HTTP GET 获取链接的HTML内容：
```
https://www.bqgcp.cc/book/1000/
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
获取到章节列表里面，每个章节的链接，如 https://www.bqgcp.cc/book/1000/1.html 打开链接：
```
https://www.bqgcp.cc/book/1000/1.html
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

# 清洗流程

获取到章节内容后，需要将带有 `请收藏本站：` 或 `手机版：` 关键字的段落删除。