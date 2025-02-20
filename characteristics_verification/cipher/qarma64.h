/************************Optimized Implementation**********************************************************************/
#include "tables.h"
uint64_t S(uint64_t in);
uint64_t M(uint64_t state);
uint64_t M_S(uint64_t state);
uint64_t InvS_M(uint64_t state);
uint64_t Tau(uint64_t in);
uint64_t InvTau(uint64_t in);
uint64_t transpose(uint64_t in);
uint64_t prince_orthomorphism(uint64_t in);
const uint64_t alpha = 0xc2c50990ab7dc7cd;
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

//Without first 1.5 round
uint64_t qarma64_23(const uint64_t input,
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
uint64_t qarma64_33(const uint64_t input,
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
