/************************Optimized Implementation**********************************************************************/
#define ALLOCATE_TRY(var,code) if (! var) { var = code; if (! var) { printf("Out of memory!\n"); fflush(stdout); exit(-1);} }

typedef uint16_t *restrict uint16_p;
typedef uint64_t *restrict uint64_p;

uint16_p S_Table       = NULL;
uint16_p M_Table       = NULL;
uint16_p InvS_Table    = NULL;
uint16_p M_S_Table     = NULL;
uint16_p InvS_M_Table  = NULL;

void PreCompute_Tables();
bool Allocate_Tables();

uint64_t S(uint64_t in);
uint64_t M(uint64_t state);
uint64_t M_S(uint64_t state);
uint64_t InvS_M(uint64_t state);
uint64_t Tau(uint64_t in);
uint64_t InvTau(uint64_t in);
uint64_t transpose(uint64_t in);
uint64_t prince_orthomorphism(uint64_t in);

uint64_t round_constant[16] = {
  0x0000000000000000,
  0x13198A2E03707344,
  0xA4093822299F31D0,
  0x082EFA98EC4E6C89,
  0x452821E638D01377,
  0xBE5466CF34E90C6C,
  0x3F84D5B5B5470917,
  0x9216D5D98979FB1B,
  0xD1310BA698DFB5AC,
  0x2FFD72DBD01ADFB7,
  0xB8E1AFED6A267E96,
  0xBA7C9045F12C7F99,
  0x24A19947B3916CF7,
  0x0801F2E2858EFC16,
  0x636920D871574E69,
  0xA458FEA3F4933D7E};

uint64_t alpha = 0xC0AC29B7C97C50DD;
inline uint64_t S(uint64_t in)
{
	return ( (uint64_t)S_Table[in & 0xffff])
	     ^ (((uint64_t)S_Table[(in >> 16) & 0xffff]) << 16)
	     ^ (((uint64_t)S_Table[(in >> 32) & 0xffff]) << 32)
	     ^ (((uint64_t)S_Table[(in >> 48) & 0xffff]) << 48);
}

inline uint64_t Inv_S(uint64_t in)
{
	return ( (uint64_t)S_Table[in & 0xffff])
	     ^ (((uint64_t)S_Table[(in >> 16) & 0xffff]) << 16)
	     ^ (((uint64_t)S_Table[(in >> 32) & 0xffff]) << 32)
	     ^ (((uint64_t)S_Table[(in >> 48) & 0xffff]) << 48);
}

// applies MixColumn (a row consists of four consecutive nibbles)

inline uint64_t M(uint64_t in)
{
	return ( (uint64_t)M_Table[in & 0xffff])
	     ^ (((uint64_t)M_Table[(in >> 16) & 0xffff]) << 16)
	     ^ (((uint64_t)M_Table[(in >> 32) & 0xffff]) << 32)
	     ^ (((uint64_t)M_Table[(in >> 48) & 0xffff]) << 48);
}

// applies MixColumn and then the S-Box

inline uint64_t M_S(uint64_t in)
{
	return ( (uint64_t)M_S_Table[in & 0xffff])
	     ^ (((uint64_t)M_S_Table[(in >> 16) & 0xffff]) << 16)
	     ^ (((uint64_t)M_S_Table[(in >> 32) & 0xffff]) << 32)
	     ^ (((uint64_t)M_S_Table[(in >> 48) & 0xffff]) << 48);
}

// applies the inverse S-Box and then MixColumn 

inline uint64_t InvS_M(uint64_t in)
{
	return ( (uint64_t)InvS_M_Table[in & 0xffff])
	     ^ (((uint64_t)InvS_M_Table[(in >> 16) & 0xffff]) << 16)
	     ^ (((uint64_t)InvS_M_Table[(in >> 32) & 0xffff]) << 32)
	     ^ (((uint64_t)InvS_M_Table[(in >> 48) & 0xffff]) << 48);
}

uint64_t bit_permute_step(uint64_t x, uint64_t m, int shift)
{
    uint64_t t;
    t = ((x >> shift) ^ x) & m;
    x = (x ^ t) ^ (t << shift);
    return x;
}

