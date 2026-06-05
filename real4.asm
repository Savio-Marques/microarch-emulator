goto main
        wb 0

out     ww 0
in1     ww 3648413612
in2     ww 0
v0      ww 0
v1      ww 0
v2      ww 0
v3      ww 0
temp    ww 0
c256    ww 256

main    load x, in1
        store x, temp
        
        ;LSB para MSB
        mod x, c256
        store x, v3
        load x, temp
        div x, c256
        store x, temp
        
        mod x, c256
        store x, v2
        load x, temp
        div x, c256
        store x, temp
        
        mod x, c256
        store x, v1
        load x, temp
        div x, c256
        store x, v0

        ; Sorting
cmp1    load x, v1
        sub x, v0
        jn x, swp1
        goto cmp2
swp1    load x, v0
        store x, temp
        load x, v1
        store x, v0
        load x, temp
        store x, v1

cmp2    load x, v3
        sub x, v2
        jn x, swp2
        goto cmp3
swp2    load x, v2
        store x, temp
        load x, v3
        store x, v2
        load x, temp
        store x, v3

cmp3    load x, v2
        sub x, v0
        jn x, swp3
        goto cmp4
swp3    load x, v0
        store x, temp
        load x, v2
        store x, v0
        load x, temp
        store x, v2

cmp4    load x, v3
        sub x, v1
        jn x, swp4
        goto cmp5
swp4    load x, v1
        store x, temp
        load x, v3
        store x, v1
        load x, temp
        store x, v3

cmp5    load x, v2
        sub x, v1
        jn x, swp5
        goto pack
swp5    load x, v1
        store x, temp
        load x, v2
        store x, v1
        load x, temp
        store x, v2

        ; MSB para LSB
pack    load x, v0
        mul x, c256
        add x, v1
        mul x, c256
        add x, v2
        mul x, c256
        add x, v3
        store x, out
        halt
    