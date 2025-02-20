#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
#include <stdbool.h>
#include <math.h>

#define PRINT

int COUNT_EQ = 0;
int EXP = 100;
int EQ12_COND = 0;
int EQ14_COND = 0;
uint64_t bb0 = 0;
uint64_t bb1 = 0;

unsigned int threads = 64;
typedef unsigned char cell_t;


#include "utility.h"
#include "./cipher/qarma64.h"   //An efficient table based implementation of Qarma-64
#include "./cipher/key_schedule.h"
#include "testProbability.h"

void calculate_stat(long double *data, long double nr_of_pairs, int expp, uint64_t randomm, long double sdr, uint64_t logPairs) {
    long double exp = (long double)expp;
    long double random_hit = (long double)randomm;
    long double sum = 0.0, sumSq = 0.0;
    long double min = data[0], max = data[0];
    long double mean, l2_mean, sd, l2_sd, l2_min, l2_max;
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
    l2_sd   = logl(sd)  / log(2.0);
    l2_min  = logl(min) / log(2.0);
    l2_max  = logl(max) / log(2.0);
    long double prob      = (mean )/ nr_of_pairs;
    long double l2_prob   = logl(prob)  / log(2.0);

#ifdef PRINT
    printf("\n-------------------------------------------------------------\n");
    printf("Mean: %Lf 2^(%Lf)\n", mean, l2_mean);
    printf("sd  : %Lf 2^(%Lf)\n", sd,   l2_sd);
    printf("Min : %Lf 2^(%Lf)\n", min,  l2_min);
    printf("Max : %Lf 2^(%Lf)\n", max,  l2_max);
    printf("prob: %Lf 2^(%Lf)\n", prob, l2_prob);
    printf("\n-------------------------------------------------------------\n");
#endif
    printf("\\( %d \\) & \\( %.2Lf \\) & \\( %.2Lf \\) & \\( \\pm\\) & \\( %.2Lf \\) & \\( %.0Lf \\) & \\( %.0Lf \\) & \\( %.2Lf \\) ", COUNT_EQ, sdr, mean, sd, min, max, -l2_prob);
    /* printf("\\( %d \\) & \\( %.2Lf \\pm %.2Lf \\) & \\( %.0Lf \\) & \\( %.0Lf \\) & \\( %.2Lf \\) & \\( %.2Lf \\) ", COUNT_EQ, mean, sd, min, max, sdr, -l2_prob); */
}
void run(int type, int logData, uint64_t tD, uint64_t inD, uint64_t outD,
         uint64_t MASK, uint64_t numZeroCell, long double q) {
#ifdef PRINT
    printf("...............Given Diff..................................\n");
    printf("tD %016lX  \n",  tD);
    printf("inD %016lX \n",  inD);
    printf("outD %016lX \n", outD);
    printf("MASK %016lX \n", MASK);
    printf("Number of zero cells at \\Delta_out = %ld \n", numZeroCell);
#endif
    uint64_t data = (1UL << logData);
    uint64_t HIT = 0UL;
    uint64_t totalHIT = 0UL;
    uint64_t randomHit = (1UL << (logData - 4*numZeroCell));
    long double temp = (long double) (1UL << (4*numZeroCell));
    long double sdr = sqrt((long double)randomHit * ((temp - 1)/temp));
    long double th = (long double)data / (2.0*pow(2, q));
    uint64_t thresholdForSuccess =  randomHit + (uint64_t)ceil(th);

    long double arr[EXP];
    long double hitD; 
    int expp = 0;
    struct timespec start, end;
    double time_meter;

    for(int i=0; i<EXP; i++){
        clock_gettime(CLOCK_MONOTONIC, &start);
        HIT = test_probability(type, tD, inD, outD, MASK, data);
        clock_gettime(CLOCK_MONOTONIC, &end);
        time_meter = ((double)(end.tv_sec - start.tv_sec));
        if (HIT >= thresholdForSuccess) {
            expp ++;
        }
        hitD = (long double)HIT - (long double)randomHit;
        arr[i] = hitD;
        totalHIT += HIT;
#ifdef PRINT
        printf("i = %d: hitD: %Lf (2^%Lf) HIT: %lld (2^%Lf) time %lf s\n",i, hitD, logl( (long double) hitD) / logl(2.0), HIT, logl( (long double) HIT) / logl(2.0) - logData, time_meter);
        fflush(stdout);
#endif
    }

#ifdef PRINT
    printf("\n");
    printf("Successful experiments = %d out of %d \n", expp, EXP);
    
    printf("Expected Random Hit = %llu,  (2^%5.2Lf) %Lf \n",randomHit,logl((double)randomHit)/logl(2.0), temp);
    printf("s.d.(\\eta) = %Lf %ld\n", sdr);
    printf("threshold for success = %ld\n", thresholdForSuccess);
    printf("Number Of Pairs in each experiments (N): (2^%5.2Lf) \n", logl( (double) data) / logl(2.0));
#endif
    calculate_stat(arr, (long double)data, EXP, randomHit, sdr, logData);
    printf("& %d\\ofhundred & \\( (%d, %d) \\) \\\\ \n", expp, bb0, bb1);
}

#include "equations.h"
int main(){
    srand((unsigned) time(NULL));

//Choose function from equation.h
#if defined(FIG12) || defined(FIG13) || defined(FIG12_STAR) || defined(FIG13_STAR)
    configure_extra();
#else
    configure();
#endif

    return 0;
}