uint64_t Tau(uint64_t in)
{
	uint64_t x = in;
#if 1
    x =  (x & 0xf000000000000f00)
      | ((x & 0x000000000f000000) <<  4)
      | ((x & 0x000000000000f000) <<  8)
      | ((x & 0x00000f0000000000) << 12)
      | ((x & 0x00000000000f0000) << 20)
      | ((x & 0x0000000000f00000) << 36)
      | ((x & 0x00000000000000f0) << 40)
      | ((x & 0x000000000000000f) << 48)
      | ((x & 0x00f0000000000000) >> 48)
      | ((x & 0x00000000f0000000) >> 28)
      | ((x & 0x0f0f000000000000) >> 24)
      | ((x & 0x000000ff00000000) >> 20)
      | ((x & 0x0000f00000000000) >>  4);
#else
	x = bit_permute_step(x, 0x00000f0f0f0f0000,  4);  // Butterfly, stage 0 (resolution is 4 bit words, not single bits)
	x = bit_permute_step(x, 0x000f00f0000f00f0,  8);  // Butterfly, stage 1
	x = bit_permute_step(x, 0x000000ff000000ff, 16);  // Butterfly, stage 2
	x = bit_permute_step(x, 0x000000000f0ff0f0, 32);  // Butterfly, stage 3
#endif
	return x;
}

uint64_t InvTau(uint64_t in)
{
	uint64_t x = in;
#if 1
   x =  (x & 0xf000000000000f00)        
     | ((x & 0x00000f0000000000) <<  4)  
     | ((x & 0x00000000000ff000) << 20)  
     | ((x & 0x0000000f0f000000) << 24)  
     | ((x & 0x000000000000000f) << 28)  
     | ((x & 0x00000000000000f0) << 48) 
     | ((x & 0x000f000000000000) >> 48) 
     | ((x & 0x0000f00000000000) >> 40) 
     | ((x & 0x0f00000000000000) >> 36)  
     | ((x & 0x000000f000000000) >> 20)  
     | ((x & 0x00f0000000000000) >> 12)  
     | ((x & 0x0000000000f00000) >>  8)  
     | ((x & 0x00000000f0000000) >>  4); 
#else
	x = bit_permute_step(x, 0x000000000f0ff0f0, 32);
	x = bit_permute_step(x, 0x000000ff000000ff, 16);
	x = bit_permute_step(x, 0x000f00f0000f00f0,  8);
	x = bit_permute_step(x, 0x00000f0f0f0f0000,  4);
#endif
	return x;
}

#define rol(A,B) ((A) << (B)) | ((A) >> (64-(B)))
#define ror(A,B) ((A) >> (B)) | ((A) << (64-(B)))

uint64_t h(uint64_t in)
{
	uint64_t x = in;
	x =   ((x & 0x00000f0000000000) <<  4)
	  | rol(x & 0x0f000000000f000f,   12)
	  |   ((x & 0x000000000f000000) << 36)
	  |   ((x & 0x0000000000000f00) << 44)
	  |   ((x & 0x000f000f00000000) >> 12)
	  |   ((x & 0xf0f0f0f0f0f0f0f0) >>  4);
	return x;
}

uint64_t invh(uint64_t in)
{
	uint64_t x = in;
    x =   ((x & 0x0f0f0f0f0f0f0f0f) <<  4)
  	  |   ((x & 0x000000f000f00000) << 12)
  	  |   ((x & 0x00f0000000000000) >> 44)
  	  |   ((x & 0xf000000000000000) >> 36)
  	  | rol(x & 0x00000000f000f0f0,    52)
	  |   ((x & 0x0000f00000000000) >>  4);
	return x;
}

//  0  1  2  3
//  4  5  6  7
//  8  9 10 11
// 12 13 14 15

// cells affected in array representation: 0,1,3,4,8,11,13
// transposed:                             0,4,12,1,2,14,7.
// reordered:                              0,1,2,4,7,12,14
// Mask                                    fff0 f00f 0000 f0f0 -> 0xfff0f00f0000f0f0

uint64_t omega(uint64_t V)
{
	// 	return (v >> 1) ^ (((v & 1) ^ ((v >> 1) & 1)) << 3);
	return (V & 0x000f0ff0ffff0f0f)
	     ^ ((V & 0xeee0e00e0000e0e0ULL) >> 1) ^ (((V & 0x1110100100001010ULL)  ^ ((V >> 1) & 0x1110100100001010ULL)) << 3);
}

