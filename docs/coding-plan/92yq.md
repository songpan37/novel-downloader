# 网站地址
https://www.92yanqing.com/

# 搜索流程
直接打开搜索结果网站： https://www.92yanqing.com/s/?searchkey={书名等搜索关键字}

从如下节点，获取搜索结果：
```html
<div class="container">
    <ol class="breadcrumb">
        <li><a href="https://www.92yanqing.com" title="就爱言情小说网">就爱言情小说网</a></li>
        <li>小说搜索</li>
        <li class="active">高武纪元</li>
        <div class="clear"></div>
    </ol>
    <div class="ranklist mt10">
        <h4>与“高武纪元”有关的小说</h4>
        <div class="content">
            <dl>
                <a href="/read/99989/" class="cover" title="高武纪元：开局加载田伯光模板"><img src="https://img.92txt.cc/image/99/99979/99979s.jpg" alt="高武纪元：开局加载田伯光模板"></a>
                <dt><a href="/read/99989/" title="高武纪元：开局加载田伯光模板">高武纪元：开局加载田伯光模板</a></dt>
                <dd></dd>
                <dd><a href="/author/%E4%BD%9A%E5%90%8D/">佚名</a><span>连载</span><span>361万字</span></dd>
            </dl>
            <dl>
                <a href="/read/92572/" class="cover" title="高武纪元：开局悟性增幅十万倍"><img src="https://img.92txt.cc/image/92/92562/92562s.jpg" alt="高武纪元：开局悟性增幅十万倍"></a>
                <dt><a href="/read/92572/" title="高武纪元：开局悟性增幅十万倍">高武纪元：开局悟性增幅十万倍</a></dt>
                <dd> 【高武+觉醒转职+重生+武道+復仇+斩神】 神弃元年，世界各地深渊降临，天道游戏融合现实，存活者天赋觉醒，走上登神之路。
                    深渊魔物肆虐，秘境副本，装备，技能数不胜数。唯有转职者升级变强才能抵抗深渊。 神弃三百年，自称神的存在走出了深渊，宣告末日降临……
                    …… 转职当天，穿越者姜源觉醒天赋——无限增幅！ 【开局悟性增幅十万倍！升级为SSS级天赋—至高解析】
                    【你解析基础呼吸法，创造混沌呼吸法，修炼
                </dd>
                <dd><a href="/author/%E4%BD%9A%E5%90%8D/">佚名</a><span>连载</span><span>120万字</span></dd>
            </dl>
            <dl>
                <a href="/read/76380/" class="cover" title="高武纪元"><img src="https://img.92txt.cc/image/76/76370/76370s.jpg" alt="高武纪元"></a>
                <dt><a href="/read/76380/" title="高武纪元">高武纪元</a></dt>
                <dd> 从南洋深海中飞起的黑龙，掀起灭世海啸……火焰魔灵毁灭一座座钢筋水泥城市，于核爆中心安然离去……域外神明试图统治整片星海……
                    这是人类科技高度发达的未来世界。 也是掀起生命进化狂潮的高武纪元。 即将高考的武道学生李源，心怀能观想星海的奇异神宫，在这个世界艰难前行。
                    多年以后。 “我现在的飞行速度是32682米/每秒，力量爆发是……”李源在距蓝星表层约180公里的大气层中极速飞行，冰冷眸子盯着昏暗虚
                </dd>
                <dd><a href="/author/%E7%83%BD%E4%BB%99/">烽仙</a><span>连载</span><span>437万字</span></dd>
            </dl>
        </div>
        <div class="clear"></div>
    </div>
</div>
```

需要提取出书名，作者，简介，类别等信息，最重要的是a标签里面的链接：<a href="/read/99989/">，这个表示作品的详情页面


# 下载流程

步骤1：获取章节列表
根据搜索结果获取到的a标签的链接，使用 HTTP GET 获取链接的HTML内容：
```
https://www.92yanqing.com/read/76380/
```

