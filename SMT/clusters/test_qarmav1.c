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
uint64_t generateState64(){
    uint64_t state1 = (uint64_t)(rand() & 0x00000000FFFFFFFFUL);
    uint64_t state2 = (uint64_t)(rand() & 0xFFFFFFFFUL);
    uint64_t state = (state1 << 32) | state2;
    return state;
}

uint64_t compactState(const cell_t s[16])
{
    int i;
    uint64_t result = 0ULL;
    for (i=0;i<16;i++)
    {
        result <<= 4;
        result |= s[i];
    }
    return result;
}

void expandState(cell_t s_out[16], uint64_t s_in)
{
    int i;
    uint64_t s_in_copy = s_in;
    for (i=15;i>=0;i--)
    {
        s_out[i] = s_in_copy & 0xf;
        s_in_copy >>= 4;
    }
}
void displayCols(const cell_t state[16]){
    int c, r;
    for (c=0; c<4; c++) {
        for(r=0; r<4; r++) {
            printf("%01X ", state[4*r + c]);
        }
        printf("|");
    }
    printf("\n");
}
void displayCols64(uint64_t state){
    cell_t s[16];
    expandState(s, state);
    displayCols(s);
    /* printf("%016LX \n",state); */
}
#include "qarma64.h"
#include "qarma64_opt.h"


uint64_t qarma64_REF(uint64_t P, cell_t *w0, cell_t *w1,
                     cell_t *k0, cell_t *k1, uint64_t T,
                     int rounds){
    cell_t state[16], tstate[16];
    expandState(state, P);
    expandState(tstate, T);
    qarma64(state, w0, w1, k0, k1, tstate, rounds);
    uint64_t C = compactState(state);
    return C;
}
uint64_t qarma64_OPT(uint64_t P, uint64_t w0c, uint64_t w1c,
                     uint64_t k0c, uint64_t k1c, uint64_t T,
                     int rounds){
    P = transpose(P);
    uint64_t C = qarma64_opt(P, w0c, w1c, k0c, k1c, T, rounds);
    C = transpose(C);
    return C;
}
uint64_t qarma64_REF_r(uint64_t P, cell_t *w0, cell_t *w1,
                     cell_t *k0, cell_t *k1, uint64_t T,
                     int rounds){
    cell_t state[16], tstate[16];
    expandState(state, P);
    expandState(tstate, T);
    qarma64_r(state, w0, w1, k0, k1, tstate, rounds);
    uint64_t C = compactState(state);
    return C;
}
uint64_t qarma64_OPT_r(uint64_t P, uint64_t w0c, uint64_t w1c,
                     uint64_t k0c, uint64_t k1c, uint64_t T,
                     int rounds){
    P = transpose(P);
    uint64_t C = qarma64_r3_opt_333(P, w0c, w1c, k0c, k1c, T);
    C = transpose(C);
    return C;
}

void encryptTest() {
    uint64_t P, T, K, W, C0, C1;
    P = generateState64();
    T = generateState64();
    K = generateState64();
    W = generateState64();

    displayCols64(P);
    displayCols64(T);
    displayCols64(K);
    displayCols64(W);

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
    printf("-------qarma_ref vs qarma_opt-----------------\n");
    C0 = qarma64_REF(P, w0, w1, k0, k1, T, 3);
    C1 = qarma64_OPT(P, w0c, w1c, k0c, k1c, transpose(T), 3);
    displayCols64(C0);
    displayCols64(C1);
    C0 = qarma64_REF_r(P, w0, w1, k0, k1, T, 3);
    C1 = qarma64_OPT_r(P, w0c, w1c, k0c, k1c, transpose(T), 3);
    displayCols64(C0);
    displayCols64(C1);

}

int main(){
    srand(time(NULL));
    alpha = transpose(alpha);
    for(int i=0; i< 16; i++)
    {
        round_constant[i] = transpose(round_constant[i]);
    }

    /* Pre Computation */
    if (!Allocate_Tables()){
        printf("Out of memory!\n");
        exit(1);
    }
    PreCompute_Tables();
    encryptTest();
    Release_Tables();
}
