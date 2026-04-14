# 网站地址
https://www.3yt.org/

# 搜索流程
打开网站 https://www.3yt.org/

步骤1：在如下输入框，输入书名：
```html
<input class="search" id="bdcsMain" name="searchkey" type="text" maxlength="30" value="可搜书名和作者，请您少字也别输错字。" title="请正确输入" onfocus="this.style.color = '#000000';this.focus();if(this.value=='可搜书名和作者，请您少字也别输错字。'){this.value='';}" ondblclick="javascript:this.value=''" style="color: rgb(0, 0, 0);">
```

步骤2：点击搜索按钮
```html
<input type="submit" class="searchBtn" value="搜索" title="搜索">
```

步骤3：解析弹出窗口页面
点击搜索按钮后，会弹出搜索结果页面，url类似：
```
https://www.3yt.org/search/94/1.html
```

在如下的页面可以获取搜索结果：
```html

<div id="sitembox">
    <dl>
        <dt><a href="/ml/213930/"><img src="https://img.3yt.org/213930/222024.jpg" alt="我不是戏神" height="150" width="120"></a></dt>
        <dd><h3><a href="/ml/213930/">我不是戏神</a></h3></dd>
        <dd class="book_other">作者：<span>三九音域</span>状态：<span>已完结</span>分类：<span>都市</span>字数：<span>786万字</span></dd>
        <dd class="book_des">
            赤色流星划过天际后，人类文明陷入停滞。从那天起，人们再也无法制造一枚火箭，一颗核弹，一架飞机，一台汽车……近代科学堆砌而成的文明金字塔轰然坍塌，而灾难，远不止此。灰色的世界随着赤色流星降临，像是镜面后的鬼魅倒影，将文明世界一点点拖入无序的深渊。在这个时代，人...
        </dd>
        <dd class="book_other">最新章节：<a href="/ml/213930/151017439.html">第1892章 崩解，与五分之一</a> 更新时间：<span>2026-04-14 22:38</span>
        </dd>
    </dl>
    <dl>
        <dt><a href="/ml/318183/"><img src="https://img.3yt.org/318183/299711.jpg" alt="戏神：我不是死神" height="150" width="120"></a></dt>
        <dd><h3><a href="/ml/318183/">戏神：我不是死神</a></h3></dd>
        <dd class="book_other">作者：<span>启宇</span>状态：<span>已完结</span>分类：<span>游戏</span>字数：<span>360万字</span></dd>
        <dd class="book_des">
            [戏神同人+单男主+无女主+无系统+改变原着遗憾+非穿越者】在戏神世界，一共有十四条通神道路，但在更古老的时代，其实一共有十八条，在时代的演变中，有四条神道被世界所遗落，其中一条，便是死神道......深红色的斗篷随风飘扬，少年伫立在黑暗深渊之上，猩红色的双...
        </dd>
        <dd class="book_other">最新章节：<a href="/ml/318183/150354910.html">第639章 如果还是不行，那我就陪他，一起坠入深渊</a> 更新时间：<span>2026-03-12 15:29</span></dd>
    </dl>
    <div class="clear"></div>
</div>
```

需要提取出书名，作者，简介，类别等信息，最重要的是a标签里面的链接：<a href="/ml/318183/">，这个表示作品的详情页面


# 下载流程

步骤1：获取章节列表
根据搜索结果获取到的a标签的链接，使用 HTTP GET 获取链接的HTML内容：
```
https://www.3yt.org/ml/213930/
```

章节列表，在如下节点里：
```html

<div id="list">
    <dl>
        <dt> 《我不是戏神》的结局（提示：已启用缓存技术，最新章节可能会延时显示，登录书架即可实时查看。）</dt>
        <dd><a href="/ml/213930/151017439.html">第1892章 崩解，与五分之一</a></dd>
        <dd><a href="/ml/213930/151001826.html">第1891章 高压锅</a></dd>
        <dt><b>《我不是戏神》正文</b><a href="https://www.3yt.org/txt/213930.html">我不是戏神txt全文下载</a></dt>
        <dd><a href="/ml/213930/102812715.html">第1章 戏鬼回家</a></dd>
        <dd><a href="/ml/213930/102812717.html">第2章 我们在看着你</a></dd>
        <dd><a href="/ml/213930/102812718.html">第3章 灾厄</a></dd>
        <dd><a href="/ml/213930/102812719.html">第4章 它们存在</a></dd>
        <dd><a href="/ml/213930/102812720.html">第5章 灰界</a></dd>
        <dd><a href="/ml/213930/102812721.html">第6章 《陈氏编导法则》</a></dd>
        <dd><a href="/ml/213930/102812722.html">第7章 全区封锁</a></dd>
        <dd><a href="/ml/213930/102812723.html">第8章 杀局</a></dd>
    </dl>
</div>
```

注意，需要跳过<dt>前面的章节，从最后一个<dt>标签之后的<dd>标签开始。


步骤2：下载所有章节
获取到章节列表里面，每个章节的链接，如`/ml/213930/102812715.html`，打开链接：
```
https://www.3yt.org/ml/213930/102812715.html
```
获取HTML内容，在如下节点里，获取章节内容：
```html
<div id="content" style="font-size: 24px;">
    <p>“我……是谁？”</p>
    <p> 轰隆——</p>
    <p> 苍白的雷光闪过如墨云层，</p>
    <p> 雨流狂落，神怒般的雷雨浇灌在泥泞大地，涟漪层叠的水洼倒影中，一道朱红色的人影支离破碎。</p>
    <p> 那是位披着大红戏袍的少年，他好似醉酒般踉跄淌过满地泥泞，宽大的袖摆在狂风中飘舞，戏袍表面的泥沙被雨水冲落，那抹似血的鲜红在黑夜中触目惊心。</p>
    <p> 喜欢我不是戏神请大家收藏：(www.suyingwang.net)我不是戏神三月天更新速度全网最快。</p>
</div>
```

可以并发打开每个章节的链接，获取到章节的内容。

# 清洗流程

获取到章节内容后，需要将带有 `www.suyingwang.net` 或 `三月天更新速度全网最快` 关键字的段落删除。