uint64_t invomega(uint64_t V)
{
	// 	return ((v << 1) & 0xF) ^ ((v & 1) ^ ((v >> 3) & 1));
	return (V & 0x000f0ff0ffff0f0f)
	     ^ (((V & 0x7770700700007070ULL) << 1) & 0xfff0f00f0000f0f0ULL) ^ ((V & 0x1110100100001010ULL) ^ ((V >> 3) & 0x1110100100001010ULL));
}

uint64_t transpose(uint64_t in)
{
	uint64_t x = in;
	x = bit_permute_step(x, 0x0000f0f00000f0f0, 12);
	x = bit_permute_step(x, 0x00000000ff00ff00, 24);
	return x;
}

uint64_t prince_orthomorphism(uint64_t in)
{
	uint64_t x = in;

	x = transpose(x);
	x = ror(x,1) ^ (x >> 63);
	x = transpose(x);

	return x;
}

// /////////////////////////////////////

#ifdef DEBUG_TRACE
#undef DEBUG_TRACE
#endif

#ifdef DEBUG

#define DEBUG_TRACE(_txt_)                                 \
	printf(_txt_);                                         \
	printf("S = %016" PRIx64 ", T = %016" PRIx64 "\n", transpose(state),transpose(T));

#else

#define DEBUG_TRACE(_txt_)

#endif

bool Allocate_Tables()
{
	ALLOCATE_TRY(S_Table      , (uint16_p) malloc((1<<16) * sizeof(uint16_t)) );
	InvS_Table = S_Table;

	ALLOCATE_TRY(M_Table      , (uint16_p) malloc((1<<16) * sizeof(uint16_t)) );
	ALLOCATE_TRY(M_S_Table    , (uint16_p) malloc((1<<16) * sizeof(uint16_t)) );
	ALLOCATE_TRY(InvS_M_Table , (uint16_p) malloc((1<<16) * sizeof(uint16_t)) );

	return true; // success
}
void Release_Tables()
{
    free(S_Table);
    free(M_Table);
    free(M_S_Table);
    free(InvS_M_Table);
}

uint64_t compact_state(const cell_t s[16])
{
    int i;
    uint64_t result = 0ULL;
    for (i=0;i<16;i++)
    {
        int j = ((i << 2) + (i >> 2)) & 0xf;
        result <<= 4;
        result |= s[j];
    }
    return result;
}

void expand_state(cell_t s_out[16], uint64_t s_in)
{
    int i;
    uint64_t s_in_copy = s_in;
    for (i=15;i>=0;i--)
    {
        int j = ((i << 2) + (i >> 2)) & 0xf;
        s_out[j] = s_in_copy & 0xf;
        s_in_copy >>= 4;
    }
}
cell_t RotCell_Cellwise(cell_t val, int amount)
{
    return ( ((val << amount) | (val >> (4-amount))) & 0xF );
}

void MixColumns_Cellwise(cell_t state[16], int a, int b, int c)
{
    int j;
    cell_t temp0, temp1, temp2, temp3;

    for(j = 0; j < 4; j++) // for each column, that has 0,1,2,3 at the top
    {
        temp0 =                                              RotCell_Cellwise(state[j+4],a) ^ RotCell_Cellwise(state[j+8],b) ^ RotCell_Cellwise(state[j+12],c);
        temp1 = RotCell_Cellwise(state[j],c) ^                                             RotCell_Cellwise(state[j+8],a) ^ RotCell_Cellwise(state[j+12],b);
        temp2 = RotCell_Cellwise(state[j],b) ^ RotCell_Cellwise(state[j+4],c) ^                                              RotCell_Cellwise(state[j+12],a);
        temp3 = RotCell_Cellwise(state[j],a) ^ RotCell_Cellwise(state[j+4],b) ^ RotCell_Cellwise(state[j+8],c);

        state[j]    = temp0;
        state[j+4]  = temp1;
        state[j+8]  = temp2;
        state[j+12] = temp3;
    }
}

