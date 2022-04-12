# 5. donate

## Writeup

### add_donate():

- 每次會 malloc 一個 print() **(即 fuction 中的 say)** 和一個 data **(即 fuction 中的 result)** 到 heap 當中
- 每次會將 print() 在 heap 中的 address 加到 donate_bars 當中
    
    
    Ex： donate_bars
    
    | 第一次 say 在 heap 中的 address |
    | ------------------------------- |
    | 第二次 say 在 heap 中的 address |
    | ...                             |
    
    Ex：heap
    
    | Chunk1 (裡面存say)  |
    | ------------------- |
    | Chunk2 (裡面存data) |
    | ......              |
    
    ![Untitled](../img/Untitled%2015.png)
    

### clear_donate():

- 每次會 free 掉 heap 當中的兩個 chunk
    
    ![Untitled](../img/Untitled%2016.png)
    

### Steps

1. 先 add_donate() 兩次，如此可使 heap 有4個 chunk。
2. 分別執行 clear_donate(1) 和 clear_donate(0)，使這4個 chunk 記憶體位址由小到大在tcache_entry 中排序，如果先 clear_donate(0)，再 clear_donate(1) 會導致記憶體位址排序錯誤。
    
    ![Untitled](../img/Untitled%2017.png)
    
    此時的donate_bar array中的值分別如下
    
    | index | value                                        |
    | ----- | -------------------------------------------- |
    | 0     | 0x1720260 (第 1 次 say 在 heap 中的 address) |
    | 1     | 0x17202a0 (第 2 次 say 在 heap 中的 address) |
3. 再 add_donate() 一次，並希望在 data **(即fuction中的result)** 的部分 malloc 一個不為0x20 的 chunk，這麼做是希望能只寫入 0x1720260 的這塊 tcahe，這樣下次再add_donate 時，我們可以將 magic_func() 寫到 0x17202a0 的記憶體位址，如此一來，我們就可以透過 danate_bar[1] 來進入 magic_func()，故我們將 data 設為 32byte，使他產生一個 0x30 chunk
    
    ![Untitled](../img/Untitled%2018.png)
    
4. 再 add_donate() 一次，這次我們會將 magic_func() 寫入 data **(即 fuction 中的 result)**，如此一來 0x270 這個 chunk 會被塞滿 print() **(即 fuction 中的 say)**，而 0x290 這個chunk的 data **(即 0x2a0 位址存放的值)** 會被塞滿 magic_func() 的 address，如此一來*donate_bar[1] 就會存放 magic_func() 的記憶體位址。
    
    ![add_donate前](../img/Untitled%2019.png)
    
    add_donate前
    
    ![add_donate()後](../img/Untitled%2020.png)
    
    add_donate()後
    
5. 因此最後我們將v5傳入1時，我們就可以成功呼叫magic_func()。
    
    ![Untitled](../img/Untitled%2021.png)
    
