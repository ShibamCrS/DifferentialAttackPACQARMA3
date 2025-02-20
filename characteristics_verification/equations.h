void configure() {
    int type;
    uint64_t logData, tD, inD, outD, MASK, numZeroCell;
    long double q;

    type = 33; EXP  = 100; logData = 14; numZeroCell = 2; q = 7.98;
    tD   = 0x0020000000000000UL;
    inD  = 0x0000802DE0040E40UL;
    outD = 0x0000000000000000UL;
    MASK = 0xFF00000000000000UL;

#ifdef EQ9
    type = 33; EXP  = 100; logData = 14; numZeroCell = 2; q = 7.98;
    tD   = 0x0020000000000000UL;
    inD  = 0x0000802DE0040E40UL;
    outD = 0x0000000000000000UL;
    MASK = 0xFF00000000000000UL;
#endif
#ifdef EQ10
    type = 33; EXP  = 100; logData = 18; numZeroCell = 2; q = 10.01;
    tD   = 0x00E0000000000090UL;
    inD  = 0x009500000700D000UL;
    outD = 0x0000000000000000UL;
    MASK = 0xFF00000000000000UL;
#endif
#ifdef EQ11
    type = 23; EXP  = 100; logData = 20; numZeroCell = 2; q = 12.00;
    tD   = 0x000FE00000000006UL;
    inD  = 0x00B00F0000000000UL;
    outD = 0x0000000000000000UL;
    MASK = 0xFF00000000000000UL;
#endif
#ifdef EQ11_PRIME
    type = 23; EXP  = 100; logData = 18; numZeroCell = 3; q = 12.01;
    tD   = 0x000FE00000000006UL;
    inD  = 0x00B00F0000000000UL;
    outD = 0x0000000000000000UL;
    MASK = 0xFFF0000000000000UL;
#endif
#if defined(EQ13) || defined(EQ13_PRIME)
    type = 33; EXP  = 100; logData = 22; numZeroCell = 2; q = 12.00;
    tD   = 0x0000000000000048UL;
    inD  = 0x0000114028880288UL;
    outD = 0x0000000000000000UL;
    MASK = 0xFF00000000000000UL;
#endif
#if defined(EQ13_STAR) || defined(EQ13_PRIME_STAR)
    printf(" type = 33; EXP  = 100; logData = 18; numZeroCell = 2; \n");
    type = 33; EXP  = 100; logData = 18; numZeroCell = 2; q = 10.00;
    tD   = 0x0000000000000048UL;
    inD  = 0x0000114028880288UL;
    outD = 0x0000000000000000UL;
    MASK = 0xFF00000000000000UL;
    EQ12_COND = 1;
#endif
#ifdef EQ15
    type = 33; EXP  = 100; logData = 29; numZeroCell = 3; q = 18.00;
    tD   = 0x0000004000090000UL;
    inD  = 0x0000010750900B02UL;
    outD = 0x1040000000000000UL;
    MASK = 0x0F0FF00000000000UL;
#endif
#ifdef EQ15_STAR
    type = 33; EXP  = 100; logData = 27; numZeroCell = 3; q = 17.00;
    tD   = 0x0000004000090000UL;
    inD  = 0x0000010750900B02UL;
    outD = 0x1040000000000000UL;
    MASK = 0x0F0FF00000000000UL;
    EQ14_COND = 1;
#endif
#ifdef EQ16
    type = 33; EXP  = 100; logData = 30; numZeroCell = 4; q = 21.00;
    tD   = 0x0000000000DED000UL;
    inD  = 0x00000F000D0000D1UL;
    outD = 0x2000000000000000UL;
    MASK = 0x0FFFF00000000000UL;
#endif
#ifdef EQ18
    type = 33; EXP  = 100; logData = 33; numZeroCell = 1; q = 18.00;
    tD   = 0x0000000E60000C00UL;
    inD  = 0x00000000C0906305UL;
    outD = 0xAA40AA0400000000UL;
    MASK = 0x000F000000000000UL;
#endif
#ifdef EQ18_PRIME
    type = 33; EXP  = 100; logData = 33; numZeroCell = 2; q = 18.00;
    tD   = 0x0000000E60000C00UL;
    inD  = 0x00000000C0906305UL;
    outD = 0xAA40AA0400000000UL;
    MASK = 0x000F00F000000000UL;
#endif
    run(type, logData, tD, inD, outD, MASK, numZeroCell, q);
}

void configure_extra() {
    int type;
    uint64_t logData, tD, inD, outD, MASK, numZeroCell;
    long double q;
#ifdef FIG12
    type = 33; EXP  = 100; logData = 24; numZeroCell = 2; q = 13.00;
    tD   = 0x0000000000000048UL;
    outD = 0x0000000000000000UL;
    MASK = 0xFF00000000000000UL;
    
    inD    = 0x0000124028180281UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000814028840248UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x00001B4028D8028DUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000214028810218UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000B140288D02D8UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q); 
    inD    = 0x0000414028820228UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000144028280282UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000194028C8028CUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x00009140288C02C8UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000184028480284UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000C14028860268UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x00001C4028680286UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);