void PreCompute_Tables()
{
    int in0,in1,in2,in3;
    int out0,out1,out2,out3;
    int i;

    for (in0 = 0; in0 < 16; in0++)
    {
        out0 = sbox_4[in0];
        for (in1 = 0; in1 < 16; in1++)
        {
            out1 = sbox_4[in1];
            for (in2 = 0; in2 < 16; in2++)
            {
                out2 = sbox_4[in2];
                for (in3 = 0; in3 < 16; in3++)
                {
                    out3 = sbox_4[in3];
                    S_Table[(in0 << 12) | (in1 << 8) | (in2 << 4) | in3] = (out0 << 12) | (out1 << 8) | (out2 << 4) | out3;
                }
            }
        }
    }

    cell_t A[16];
    uint64_t in64, state;

    for (i=0; i<(1<<16); i++)
    {
        in64 = (uint64_t)i;
        expand_state(A,in64);
        MixColumns_Cellwise(A,ROTATION_A,ROTATION_B,ROTATION_C);
        state = compact_state(A);
        M_Table[i] = (uint16_t)state;
    }

    for (i=0; i<(1<<16); i++)
    {
        InvS_M_Table[i] = M_Table[S_Table[i]];
        M_S_Table[i] = S_Table[M_Table[i]];
    }
}
/********************************************************************************************************/

uint64_t qarma64_opt(const uint64_t input,
             const uint64_t W, const uint64_t W_p,
             const uint64_t core_key, const uint64_t middle_key,
             const uint64_t tweak,
             int R)
{
	uint64_t state, T, K;
	int i;

	state = input;
	T	  = tweak;
	K     = core_key;
	DEBUG_TRACE("Q64 - initial state:                           ");

    // Initial whitening

	state ^= W;
	DEBUG_TRACE("Q64 - after whitening with w:                  ");

	// The R forward rounds

	for(i = 0; i < R; i++)
	{
		// A round is Add_Cellwise(constant+key+tweak), then S-Box, MixColumns_Cellwise, and Shuffle

		state ^= round_constant[i];
		state ^= K;
		state ^= T;
		DEBUG_TRACE("Q64 - round %.2i - after AddRoundTK:             " COMMA i);

		if (i != 0)
		{
			state = Tau(state);
			DEBUG_TRACE("Q64 - round %.2i - after ShuffleCells:           " COMMA i);
#if 1
			state = M_S(state);
			DEBUG_TRACE("Q64 - round %.2i - after MixColumns_Cellwise,SubCells:    " COMMA i);
#else
			state = M(state);
			DEBUG_TRACE("Q64 - round %.2i - after MixColumns_Cellwise:             " COMMA i);
			state = S(state);
			DEBUG_TRACE("Q64 - round %.2i - after SubCells:               " COMMA i);
#endif
		}
		else
		{
			state = S(state);
			DEBUG_TRACE("Q64 - round %.2i - after SubCells:               " COMMA i);
		}

		// and update the tweak

		T = h(T);
		T = omega(T);
	} 

	// The pseudo-reflector

    // first whitening key addition

	state ^= W_p;
	state ^= T;
	DEBUG_TRACE("Q64 - reflector - after AddRoundTK:            ");

	// full forward diffusion layer

	state  = Tau(state);
	DEBUG_TRACE("Q64 - reflector - after ShuffleCells:          ");
	state  = M_S(state);
#if 0
	state  = M(state);
	DEBUG_TRACE("Q64 - reflector - after MixColumns_Cellwise:            ");
	state  = S(state);
#endif
	DEBUG_TRACE("Q64 - reflector - after MixColumns_Cellwise, SubCells:  ");

	// bridge

	state  = Tau(state);
    DEBUG_TRACE("Q64 - bridge - after ShuffleCells:             ");

	state  = M(state);
	DEBUG_TRACE("Q64 - bridge - after MixColumns_Cellwise:               ");

	state ^= middle_key;
	DEBUG_TRACE("Q64 - bridge - after adding middle_key:        ");

	state  = InvTau(state);
	DEBUG_TRACE("Q64 - bridge - after InvShuffleCells:          ");
	//state  = Inv_S(state);
	//DEBUG_TRACE("Q64 - reflector - after middle part:           ");

    // backward round with whitening key in place of core key

	//state  = Inv_S(state);
	state  = InvS_M(state);
	DEBUG_TRACE("Q64 - reflector - after SubCells,MixColumns_Cellwise:   ");
	state  = InvTau(state);
	DEBUG_TRACE("Q64 - reflector - after InvShuffleCells:       ");

	state ^= W;
	state ^= T;

	DEBUG_TRACE("Q64 - reflector - after AddRoundTK:            ");

	// The R backward rounds

    for(i = 0; i < R; i++)
    {
		T = invomega(T);
		T = invh(T);

		if (i != R-1)
		{
			state  = InvS_M(state);
			DEBUG_TRACE("Q64 - inverse round %.2i - after SubCells,MixColumns_Cellwise: " COMMA R-1-i);
			state = InvTau(state);
			DEBUG_TRACE("Q64 - inverse round %.2i - after ShuffleCells:   " COMMA R-1-i);
		}
		else
		{
			state = S(state); // InvS same as S
			DEBUG_TRACE("Q64 - inverse round %.2i - after SubCell:        " COMMA R-1-i);
		}

		state ^= K;
		state ^= T;
		state ^= round_constant[R-1-i];
		state ^= alpha;
		DEBUG_TRACE("Q64 - inverse round %.2i - after AddRoundTK:     " COMMA R-1-i);
	}

    // Final whitening with W_p

	state ^= W_p;
	DEBUG_TRACE("Q64 - final state (after whitening with w'):   ");

	return state;
}

