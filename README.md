# Dian_Backend_Recruit_2020
点团队后台招新2020
## 2020-05-09

#### 完成：

1. 搭建flask项目框架

#### 疑问：

1. flask_sqlalchemy貌似没有提供底层接口，最终还是用sqlalchemy混合实现，不知道flask_sqlalchemy能否直接实现分库
2. session的生命周期有点模糊，不知道上下文反复`sessionmaker`开销会不会很大，有空优化一下