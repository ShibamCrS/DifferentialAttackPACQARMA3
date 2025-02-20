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
void generateState(cell_t *state){
    for(int j=0;j<16;j++){
        state[j]=rand() & 0xF;
    }
}

uint64_t generateState64(){
    uint64_t state1 = (uint64_t)(rand() & 0x00000000FFFFFFFFUL);
    uint64_t state2 = (uint64_t)(rand() & 0xFFFFFFFFUL);
    uint64_t state = (state1 << 32) | state2;
    return state;
}

// extracting yth bit of the xth cell, i.e., (4*(15 - x) + y)-th bit
uint64_t extractBit(uint64_t A, int x, int y){
    int index = (4*(15 - x) + y);
    uint64_t bit = (A >> index) & 0x1UL;
    return bit;
}
uint64_t setBit(uint64_t A, uint64_t bit, int x, int y){
    uint64_t B;
    int index = (4*(15 - x) + y);
    B = A & (~(1UL << index));
    B = B | (bit << index);
    return B;
}
uint64_t generateTweakCondEq12(uint64_t K) {
    uint64_t T = generateState64();
    //T2_2 = T5_2 ^ K0_1 ^ K5_1
    uint64_t T5_2 = extractBit(T, 5, 2);
    uint64_t K0_1 = extractBit(K, 0, 1);
    uint64_t K5_1 = extractBit(K, 5, 1);
    uint64_t T2_2 = (T5_2 ^ K0_1 ^ K5_1 ^ bb0) & 0x1UL;
    T = setBit(T, T2_2, 2, 2);
    //T2_0 = T2_1 ^ T5_0 ^ T5_1 ^ K0_3 ^ K5_3
    uint64_t T2_1 = extractBit(T, 2, 1);
    uint64_t T5_0 = extractBit(T, 5, 0);
    uint64_t T5_1 = extractBit(T, 5, 1);
    uint64_t K0_3 = extractBit(K, 0, 3);
    uint64_t K5_3 = extractBit(K, 5, 3);
    uint64_t T2_0 = (T2_1 ^ T5_0 ^ T5_1 ^ K0_3 ^ K5_3 ^ bb1) & 0x1UL;
    T = setBit(T, T2_0, 2, 0);
    return T;
}

uint64_t generateTweakCondEq14(uint64_t K) {
    uint64_t T = generateState64();
    //T15_0 = T15_2 ^ T15_3 ^ T3_0 ^ T3_2 ^ T3_3 ^ parity_K7 ^ parity_K8
    uint64_t T15_2 = extractBit(T, 15, 2);
    uint64_t T15_3 = extractBit(T, 15, 3);
    uint64_t T3_0  = extractBit(T, 3, 0);
    uint64_t T3_2  = extractBit(T, 3, 2);
    uint64_t T3_3  = extractBit(T, 3, 3);
    uint8_t K7 = (K >> (8*4)) & 0xF;
    uint8_t K8 = (K >> (7*4)) & 0xF;
    uint64_t parity_K7 = (uint64_t)(__builtin_parity(K7));
    uint64_t parity_K8 = (uint64_t)(__builtin_parity(K8));
    uint64_t T15_0 = (T15_2 ^ T15_3 ^ T3_0 ^ T3_2 ^ T3_3 ^ parity_K7 ^ parity_K8 ^ 1) & 0x01;
    T = setBit(T, T15_0, 15, 0);
    return T;
}
