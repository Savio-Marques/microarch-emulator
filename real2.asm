goto main
        wb 0

out     ww 0
in1     ww 14
in2     ww 0
n       ww 0
m       ww 0
d       ww 0
temp    ww 0
soma    ww 0
um      ww 1
dois    ww 2

main    load x, in1
        store x, n
        sub x, dois
        jn x, nprimo
        jz x, eprimo
        load x, dois
        store x, d
chk1    load x, d
        mul x, d
        store x, temp
        load x, n
        sub x, temp
        jn x, eprimo
        load x, n
        mod x, d
        jz x, nprimo
        load x, d
        add x, um
        store x, d
        goto chk1
eprimo  load x, n
        add x, um
        store x, m
        load x, um
        store x, soma
        load x, dois
        store x, d
sumdiv  load x, d
        mul x, d
        store x, temp
        load x, m
        sub x, temp
        jn x, fimsum
        load x, m
        mod x, d
        jz x, adddiv
        goto nxtd
adddiv  load x, soma
        add x, d
        store x, soma
        load x, m
        sub x, temp
        jz x, nxtd
        load x, m
        div x, d
        store x, temp
        load x, soma
        add x, temp
        store x, soma
nxtd    load x, d
        add x, um
        store x, d
        goto sumdiv
fimsum  load x, soma
        store x, out
        halt
nprimo  load x, n
        add x, um
        store x, m
nxtpl   load x, dois
        store x, d
chk2    load x, d
        mul x, d
        store x, temp
        load x, m
        sub x, temp
        jn x, fndp
        load x, m
        mod x, d
        jz x, notp2
        load x, d
        add x, um
        store x, d
        goto chk2
notp2   load x, m
        add x, um
        store x, m
        goto nxtpl
fndp    load x, m
        store x, out
        halt