# 7. akukin

## Writeup

### Step

1. 想辦法透過 BOF 跳到 nothing()，因為此題有開 PIE，所以不能直接透過 objdump 去找他的address 跳過去。
    
    ![Untitled](../img/Untitled%2026.png)
    
2. 我們觀察每次執行程式後 nothing() 的 address，發現後面 address 後面三碼都是固定的，因此我們就利用 BOF 塞到 RIP 的倒數第四位，之後讓他一直重複執行，一定會賽中 nothing() 0的 addresss。
3. 成功跳到 nothing() 後，可以透過 printf() 拿到 sevbuf 的 address，接著我們可以透過`l.symbols[”setvbuf”]` 拿到 setvbuf 的 offset，這樣我們兩個相減就可以拿到 libc_address。
4. 最後就是透過 one_gadget 去開 shell。