#endif

#ifdef FIG13
    type = 33; EXP  = 100; logData = 26; numZeroCell = 2; q = 14.00;
    tD   = 0x0000000000000048UL;
    outD = 0x0000000000000000UL;
    MASK = 0xFF00000000000000UL;
    
    inD    = 0x0000B440282D02D2UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q); 
    inD    = 0x0000BB4028DD02DDUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x00009440282C02C2UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000C24028160261UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x00002B4028D1021DUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x00009C40286C02C6UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x00002C4028610216UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000224028110211UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x00008B4028D4024DUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x00009840284C02C4UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000284028410214UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000244028210212UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000BC40286D02D6UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x00009B4028DC02CDUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000CC4028660266UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x00009240281C02C1UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000C84028460264UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000C94028C6026CUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000C44028260262UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x00004B4028D2022DUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000294028C1021CUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000B240281D02D1UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x00008C4028640246UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000424028120221UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000CB4028D6026DUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000894028C4024CUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000B840284D02D4UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x00004C4028620226UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000494028C2022CUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000B94028CD02DCUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
    inD    = 0x0000824028140241UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
#endif

#ifdef FIG12_STAR
    EQ12_COND = 1;
    type = 33; EXP  = 100; logData = 20; numZeroCell = 2; q = 11.00;
    tD   = 0x0000000000000048UL;
    outD = 0x0000000000000000UL;
    MASK = 0xFF00000000000000UL;
    
 bb0 = 0 ; bb1 = 1 ;inD    = 0x0000124028180281UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 0 ;inD    = 0x0000814028840248UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 1 ;inD    = 0x00001B4028D8028DUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 0 ; bb1 = 1 ;inD    = 0x0000214028810218UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 1 ;inD    = 0x0000B140288D02D8UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 0 ;inD    = 0x0000414028820228UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 0 ;inD    = 0x0000144028280282UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 1 ;inD    = 0x0000194028C8028CUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 1 ;inD    = 0x00009140288C02C8UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 0 ;inD    = 0x0000184028480284UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 0 ; bb1 = 1 ;inD    = 0x0000C14028860268UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 0 ; bb1 = 1 ;inD    = 0x00001C4028680286UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
#endif
#ifdef FIG13_STAR
    EQ12_COND = 1;
    type = 33; EXP  = 100; logData = 22; numZeroCell = 2; q = 12.00;
    tD   = 0x0000000000000048UL;
    outD = 0x0000000000000000UL;
    MASK = 0xFF00000000000000UL;
    
 bb0 = 0 ; bb1 = 1 ;inD    = 0x0000B440282D02D2UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q); 
 bb0 = 0 ; bb1 = 0 ;inD    = 0x0000BB4028DD02DDUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 0 ; bb1 = 1 ;inD    = 0x00009440282C02C2UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 0 ; bb1 = 0 ;inD    = 0x0000C24028160261UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 0 ;inD    = 0x00002B4028D1021DUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 0 ;inD    = 0x00009C40286C02C6UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 0 ; bb1 = 0 ;inD    = 0x00002C4028610216UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 0 ; bb1 = 0 ;inD    = 0x0000224028110211UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 0 ; bb1 = 1 ;inD    = 0x00008B4028D4024DUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 0 ; bb1 = 1 ;inD    = 0x00009840284C02C4UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 1 ;inD    = 0x0000284028410214UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 1 ;inD    = 0x0000244028210212UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 0 ;inD    = 0x0000BC40286D02D6UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 0 ; bb1 = 0 ;inD    = 0x00009B4028DC02CDUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 0 ; bb1 = 0 ;inD    = 0x0000CC4028660266UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 0 ;inD    = 0x00009240281C02C1UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 1 ;inD    = 0x0000C84028460264UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 0 ;inD    = 0x0000C94028C6026CUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 1 ;inD    = 0x0000C44028260262UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 0 ; bb1 = 1 ;inD    = 0x00004B4028D2022DUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 0 ;inD    = 0x0000294028C1021CUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 0 ;inD    = 0x0000B240281D02D1UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 1 ;inD    = 0x00008C4028640246UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 1 ;inD    = 0x0000424028120221UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 0 ;inD    = 0x0000CB4028D6026DUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 0 ; bb1 = 1 ;inD    = 0x0000894028C4024CUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 0 ; bb1 = 1 ;inD    = 0x0000B840284D02D4UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 1 ;inD    = 0x00004C4028620226UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 0 ; bb1 = 1 ;inD    = 0x0000494028C2022CUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 0 ; bb1 = 0 ;inD    = 0x0000B94028CD02DCUL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
 bb0 = 1 ; bb1 = 1 ;inD    = 0x0000824028140241UL;COUNT_EQ++;run(type, logData, tD, inD, outD, MASK, numZeroCell,q);
#endif
}
