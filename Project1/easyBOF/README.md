# 6. easyBOF

## Writeup

### Step

1. 從 checksec 可以發現他有開 Canary 跟 NX，所以我們要想辦法拿到Canary的值。另外我們沒辦法透過注入 shellcode 來開 shell，因為有 NX，所以直覺上會使用 ROP 來解。
    
    ![Untitled](../img/Untitled%2022.png)
    
2. 我們透過 GDB 發現 printf 的 rsp+0x40 的位置剛好是 Canary 的值，所以我們可以透過 printf format string 方式去取出 rsp+0x40 的值。詳細可以看下列網址
    
    [Format String](https://frozenkp.github.io/pwn/format_string/)
    
3. ROP的部分，我們透過程式中已有的Gadget去組合出execve()的syscall，將該放的值放到相對應的暫存器，這樣就可以拿到shell了。
    
    ![Untitled](../img/Untitled%2023.png)
    

### IDA Analysis

![Untitled](../img/Untitled%2024.png)

![Untitled](../img/Untitled%2025.png)