uint64_t qarma64_r3_opt(const uint64_t input,
             const uint64_t W, const uint64_t W_p,
             const uint64_t core_key, const uint64_t middle_key,
             const uint64_t tweak)
{
	uint64_t state, T[4], K;
	int i;

	state = input;
	T[0]  = tweak;
	T[1]  = omega(h(T[0]));
	T[2]  = omega(h(T[1]));
	T[3]  = omega(h(T[2]));

	K     = core_key;

    // Initial whitening

	state ^= W;

	// The R forward rounds

	state ^= round_constant[0];
	state ^= K;
	state ^= T[0];

	state = S(state);

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

    // first whitening key addition

	state ^= W_p;
	state ^= T[3];

	// full forward diffusion layer

	state  = Tau(state);
	state  = M_S(state);

	// bridge

	state  = Tau(state);
	state  = M(state);
	state ^= middle_key;
	state  = InvTau(state);

    // backward round with whitening key in place of core key
	state  = InvS_M(state);
	state  = InvTau(state);

	state ^= W;
	state ^= T[3];

	// The R backward rounds

	state  = InvS_M(state);
	state  = InvTau(state);

	state ^= K;
	state ^= T[2];
	state ^= round_constant[2];
	state ^= alpha;


	state  = InvS_M(state);
	state  = InvTau(state);

	state ^= K;
	state ^= T[1];
	state ^= round_constant[1];
	state ^= alpha;

	state = S(state); // InvS same as S

	state ^= K;
	state ^= T[0];
	state ^= round_constant[0];
	state ^= alpha;

    // Final whitening with W_p

	state ^= W_p;

	return state;
}

//Only the first 0.5 rounds
uint64_t qarma64_half(const uint64_t input,
             const uint64_t W, const uint64_t W_p,
             const uint64_t core_key, const uint64_t middle_key,
             const uint64_t tweak){
	uint64_t state, T[4], K;
	int i;

	state = input;
	T[0]  = tweak;
	T[1]  = omega(h(T[0]));
	T[2]  = omega(h(T[1]));
	T[3]  = omega(h(T[2]));

	K     = core_key;

    // Initial whitening

	state ^= W;

	// The R forward rounds

	state ^= round_constant[0];
	state ^= K;
	state ^= T[0];

	state = S(state);
	return state;
}

uint64_t qarma64_one_half(const uint64_t input,
             const uint64_t W, const uint64_t W_p,
             const uint64_t core_key, const uint64_t middle_key,
             const uint64_t tweak)
{
	uint64_t state, T[4], K;
	int i;

	state = input;
	T[0]  = tweak;
	T[1]  = omega(h(T[0]));
	T[2]  = omega(h(T[1]));
	T[3]  = omega(h(T[2]));

	K     = core_key;

    // Initial whitening

	state ^= W;

	// The R forward rounds

	state ^= round_constant[0];
	state ^= K;
	state ^= T[0];

	state = S(state);

	state ^= round_constant[1];
	state ^= K;
	state ^= T[1];

	state = Tau(state);
	state = M_S(state);
	return state;
}
