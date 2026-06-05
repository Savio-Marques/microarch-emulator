goto main
        wb 0

out     ww 0
in1     ww 3648413612
in2     ww 1017835715
a       ww 0
b       ww 0
soma    ww 0
c256    ww 256
ba      ww 0
bb      ww 0
temp    ww 0
zero    ww 0

main    load x, in1
        store x, a
        load x, in2
        store x, b
        load x, zero
        store x, soma
        
        load x, a
        mod x, c256
        store x, ba
        load x, b
        mod x, c256
        store x, bb
        load x, ba
        mul x, bb
        store x, temp
        load x, soma
        add x, temp
        store x, soma
        load x, a
        div x, c256
        store x, a
        load x, b
        div x, c256
        store x, b
        
        load x, a
        mod x, c256
        store x, ba
        load x, b
        mod x, c256
        store x, bb
        load x, ba
        mul x, bb
        store x, temp
        load x, soma
        add x, temp
        store x, soma
        load x, a
        div x, c256
        store x, a
        load x, b
        div x, c256
        store x, b
        
        load x, a
        mod x, c256
        store x, ba
        load x, b
        mod x, c256
        store x, bb
        load x, ba
        mul x, bb
        store x, temp
        load x, soma
        add x, temp
        store x, soma
        load x, a
        div x, c256
        store x, a
        load x, b
        div x, c256
        store x, b
        
        load x, a
        mod x, c256
        store x, ba
        load x, b
        mod x, c256
        store x, bb
        load x, ba
        mul x, bb
        store x, temp
        load x, soma
        add x, temp
        store x, soma
        
        load x, soma
        store x, out
        halt