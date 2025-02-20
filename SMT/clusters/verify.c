#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
#include <stdbool.h>
#include <math.h>

#define ALLOCATE_TRY(var,code) if (! var) { var = code; if (! var) { printf("Out of memory!\n"); fflush(stdout); exit(-1);} }
#define RotCell(val,amount) ( (((val) << (amount)) | ((val) >> (4-(amount)))) & 0xF )

#define SubCell4(cells) do { for(int i = 0; i < 16; i++) (cells)[i] = sbox_4[(cells)[i]]; } while(0)
#define SubCell4_inv(cells) do { for(int i = 0; i < 16; i++) (cells)[i] = sbox_4_inv[(cells)[i]]; } while(0)

typedef unsigned char cell_t;
#include "utility.h"
#include "qarma64.h"
#define PRECOMPUTE
#ifdef PRECOMPUTE
#include "qarma64_opt.h"
#else
#include "qarma64_opt_const_table.h"
#endif

#define PRINT

int VISIBLE = 16;
int EXP = 16;
uint64_t MASK;
uint64_t MASK3;
uint64_t MASKF;

uint64_t encrypt_s(int rnd, const uint64_t W, const uint64_t W_p, const uint64_t core_key, const uint64_t middle_key, const uint64_t P0, const uint64_t P1, const uint64_t T0[4], const uint64_t T1[4]){
    uint64_t S0, S1, D, D1,  K;
    int i;

    S0 = P0;
    S1 = P1;
    K  = core_key;
    
        D1 = 0;
#ifdef PRINT
        D  = S0 ^ S1;
        displayCols64(D);
#endif       
        S0 = S(S0);
        S1 = S(S1);
#ifdef PRINT
        D  = S0 ^ S1;
        displayCols64(D);
#endif
        D1 = D;
        /* S0 = S0 ^ round_constant[2] ^ K; */
        /* S1 = S1 ^ round_constant[2] ^ K; */
        S0 ^= T0[0];
        S1 ^= T1[0];
#ifdef PRINT
        D  = S0 ^ S1;
        displayCols64(D);
#endif
        S0 = Tau(S0);
        S1 = Tau(S1);
#ifdef PRINT
        D  = S0 ^ S1;
        displayCols64(D);
#endif
        S0 = M(S0);
        S1 = M(S1);
#ifdef PRINT
        D  = S0 ^ S1;
        displayCols64(D);
#endif
        S0 = S(S0);
        S1 = S(S1);

        D  = S0 ^ S1;
#ifdef PRINT
        displayCols64(D);
        printf("***************************************************************\n");
#endif
    return D1;
}
uint64_t encrypt(int rnd, const uint64_t W, const uint64_t W_p, const uint64_t core_key, const uint64_t middle_key, const uint64_t P0, const uint64_t P1, const uint64_t T0[4], const uint64_t T1[4]){
    uint64_t S0, S1, D, D1,  K;
    int i;

    S0 = P0;
    S1 = P1;
    K  = core_key;
    
    D1 = 0;
    for(int i=0; i<rnd; i++) {
        /* S0 = S0 ^ round_constant[i+1] ^ K; */
        /* S1 = S1 ^ round_constant[i+1] ^ K; */
#ifdef PRINT
        D  = S0 ^ S1;
        displayCols64(D);
#endif
        S0 ^= T0[i+1];
        S1 ^= T1[i+1];
#ifdef PRINT
        D  = S0 ^ S1;
        displayCols64(D);
#endif
        S0 = Tau(S0);
        S1 = Tau(S1);
#ifdef PRINT
        D  = S0 ^ S1;
        displayCols64(D);
#endif
        S0 = M(S0);
        S1 = M(S1);
#ifdef PRINT
        D  = S0 ^ S1;
        displayCols64(D);
#endif
        
        S0 = S(S0);
        S1 = S(S1);
        D  = S0 ^ S1;
#ifdef PRINT
        displayCols64(D);
        printf("------------------------------\n");
#endif
        if(D == 0x1000010004000400) {
            D1 = D;
        }
    }
#ifdef PRINT
    printf("***************************************************************\n");
#endif
    return D;
}

uint64_t run(int r, uint64_t inD, uint64_t outD, uint64_t tD, uint64_t K, uint64_t W) {
    cell_t k0[16];
    cell_t k1[16];
    cell_t k1_M[16];
    cell_t w0[16];
    cell_t w1[16];
    expandState(k0, K);
    expandState(w0, W);
    KeySpecialisation(k0, w0, k1, k1_M, w1);

    uint64_t k0c, k1c, k1_Mc, w0c, w1c;
    k0c   = transpose(compactState(k0));
    k1c   = transpose(compactState(k1));
    k1_Mc = transpose(compactState(k1_M));
    w0c   = transpose(compactState(w0));
    w1c   = transpose(compactState(w1));

    uint64_t T = generateState64();
    uint64_t TT = T ^ tD;
    uint64_t T0c = transpose(T);
    uint64_t T1c = transpose(TT);
    displayCols64(T);

    uint64_t T0[4], T1[4];
    T0[0]  = T0c;
    T0[1]  = omega(h(T0[0]));
    T0[2]  = omega(h(T0[1]));
    T0[3]  = omega(h(T0[2]));

    T1[0]  = T1c;
    T1[1]  = omega(h(T1[0]));
    T1[2]  = omega(h(T1[1]));
    T1[3]  = omega(h(T1[2]));
    
    uint64_t inDc = transpose(inD);
    uint64_t outDc = transpose(outD);    
    uint64_t counter = 0;
    while(1) {
        uint64_t P0 = generateState64();
        uint64_t P1 = P0 ^ inDc;

        /* uint64_t D = encrypt(r, w0c, w1c, k0c, k1c, P0, P1, T0, T1); */
        uint64_t D = encrypt_s(r, w0c, w1c, k0c, k1c, P0, P1, T0, T1);
        if (D == 0x1000010004000400) {
        /* if (D == outDc) { */
            break;
            displayCols64(D);
        }
        counter++;
    }
    printf("Counter = %lld 2^(%LF) \n", counter, logl( (long double) counter) / logl(2.0));


}