章节列表，在如下节点里：
```html

<div class="chapterlist mt10">
    <div class="all">
        <h3>目录</h3>
        <ul>
            <li><a href="https://www.92yanqing.com/read/76380/37623034.html" title="第1章 李源" rel="chapter">第1章 李源</a></li>
            <li><a href="https://www.92yanqing.com/read/76380/37623036.html" title="第2章 身体素质6.5级" rel="chapter">第2章 身体素质6.5级</a></li>
            <li><a href="https://www.92yanqing.com/read/76380/37623039.html" title="第3章 未觉醒的高等灵性" rel="chapter">第3章 未觉醒的高等灵性</a></li>
        </ul>
    </div>
    <div class="clear"></div>
</div>
```

步骤2：下载所有章节
获取到章节列表里面，每个章节的链接，如 `https://www.92yanqing.com/read/76380/37623034.html` 打开链接：
```
https://www.92yanqing.com/read/76380/37623034.html
```
获取HTML内容，在如下节点里，获取章节内容：
```html

<div class="container">
    <!--面包屑-->
    <ol class="breadcrumb">
        <li><a href="https://www.92yanqing.com">就爱言情小说网</a></li>
        <li><a href="https://www.92yanqing.com/list/1-1.html">玄幻魔法</a></li>
        <li><a href="https://www.92yanqing.com/read/76380/" title="高武纪元">高武纪元</a></li>
        <li class="active">第1章 李源</li>
        <div class="pull-right"></div>
        <div class="clear"></div>
    </ol>

    <div class="read mt10">
        <h1>第1章 李源（1/2）</h1>
        <div class="readpage">
            <a rel="prev" href="javascript:void(0);" class="gray">没有了</a> <a href="/read/76380/" rel="index">目录</a>
            <a href="javascript:addbookcase('76380','高武纪元','37623034','第1章 李源');" class="addbookcase">加书签</a>
            <a rel="next" href="/read/76380/37623034_2.html">下一页</a>
        </div>
        <div class="content">
            <div id="booktxt">
                <p> 七星历2042年九月，夏国，江北省，江城。</p>
                <p> 有着火炉之称的城市，一年多是冬夏，九月初正是炎热时。</p>
                <p> 关山区第一高中。</p>
                <p> 高三教学楼的每间教室的后黑板上，都挂着颇为相似的横幅，‘不拼不搏，高三白活’‘拼一年春夏秋冬，博一生无怨无悔’‘高三不狠，怎能站稳’……</p>
                <p> 而一楼东侧的一间教室，占地格外大，近千平米，这里和普通教室不同，没有任何桌椅，一侧摆放着刀、枪、剑、棍等大量冷兵器，另一侧则摆放着诸多特殊仪器，以及一条由暗红色金属铺就的特殊跑道。</p>
                <p> 教室内顿时炸开了锅。</p>
            </div>
            <div class="report"><p style="color: red;">本章未完，点击下一页继续阅读。</p></div>
        </div>
        <div class="readpage">
            <a class="gray" href="javascript:void(0);">没有了</a> <a href="/read/76380/" rel="index" id="info_url">目录</a>
            <a href="javascript:addbookcase('76380','高武纪元','37623034','第1章 李源');" class="addbookcase">加书签</a>
            <a href="/read/76380/37623034_2.html" rel="next" id="next_url">下一页</a>
        </div>
        <div class="clear"></div>
    </div>
</div>
```

需要注意，一个章节的页面如果有 `<a href="/read/76380/37623034_2.html" rel="next" id="next_url">下一页</a>` 这种标签，就说明该章节在当前页面的内容还不是章节完整内容，需要点击下一页，走相同流程获取后续分页内容，直到出现 `<a href="/read/76380/37623036.html" rel="next" id="next_url">下一章</a>` 这种下一章的链接， 或者出现 `<a href="javascript:void(0);" class="gray" id="next_url">没有了</a>` 这种没有了的标签，才算章节内容完整。
