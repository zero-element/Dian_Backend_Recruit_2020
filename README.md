# Dian_Backend_Recruit_2020
点团队后台招新2020
## 2020-05-09

#### 完成：

1. 搭建flask项目框架，参考学习其他flask项目目录结构设计，使用restful模式构建api
2. 使用sqlalchemy的session实现分库，利用contextmanager和flask.g方便的切库

#### 疑问：

1. flask_sqlalchemy貌似没有提供底层接口，最终还是用sqlalchemy混合实现，不知道flask_sqlalchemy能否直接实现分库
2. session的生命周期有点模糊，不知道上下文反复`sessionmaker`开销会不会很大，有空优化一下

## 2020-05-10
今天网鼎杯，进度可能稍有耽搁
20：00
网鼎杯复盘完毕，继续开发
#### 完成：
1. 学习使用flask_jwt_extended管理权限
2. 学习使用postman管理api并导出
3. 实现了登录，根据分库的要求，使用jwt的claims对blog_type进行判别，防止鉴权出错
4. 改用sha1储存密码，加强安全性
5. 完成了五个路由的基本功能，优化了表的结构，使用UnicodeText储存正文长文本
#### 疑问：
1. 最初Users和Articles建了backref，但是好像不容易做分页查询，而且不清楚底层机制，不能保证count效率
2. 使用contextmanager封装session后，db报错会被catch住，无法直接在contextmanager中直接返回json，于是还是手动添加了commit，不知道有没有更好的处理方法

## 2020-05-11

#### 完成：

1. 优化了session的动态创建和存储，减小sessionmaker的开销，修改了一些报错的处理逻辑，解决了先前的疑问
2. 根据实际情况，删减了一些如func.count等不必要的优化
3. 实现了一个带回复功能的简单二级评论接口
4. 统一了一些接口命名，添加了tag和category支持，学习了sqlalchemy多对多的写法
5. 添加了简单的表单验证
6. 通过echo确认了relationship会fetch整个表，分页时不适用（其实也关系不大？经验不足，一开始就去想优化有些本末倒置了）
7. 试图通过构建relationship实现自动删除孤儿tag和category，最后发现数据库似乎并不支持这类操作，只能通过手动删除实现

##### 疑问：

1. 没有系统学习过数据库知识，对复杂的数据关系还是比较模糊

## 2020-05-12

##### 完成：

1. 之前对tag和category的写法在多用户的情况下有很多问题，学习了包括联合主键，联合唯一约束等等数据库知识，大改了表结构并调整了api设计
2. 学习了listen的使用，更简洁的实现了自动删除tag和category
3. 统一使用json传参，便于前端提交tags等参数
4. 支持图片上传，使用secure_filename，PIL等方法防范了路径穿越和文件类型伪造
5. 密码改为hmac加密，防范了长度拓展攻击，并使用username作为key计算文件名，防止不同用户文件冲突
6. 支持markdown，基本能用了，有空搓一下前端
7. 学到可以用lazy='dynamic'懒加载，解决了多对多的relationship效率问题
8. 重构了评论系统，添加了点赞和置顶功能，重写了回复逻辑，能用了

##### 疑问：

1. new一个model并merge到db中，再赋给别的model并提交会报Duplicate，调了一下午。看echo发现是sqlalchemy的内部逻辑把这两次插入时的model当成不同的数据，造成了重复插入
2. 搜/调了一天的数据库，人晕了。每次重新建库都要手动删表，不知道flask migrate对这个问题有没有帮助，有空学一下。（发现自己蠢了，可以删库跑路（

