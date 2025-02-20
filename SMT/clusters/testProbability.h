struct encArgs{
    uint64_t inD;
    uint64_t outD;
    uint64_t tD;
    
    uint64_t T0c;
    uint64_t T1c;

    uint64_t w0c;
    uint64_t w1c;
    uint64_t k0c; 
    uint64_t k1c;

    uint64_t HIT;

    uint64_t data;
    uint64_t *dataArr;

    uint64_t T;
};
typedef struct encArgs encArgs;

//Without first 1.5 round
uint64_t qarma64_r3_opt_323(const uint64_t input,
             const uint64_t W, const uint64_t W_p,
             const uint64_t core_key, const uint64_t middle_key,
             const uint64_t T[4]){
    uint64_t state, K;
	int i;

	state = input;
    K     = core_key;
	
	//1 forward rounds
    state ^= round_constant[2];
	state ^= K;
	state ^= T[2];
	state = Tau(state);
	state = M_S(state);

	// The pseudo-reflector
	state ^= W_p;
	state ^= T[3];
	state  = Tau(state);
	state  = M_S(state);

	// bridge
	state  = Tau(state);
	state  = M(state);
	state ^= middle_key;
	state  = InvTau(state);

	state  = InvS_M(state);
	state  = InvTau(state);
	state ^= W;
	state ^= T[3];

	//2 backward rounds
	state  = InvS_M(state);
	state  = InvTau(state);

	state ^= K;
	state ^= T[2];
	state ^= round_constant[2];
	state ^= alpha;

	state  = InvS_M(state);
	state  = InvTau(state);

	/* state ^= K; */
	/* state ^= T[1]; */
	/* state ^= round_constant[1]; */
	/* state ^= alpha; */
	return state;
}
//Without first 0.5 round
uint64_t qarma64_r3_opt_222(const uint64_t input,
             const uint64_t W, const uint64_t W_p,
             const uint64_t core_key, const uint64_t middle_key,
             const uint64_t T[4]){
	uint64_t state, K;
	int i;

	state = input;
	K     = core_key;

	//1 forward rounds
	state ^= round_constant[2];
	state ^= K;
	state ^= T[2];
	state = Tau(state);
	state = M_S(state);

	// The pseudo-reflector
	state ^= W_p;
	state ^= T[3];
	state  = Tau(state);
	state  = M_S(state);
	// bridge
	state  = Tau(state);
	state  = M(state);
	state ^= middle_key;
	state  = InvTau(state);
	//End bridge
	state  = InvS_M(state);
	state  = InvTau(state);
	state ^= W;
	state ^= T[3];

	//1 backward rounds
	state  = InvS_M(state);
	state  = InvTau(state);
	/* state ^= K; */
	/* state ^= T[2]; */
	/* state ^= round_constant[2]; */
	/* state ^= alpha; */

	return state;
}
//Without first 0.5 round
uint64_t qarma64_r3_opt_333(const uint64_t input,
             const uint64_t W, const uint64_t W_p,
             const uint64_t core_key, const uint64_t middle_key,
             const uint64_t T[4]){
	uint64_t state,  K;
	int i;

	state = input;
	K     = core_key;

	//2 forward rounds
	state ^= round_constant[1];
	state ^= K;
    state ^= T[1];
	state = Tau(state);
	state = M_S(state);

	state ^= round_constant[2];
	state ^= K;
	state ^= T[2];
	state = Tau(state);
	state = M_S(state);

	// The pseudo-reflector
	state ^= W_p;
	state ^= T[3];
	state  = Tau(state);
	state  = M_S(state);
	// bridge
	state  = Tau(state);
	state  = M(state);
	state ^= middle_key;
	state  = InvTau(state);
	//End bridge
	state  = InvS_M(state);
	state  = InvTau(state);
	state ^= W;
	state ^= T[3];

	//2 backward rounds
	state  = InvS_M(state);
	state  = InvTau(state);
	state ^= K;
	state ^= T[2];
	state ^= round_constant[2];
	state ^= alpha;

	state  = InvS_M(state);
	state  = InvTau(state);
	/* state ^= K; */
	/* state ^= T[1]; */
	/* state ^= round_constant[1]; */
	/* state ^= alpha; */

	return state;
}

