# 4. superchat

## Writeup

1. 首先先用 Checksec 來確認防禦機制，會發現此題並沒有開啟 NX Protection，因此可以嘗試塞入 shellcode 來成功拿到 shell
    
    ![Untitled](../img/Untitled%207.png)
    
2. 透過 IDA 去看原始碼發現，read 的 buffer 只開了 16byte，太少了，所以我們一開始會把它改長。
    
    ![Untitled](../img/Untitled%208.png)
    
    我們可以透過以下這個網站去查如果要 call 哪一種syscall，以及相對應的 register 要放哪些值，因此將 %rdx 改成 0x100，這樣就可以成功塞入 shellcode
    
    [Linux System Call Table for x86 64](https://blog.rchapman.org/posts/Linux_System_Call_Table_for_x86_64/)
    
    ![Untitled](../img/Untitled%209.png)
    
3. 從 IDA 分析會發現有做 seccomp 的初始化，seccomp 是一種禁止一些 syscall 的保護機制。我們利用 seccomp-tools 檢查發現這題有禁用 execve，所以我們只能透過 print 在終端機上的方式拿到 flag
    
    ![Untitled](../img/Untitled%2010.png)
    
    ![Untitled](../img/Untitled%2011.png)
    
    ![Untitled](../img/Untitled%2012.png)
    
4. 我們嘗試依序 call open、read、write 開遠端機器上的 flag，從 fd 讀取檔案內容，但因為從 init 裡面會觀察到這題只有 stdin 和 stderr，因此要將 flag 輸出至終端機上的話只能用 stderr 替代 stdout。
    
    ![Untitled](../img/Untitled%2013.png)
    
    ![Untitled](../img/Untitled%2014.png)
    
    <aside>
    💡 unsigned int fd 處給 2
    
    </aside>