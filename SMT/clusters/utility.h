void printreg_to_file(const void *a, int nrof_byte, FILE *fp){
    int i;
    unsigned char *f = (unsigned char *)a;
    for(i=0; i < nrof_byte; i++){
        fprintf(fp, "%02X ",(unsigned char) f[nrof_byte - 1 - i]); 
    }
    fprintf(fp, "\n");
}

void printreg(const void *a, int nrof_byte){
    printreg_to_file(a, nrof_byte, stdout);
}

void printArr(int *a, int size) {
    for(int i=0; i<size; i++) {
        printf("%d ",a[i]);
    }
    printf("\n");
}

void printArrFile(FILE *fp, char *arrname, uint16_t *a, int size) {
    fprintf(fp, "const uint16_t %s[%d] = { ", arrname, size);
    for(int i=0; i<size - 1; i++) {
        fprintf(fp, "%d, ",a[i]);
    }
    fprintf(fp, "%d};\n \n",a[size - 1]);
}
void printArrFile64(FILE *fp, char *arrname, uint64_t *a, int size) {
    fprintf(fp, "const uint64_t %s[%d] = { ", arrname, size);
    for(int i=0; i<size - 1; i++) {
        fprintf(fp, "0x%llx, ",a[i]);
    }
    fprintf(fp, "0x%llx};\n \n",a[size - 1]);
}

void printBoolArr(const uint8_t *arr){
    int c;
    for (c=0; c<16; c++) {
        printf("%01X ", c);
    }
    printf("\n");
    for (c=0; c<16; c++) {
        printf("%01X ", arr[c]);
    }
    printf("\n");
}

void printMaxN (uint32_t *array, int size, int N) {
    uint8_t maxValues[10] = {0};
    int maxPositions[10] = {0};

    for (int i = 0; i < size; i++) {
        for (int j = 0; j < N; j++) {
            if (array[i] > maxValues[j]) {
                for (int k = N-1; k > j; k--) {
                    maxValues[k] = maxValues[k - 1];
                    maxPositions[k] = maxPositions[k - 1];
                }
                maxValues[j] = array[i];
                maxPositions[j] = i;
                break;
            }
        }
    }

    for (int i = 0; i < N; i++) {
        printf("%04X : %d ", maxPositions[i], array[maxPositions[i]]);
    }
    printf("\n");
}

uint32_t findMaxPosition(uint32_t arr[], size_t size) {
    uint32_t max = arr[0];
    size_t maxPos = 0;

    for (size_t i = 1UL; i < size; i++) {
        if (arr[i] > max) {
            max = arr[i];
            maxPos = i;
        }
    }

    return maxPos;
}
uint32_t findMinPosition(uint32_t arr[], size_t size) {
    uint32_t min = arr[0];
    size_t minPos = 0;

    for (size_t i = 1UL; i < size; i++) {
        if (arr[i] < min) {
            min = arr[i];
            minPos = i;
        }
    }

    return minPos;
}

uint32_t findNumberSuggestedKeys(uint32_t arr[], uint64_t size, uint32_t lowerBound){
    uint32_t noKeys = 0UL;
    for (uint64_t i = 0UL; i < size; i++) {
        if (arr[i] >= lowerBound) {
            noKeys++;
        }
    }
    return noKeys;
}

uint32_t findNumberSuggestedKeysl(uint32_t arr[], uint32_t size, uint32_t upperBound){
    uint32_t noKeys = 0UL;
    for (uint64_t i = 0UL; i < size; i++) {
        if (arr[i] < upperBound) {
            noKeys++;
        }
    }
    return noKeys;
}

uint32_t findNumberSuggestedKeysSame(uint32_t arr[], uint32_t size, uint32_t count){
    uint32_t noKeys = 0UL;
    for (uint64_t i = 0UL; i < size; i++) {
        if (arr[i] == count) {
            noKeys++;
        }
    }
    return noKeys;
}

void findMaxPositions(uint32_t maxes[], size_t indices[], uint32_t arr[], size_t size, size_t depth) {    
    for (size_t j = 0; j < depth; j ++) {
        maxes[j] = arr[0];
        indices[j] = 0;
    }
    for (size_t i = 1; i < size; i++) {
        if (arr[i] > maxes[depth-1]) {
            maxes[depth-1] = arr[i];
            indices[depth-1] = i;
            for (size_t j = depth-1; j > 0; j--) {
                if (maxes[j] > maxes[j-1]) {
                    uint32_t tmp1 = maxes[j];
                    maxes[j] = maxes[j-1];
                    maxes[j-1] = tmp1;

                    size_t tmp2 = indices[j];
                    indices[j] = indices[j-1];
                    indices[j-1] = tmp2;
                }
            }
        }
    }
}