void* count_hit323(void *args1){
    encArgs *args = (encArgs*) args1;
    uint64_t Dc, P0, P1, C0, C1, C0c, C1c;
    uint64_t HIT = 0UL;
    uint64_t inDc  = transpose(args->inD);

    uint64_t T0[4], T1[4];
    T0[0]  = args->T0c;
    T0[1]  = omega(h(T0[0]));
    T0[2]  = omega(h(T0[1]));
    T0[3]  = omega(h(T0[2]));
    
    T1[0]  = args->T1c;
    T1[1]  = omega(h(T1[0]));
    T1[2]  = omega(h(T1[1]));
    T1[3]  = omega(h(T1[2]));


    /* printf("---------------Normal Encryption: data = %ld -------------------\n", data); */
    for (uint64_t i=0; i<args->data; i++) {
        P0 = args->dataArr[i]; // generateState64();
        P1 = P0 ^ inDc;

        C0c =  qarma64_r3_opt_323(P0, args->w0c, args->w1c, args->k0c, args->k1c, T0);
        C1c =  qarma64_r3_opt_323(P1, args->w0c, args->w1c, args->k0c, args->k1c, T1);

        Dc = C0c ^ C1c;
        Dc = transpose(Dc);
        
        args->HIT += cmpTruncated64_my(Dc, args->outD);
    }
    pthread_exit(NULL);
}
void* count_hit222(void *args1){
    encArgs *args = (encArgs*) args1;
    uint64_t Dc, P0, P1, C0, C1, C0c, C1c;
    uint64_t HIT = 0UL;
    uint64_t inDc  = transpose(args->inD);

    uint64_t T0[4], T1[4];
    T0[0]  = args->T0c;
    T0[1]  = omega(h(T0[0]));
    T0[2]  = omega(h(T0[1]));
    T0[3]  = omega(h(T0[2]));
    
    T1[0]  = args->T1c;
    T1[1]  = omega(h(T1[0]));
    T1[2]  = omega(h(T1[1]));
    T1[3]  = omega(h(T1[2]));


    /* printf("---------------222: data = %ld -------------------\n", args->data); */
    for (uint64_t i=0; i<args->data; i++) {
        P0 = args->dataArr[i]; 
        P1 = P0 ^ inDc;

        C0c =  qarma64_r3_opt_222(P0, args->w0c, args->w1c, args->k0c, args->k1c, T0);
        C1c =  qarma64_r3_opt_222(P1, args->w0c, args->w1c, args->k0c, args->k1c, T1);

        Dc = C0c ^ C1c;
        Dc = transpose(Dc);
        
        args->HIT += cmpTruncated64_my(Dc, args->outD);
    }
    pthread_exit(NULL);
}
void* count_hit333(void *args1){
    encArgs *args = (encArgs*) args1;
    
    uint64_t Dc, P0, P1, C0, C1, C0c, C1c;
    uint64_t HIT = 0UL;
    uint64_t inDc  = transpose(args->inD);

    uint64_t T0[4], T1[4];
    T0[0]  = args->T0c;
    T0[1]  = omega(h(T0[0]));
    T0[2]  = omega(h(T0[1]));
    T0[3]  = omega(h(T0[2]));
    
    T1[0]  = args->T1c;
    T1[1]  = omega(h(T1[0]));
    T1[2]  = omega(h(T1[1]));
    T1[3]  = omega(h(T1[2]));


    for (uint64_t i=0; i<args->data; i++) {
        P0 = args->dataArr[i];
        P1 = P0 ^ inDc;

        C0c =  qarma64_r3_opt_333(P0, args->w0c, args->w1c, args->k0c, args->k1c, T0);
        C1c =  qarma64_r3_opt_333(P1, args->w0c, args->w1c, args->k0c, args->k1c, T1);

        Dc = C0c ^ C1c;
        Dc = transpose(Dc);
        
        args->HIT += cmpTruncated64_my(Dc, args->outD);
    }
    pthread_exit(NULL);
}

uint64_t encryptThreaded(int parameter, uint64_t inD, uint64_t outD, uint64_t tD, 
                         uint64_t K, uint64_t W, uint64_t data, int type) {
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

    pthread_t thread_ids[threads];
    encArgs  thread_args[threads];
    uint64_t data_in_each_thread = (data / threads);

    uint64_t T0;
    if (EQ12 == 1){  //If verify Charecteristics 12, set tweak based on key k0
        //this function defined in utility.h
        T0 = generateTweakCondEq12(compactState(k0) ^ transpose(round_constant[2]));
    }
    else if (EQ14 == 1) { //If verify Charecteristics 12, set tweak based on key k0
        //this function defined in utility.h
        T0 = generateTweakCondEq14(compactState(k0) ^ transpose(round_constant[2]));
    }
    else{
        T0 = generateState64();
    }
    uint64_t T1 = T0 ^ tD;
    uint64_t T0c = transpose(T0);
    uint64_t T1c = transpose(T1);
    
    for(int i=0; i<threads; i++){
        thread_args[i].inD = inD;
        thread_args[i].outD = outD; // ^ tD;
        thread_args[i].tD = tD;
                
        thread_args[i].T0c = T0c;
        thread_args[i].T1c = T1c;

        thread_args[i].w0c = w0c;
        thread_args[i].w1c = w1c;
        thread_args[i].k0c = k0c;
        thread_args[i].k1c = k1c;

        thread_args[i].HIT = 0;
        thread_args[i].data = data_in_each_thread;
        thread_args[i].dataArr = (uint64_t *)malloc(sizeof(uint64_t)*data_in_each_thread);
        for (uint64_t j=0UL; j<data_in_each_thread; j++) {
            thread_args[i].dataArr[j] = generateState64();
        }
    }

    if(type == 333){
    for(int i=0; i < threads; i++){
        pthread_create(thread_ids + i, NULL, count_hit333, (void*) (thread_args + i));
    }
    }
    else if(type == 323){
    for(int i=0; i < threads; i++){
        pthread_create(thread_ids + i, NULL, count_hit323, (void*) (thread_args + i));
    }
    }
    else if(type == 222){
    for(int i=0; i < threads; i++){
        pthread_create(thread_ids + i, NULL, count_hit222, (void*) (thread_args + i));
    }
    }
    else{
        printf("WRONG TYPE\n");
        exit(0);
    }

    for(int i=0; i < threads; i++){
        pthread_join(thread_ids[i], NULL);
    }
    uint64_t HIT = 0UL;
    for(int i=0; i<threads; i++){
        HIT += thread_args[i].HIT;
        free(thread_args[i].dataArr);
    }
    return HIT;
}
uint64_t test_probability(int parameter, int type, uint64_t tD, uint64_t inD, uint64_t outD, uint64_t data){
    uint64_t K, W;    
    K = generateState64();
    W = generateState64();
    /* K = 0x3BC029496A4BAD69UL; */
    /* W = 0x542186212F0F4855UL; */ 
    /* printf("uint64_t K = 0x%016lX; \n", K); */
    /* printf("uint64_t W = 0x%016lX; \n", W); */
    uint64_t HIT = encryptThreaded(parameter, inD, outD, tD, K, W, data, type);
    return HIT;
}
