# Clash Parser

嘗試復現 [`Clash for Windows`] 的 [`配置文件預處理`] 功能.

## 使用

### Parser 文件格式

形如:

```yml
prepend-rules:
  - DOMAIN,test.com,DIRECT # rules最前面增加一个规则
append-proxies:
  - name: test # proxies最后面增加一个服务
    type: http
    server: 123.123.123.123
    port: 456
commands:
  - proxy-groups.0.proxies=[]proxyNames
```

參考 [`Clash for Windows`] 文章 [`配置文件預處理`];  
本程序讀取的 Parser YAML 文件和該文章示例略有不同, 省略了頭部的 `parsers`, `url`, `yaml`.

### 運行

```sh
python -m parser <原配置文件> <Parser 文件>
```

[`Clash for Windows`]: https://github.com/Fndroid/clash_for_windows_pkg
[`配置文件預處理`]: https://docs.cfw.lbyczf.com/contents/parser.html
