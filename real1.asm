goto main
        wb 0

out     ww 0
in1     ww 42
in2     ww 0
n       ww 0
d       ww 0
soma    ww 0
temp    ww 0
temp2   ww 0
zero    ww 0
um      ww 1
dois    ww 2

main    load x, in1
        store x, n
        load x, zero
        store x, soma
        load x, n
        mod x, dois
        jz x, ehpar
        load x, um
        store x, d
limpar  load x, d
        mul x, d
        store x, temp
        load x, n
        sub x, temp
        jn x, fim
        load x, n
        mod x, d
        jz x, ehdivi
        goto pxdi
ehdivi  load x, soma
        add x, d
        store x, soma
        load x, d
        sub x, um
        jz x, pxdi
        load x, n
        sub x, temp
        jz x, pxdi
        load x, n
        div x, d
        store x, temp2
        load x, soma
        add x, temp2
        store x, soma
pxdi    load x, d
        add x, um
        store x, d
        goto limpar
ehpar   load x, dois
        store x, d
lpar    load x, d
        mul x, d
        store x, temp
        load x, n
        sub x, temp
        jn x, rpar
        load x, n
        mod x, d
        jz x, ehfat
        goto pxdp
ehfat   load x, soma
        add x, d
        store x, soma
ldiv    load x, n
        mod x, d
        jz x, divn
        goto pxdp
divn    load x, n
        div x, d
        store x, n
        goto ldiv
pxdp    load x, d
        add x, um
        store x, d
        goto lpar
rpar    load x, n
        sub x, um
        jz x, fim
        jn x, fim
        load x, soma
        add x, n
        store x, soma
fim     load x, soma
        store x, out
        halt