void printCounter(const uint8_t *arr, int size){
    for(int i=0; i<size; i++){
        int val  = arr[i];
        if(val > 0) {
            printf("%02X : %d ", i, val);
        }
    }
    printf("\n");
}

/* uint64_t compactState(const cell_t s[16]) */
/* { */
/*     int i; */
/*     uint64_t result = 0ULL; */
/*     for (i=0;i<16;i++) */
/*     { */
/*         int j = ((i << 2) + (i >> 2)) & 0xf; */
/*         result <<= 4; */
/*         result |= s[j]; */
/*     } */
/*     return result; */
/* } */
/* void expandState(cell_t s_out[16], uint64_t s_in) */
/* { */
/*     int i; */
/*     uint64_t s_in_copy = s_in; */
/*     for (i=15;i>=0;i--) */
/*     { */
/*         int j = ((i << 2) + (i >> 2)) & 0xf; */
/*         s_out[j] = s_in_copy & 0xf; */
/*         s_in_copy >>= 4; */
/*     } */
/* } */

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

uint64_t addSpecificPos(uint64_t state, uint64_t val, int *pos, int noPos){
    for(int a=0; a<noPos; a++) {
        state ^= (uint64_t)((val >> (4*a)) & 0x0FUL) << ((15 - pos[a])*4);
    }
    return state;
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

void transpose_my(cell_t *state){
    cell_t t[16];
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            t[4*i + j] = state[i + 4*j];
        }
    }
    for(int i=0; i<16; i++) {
        state[i] = t[i];
    }
}

int memCmp(const void *a, const void *b, uint32_t nrof_byte){
    if(memcmp(a, b, nrof_byte) == 0){
        return 1;
    }
    else{
        return 0;
    }
}

int cmpTruncated(cell_t *a, cell_t *b, uint32_t nrof_byte){
    for(uint32_t i=0; i<nrof_byte; i++) {
        if (b[i] == 0){
            if(a[i] != 0)
                return 0;
        }
    }
    return 1;
}

#if 0
int cmpTruncated64(uint64_t a, uint64_t b){
    cell_t aa[16], bb[16];
    expandState(aa, a);
    expandState(bb, b);
    return cmpTruncated(aa, bb, VISIBLE);
} 
#else

extern uint64_t MASK;
extern uint64_t MASK3;
extern uint64_t MASKF;

int cmpTruncated64(uint64_t a, uint64_t b){
    uint64_t BM = (b | (b >> 2));
    BM = (BM | (BM >> 1)) & MASK;
    printf("BM %016llX\n", BM);
    uint64_t bb = BM | (BM << 1);
    bb = bb | (bb << 2);
    printf("bb  %016llX\n", bb);
    bb = ~ bb;
    printf("bb  %016llX\n", bb);
    bb = bb & a & MASKF;
    printf("bb  %016llX\n", bb);
    if (bb != 0) {
        return 0;
    }
    return 1;
}
#endif
int cmpTruncated64_my(uint64_t a, uint64_t b){
    uint64_t bb = (b ^ a) & MASKF;
    if (bb != 0) {
        return 0;
    }
    return 1;
}

//a = b ^ c
void XOR(cell_t a[16], const cell_t b[16], const cell_t c[16])
{
    for(int i = 0; i < 16; i++) a[i] = b[i] ^ c[i];
}

uint64_t getNumberOfZeroCells(uint8_t *bsc, int vv){
    uint64_t count = 0UL;
    for(int i=0; i<vv; i++){
        if (bsc[i] == 0) {
            count++;
        }
    }
    return count;
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
    uint64_t T2_2 = (T5_2 ^ K0_1 ^ K5_1) & 0x1UL;
    T = setBit(T, T2_2, 2, 2);
    //T2_0 = T2_1 ^ T5_0 ^ T5_1 ^ K0_3 ^ K5_3
    uint64_t T2_1 = extractBit(T, 2, 1);
    uint64_t T5_0 = extractBit(T, 5, 0);
    uint64_t T5_1 = extractBit(T, 5, 1);
    uint64_t K0_3 = extractBit(K, 0, 3);
    uint64_t K5_3 = extractBit(K, 5, 3);
    uint64_t T2_0 = (T2_1 ^ T5_0 ^ T5_1 ^ K0_3 ^ K5_3) & 0x1;
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
    uint64_t T15_0 = T15_2 ^ T15_3 ^ T3_0 ^ T3_2 ^ T3_3 ^ parity_K7 ^ parity_K8 ^ 1;
    T = setBit(T, T15_0, 15, 0);
    return T;
}
