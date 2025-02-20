#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
#include <stdbool.h>
#include <math.h>
#define PRINT

int VISIBLE = 16;
int EXP = 16;
int EQ12 = 0;
int EQ14 = 0;
unsigned int threads = 64;
uint64_t MASK;
uint64_t MASK3;
uint64_t MASKF;

uint64_t TOTAL = 0;
pthread_mutex_t lock;

#define RotCell(val,amount) ( (((val) << (amount)) | ((val) >> (4-(amount)))) & 0xF )
#define SubCell4(cells) do { for(int i = 0; i < 16; i++) (cells)[i] = sbox_4[(cells)[i]]; } while(0)
#define SubCell4_inv(cells) do { for(int i = 0; i < 16; i++) (cells)[i] = sbox_4_inv[(cells)[i]]; } while(0)
typedef unsigned char cell_t;

#include "utility.h"
#include "qarma64.h"
#include "qarma64_opt_const_table.h"
#include "testProbability.h"
void calculate_stat(long double *data, long double nr_of_pairs, int expp, uint64_t randomm) {
    long double exp = (long double)expp;
    long double random_hit = (long double)randomm;
    long double sum = 0.0, sumSq = 0.0;
    long double min = data[0], max = data[0];
    long double mean, mean1, l2_mean, l2_mean1, sd, l2_sd, l2_min, l2_max, sdr, l2_sdr;
    long double mean_plus_sd, mean_minus_sd, l2_mean_plus_sd, l2_mean_minus_sd;
    // Calculate sum, min, max in one loop
    for (int i = 0; i < expp; i++) {
        sum += data[i];
        if (data[i] < min) {
            min = data[i];
        }
        if (data[i] > max) {
            max = data[i];
        }
    }
    mean = sum / exp;

    // Calculate sum of squared differences from the mean
    for (int i = 0; i < exp; i++) {
        sumSq += (data[i] - mean) * (data[i] - mean);
    }
    sd = sqrt(sumSq / exp);
    
    l2_mean = logl(mean)/ log(2.0);
    l2_min  = logl(min) / log(2.0);
    l2_max  = logl(max) / log(2.0);
    l2_sd   = logl(sd)  / log(2.0);
    

    long double prob      = (mean )/ nr_of_pairs;
    long double l2_prob   = logl(prob)  / log(2.0);
    
    mean_plus_sd  = mean1 + sd;
    mean_minus_sd = mean1 - sd;
    l2_mean_plus_sd  = logl(mean_plus_sd)/ log(2.0);
    l2_mean_minus_sd = logl(mean_minus_sd)/ log(2.0);

    printf("\n-------------------------------------------------------------\n");
    printf("Mean: %Lf %Lf\n", mean, l2_mean);
    printf("Min : %Lf %Lf\n", min,  l2_min);
    printf("Max : %Lf %Lf\n", max,  l2_max);
    printf("sd  : %Lf %Lf\n", sd,   l2_sd);
    printf("prob: %Lf %Lf\n", prob,   l2_prob);
    printf("\n-------------------------------------------------------------\n");
}
void run(int parameter, int type, int logData, cell_t *ft, cell_t *fsc, cell_t *bsc) {
    uint64_t tD, inD, outD;
    tD   = compactState(ft);
    inD  = compactState(fsc);
    outD = compactState(bsc);
    printf("outD %016lX \n", outD);
#ifdef PRINT
    printf("...............Given Diff..................................\n");
    displayCols64(tD);
    displayCols(ft);
    displayCols64(inD);
    displayCols(fsc);
    displayCols64(outD);
    displayCols(bsc);
    printf("...........................................................\n");
    printf("VISIBLE = %d\n", VISIBLE);
    printf("...........................................................\n");
#endif
    printf("outD %016lX \n", outD);
    printf("inD %016lX \n", inD);
    printf("inD %016lX \n", transpose(Tau(transpose(inD))));
    printf("outD = 0x%016llX \n", transpose(outD));
    uint64_t data = (1UL << logData);
    uint64_t HIT = 0UL;
    uint64_t totalHIT = 0UL;
    
    //---------------------------------------------------------------------
    printf("....................To Copy............................\n");
    printf("    type = %d; EXP  = %d; logData = %d; numZeroCell = %d;\n", type - 300, EXP, logData, VISIBLE);
    printf("    tD   = 0x%016lXUL;\n",  tD);
    printf("    inD  = 0x%016lXUL;\n",  inD);
    printf("    outD = 0x%016lXUL;\n", outD);
    printf("    MASK = 0x%016lXUL;\n", MASKF);
    //---------------------------------------------------------------------


    TOTAL = data;
    uint64_t numZeroCell = VISIBLE;
    uint64_t randomHit = (1UL << (logData - 4*numZeroCell));
    long double temp = (long double) (1UL << (4*numZeroCell));
    printf("Expected Random Hit = %llu,  (2^%5.2Lf) %Lf \n",randomHit,logl((double)randomHit)/logl(2.0), temp);
    long double sdr = sqrt((long double)randomHit * ((temp - 1)/temp));
    uint64_t intSdr = (uint64_t)ceil(sdr); 
    uint64_t threas = randomHit + intSdr;
    printf("sdr = %Lf %ld %ld\n", sdr, intSdr, threas);

    long double arr[EXP];
    long double hitD; 
    int expp = 0;
    struct timespec start, end;
    double time_meter;

    for(int i=0; i<EXP; i++){
        clock_gettime(CLOCK_MONOTONIC, &start);
        HIT = test_probability(parameter, type, tD, inD, outD, data);
        clock_gettime(CLOCK_MONOTONIC, &end);
        time_meter = ((double)(end.tv_sec - start.tv_sec));
        if (HIT > threas) {
            expp ++;
        }
        hitD = (long double)HIT - (long double)randomHit;
        arr[i] = hitD;
        totalHIT += HIT;
        printf("i = %d: hitD: %Lf (2^%Lf) HIT: %lld (2^%Lf) time %lf s\n",i, hitD, logl( (long double) hitD) / logl(2.0), HIT, logl( (long double) HIT) / logl(2.0) - logData, time_meter);
        fflush(stdout);
    }
    printf("\n");
    printf("Succesful experiments = %d \n", expp);
    
    calculate_stat(arr, (long double)data, EXP, randomHit);
    long double expectedHit = (long double)totalHIT/(long double)EXP;
    printf("totalHIT: %Lf (2^%5.2Lf) \n", expectedHit, logl(expectedHit) / logl(2.0));
    printf("TOTAL: (2^%5.2Lf) \n", logl( (double) TOTAL) / logl(2.0));

    hitD = expectedHit - (long double)randomHit;
    printf("HIT due to diff = %Lf,  (2^%5.2Lf) \n",hitD, logl(hitD)/logl(2.0));

    long double prob = hitD/(double)data;
    printf("Prob = %Lf,  (2^%5.2Lf) \n",prob,logl(prob)/logl(2.0));

}
#include "configure.h"
int main(){
    srand((unsigned) time(NULL));
    /* configure2(); */
    /* configure3(); */
    configure_special_eqn_w_24();
    /* configure_special_eqn_w_26(); */
    return 0;
}