void testSbox() {
    uint64_t count = 0.0;
    uint8_t a,b, d;
    /* for(d=0; d<16; d++) { */
    d = 0x2;
    printf("d = %02X -----------------\n", d);
    for (int y=0; y<16; y++) {
        count = 0;
        for (int x=0; x<16; x++) {
            a = sbox_4[RotCell(sbox_4[x      ], 2) ^ y];
            b = sbox_4[RotCell(sbox_4[x ^ 0x4], 2) ^ y];
            if ( (a ^ b) == d) {
                count++;
            }
        }
        printf("y = %02X: %ld %Lf \n", y, count, logl(((double)count/16.0)/logl(2.0)) );
    }
    /* } */
}

int main() {
    srand((unsigned) time(NULL));
#ifdef PRECOMPUTE
    alpha = transpose(alpha);
    printf("%016llx \n", alpha);
    for(int i=0; i< 16; i++)
    {
        round_constant[i] = transpose(round_constant[i]);
    }
    //Pre Computation
    if (!Allocate_Tables()){
        printf("Out of memory!\n");
        exit(1);
    }
    PreCompute_Tables();
#endif

    uint64_t K, W;
    K = generateState64();
    W = generateState64();
    
    //111
    /* int r = 1; */
    /* cell_t ft[16]  = {0x0,0x0,0x0,0x0, 0x0,0x0,0x0,0x0, 0x0,0x0,0x0,0x0, 0x0,0x0,0x4,0x8}; */
    /* cell_t fsc[16] = {0x0,0x0,0x0,0x0, 0x1,0x1,0x4,0x0, 0x2,0x8,0x8,0x8, 0x0,0x2,0x8,0x8}; */
    /* cell_t bsc[16] = {0x1,0x0,0x0,0x0, 0x0,0x1,0x4,0x4, 0x0,0x0,0x0,0x0, 0x0,0x0,0x0,0x0}; */

    //111
    /* int r = 1; */
    /* cell_t ft[16]  = {0x0,0x0,0x4,0x4, 0x0,0x0,0x0,0x0, 0x0,0x0,0x0,0x0, 0x0,0x0,0x0,0x0}; */
    /* cell_t fsc[16] = {0x1,0x0,0x0,0x0, 0x0,0x1,0x4,0x4, 0x0,0x0,0x0,0x0, 0x0,0x0,0x0,0x0}; */
    /* cell_t bsc[16] = {0x2,0x0,0x0,0x0, 0x0,0x0,0x0,0x0, 0x2,0x0,0x0,0x0, 0x0,0x0,0x0,0x0}; */

    //222
    /* int r = 2; */
    /* cell_t ft[16]  = {0x0,0x0,0x0,0x0, 0x0,0x0,0x0,0x0, 0x0,0x0,0x0,0x0, 0x0,0x0,0x4,0x8}; */
    /* cell_t fsc[16] = {0x0,0x0,0x0,0x0, 0x1,0x1,0x4,0x0, 0x2,0x8,0x8,0x8, 0x0,0x2,0x8,0x8}; */
    /* cell_t bsc[16] = {0x2,0x0,0x0,0x0, 0x0,0x0,0x0,0x0, 0x2,0x0,0x0,0x0, 0x0,0x0,0x0,0x0}; */
    
    int r = 2;
    cell_t ft[16]  = {0x0,0x0,0x0,0x0, 0x0,0x0,0x4,0x4, 0x0,0x0,0x0,0x0, 0x0,0x0,0x0,0x0};
    cell_t fsc[16] = {0x4,0x0,0x0,0x0, 0x0,0x4,0x2,0x1, 0x0,0x0,0x0,0x0, 0x0,0x0,0x0,0x0};
    cell_t bsc[16] = {0x2,0x0,0x0,0x0, 0x0,0x0,0x0,0x0, 0x2,0x0,0x0,0x0, 0x0,0x0,0x0,0x0};
    

    uint64_t tD, inD, outD;
    tD   = compactState(ft);
    inD  = compactState(fsc);
    outD = compactState(bsc);
    run(r, inD, outD, tD, K, W);
    /* testSbox(); */
    return 0;
}
    
