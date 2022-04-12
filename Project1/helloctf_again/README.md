# 2. helloctf_again

## Writeup

### Checksec ./helloctf_again

![Untitled](../img/Untitled%201.png)

### Run ./helloctf_again

- Given two string and ask user input some text

![Untitled](../img/Untitled%202.png)

> **與第一題不同為不是單純字串過長造成 *Segmentation fault***
> 

### IDA Analysis

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  char s[16]; // [rsp+0h] [rbp-10h] BYREF

  init();
  puts("I check every input so it is very safe now");
  puts("I think this question is also very easy right?");
  __isoc99_scanf("%s", s);
  if ( strlen(s) > 0x10 )
  {
    puts("input toooooooo long");
    exit(0);
  }
  if ( strcmp(s, "yes") )
  {
    puts(asc_402090);
    exit(0);
  }
  return 0;
}
```

> **從 IDA 分析可以看出如果輸入的字串長度超過 16 或者字串不等於 yes 的狀況下都會讓程式直接離開。   → 要想辦法繞過這兩個機制**
> 

### objdump Analysis

![Untitled](../img/Untitled%203.png)

> **function magic 可以直接 access 到 system@plt 來 call 出 shell。可以做為 buffer overflow 改寫 return address 到 magic function 的位置**
> 

> **本題的 main 中接使用者輸入的為 scanf**
> 

<aside>
💡 **字串中起頭肯定是 yes 才可以避免掉進入 if( strcmp(s, "yes") ) 的迴圈，且也只能是 yes，但同時又要讓 buffer overflow，因此加入可以加入 \0 讓 scanf 視為輸入結束。**

</aside>

<aside>
💡 **第一題是使用 evecev@plt，而本題使用的是 system@plt。system@plt 中會有 MOVAPS Issue，因此會檢查stack有沒有對齊0x10 bytes，由於我們是在main的return做到stack overflow，因此如果我們將ret address塞magic function address則會造成magic function需要做function prologue，但是因為我們在main的ret做stack overflow，所以magic function的function prologue沒有ret address，因此這個function stack會少8個byte，以至於在MOVAPS指令時無法對齊造成error。**

</aside>

原因可以參考下面網站！

![Untitled](../img/Untitled%204.png)

[Pwntools遇到Got EOF while reading in interactive【未完全解决】_ChenY.Liu的博客-CSDN博客](https://blog.csdn.net/qq_43596950/article/details/113849666)