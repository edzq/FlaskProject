# flask
初次尝试mysql+flask 写了一个登陆注册的web

运行 main.py
使用默认的5000端口时候为login.html登陆界面，修改成为5000/regist就可以访问regist.html的注册界面


结构如下：

  loginout
  
      | templates
      
        | login.html
        
        | regist.html
        
      main.py
      
      
 method 使用了get，登陆和注册的action为/login和/registuser
 
 第一次使用MySQL 在regist中把前台的账号名和密码插入到数据库中（创建好的user表单中）
 登陆也是一样的。
 
 学习的过程中发现flask 里面的app.route()这个装饰器 好有趣，找到一片CSDN上的blog看了许久，之前学python装饰器几乎不用，现在重新认识了一遍。
