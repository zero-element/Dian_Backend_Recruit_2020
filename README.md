# Dian_Backend_Recruit_2020
点团队后台招新2020
## 2020-05-09

#### 完成：

1. 搭建flask项目框架

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