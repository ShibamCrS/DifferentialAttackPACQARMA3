#define ROTATION_A_MID  1
#define ROTATION_B_MID  2
#define ROTATION_C_MID  1
#define RotCell(val,amount) ( (((val) << (amount)) | ((val) >> (4-(amount)))) & 0xF )

void MixColumns(cell_t state[16], int a, int b, int c)
{
	int j;
    cell_t temp0, temp1, temp2, temp3;

	for(j = 0; j < 4; j++) // for each column, that has 0,1,2,3 at the top
	{
        temp0 =                       RotCell(state[j+4],a) ^ RotCell(state[j+8],b) ^ RotCell(state[j+12],c);
        temp1 = RotCell(state[j],c) ^                         RotCell(state[j+8],a) ^ RotCell(state[j+12],b);
        temp2 = RotCell(state[j],b) ^ RotCell(state[j+4],c) ^                         RotCell(state[j+12],a);
        temp3 = RotCell(state[j],a) ^ RotCell(state[j+4],b) ^ RotCell(state[j+8],c);

        state[j]    = temp0;
        state[j+4]  = temp1;
        state[j+8]  = temp2;
        state[j+12] = temp3;
	}
}
// in: core and whitening keys w0 and k0
// out: center core keys k1 and k1_M, second whitening key w1

void PRINCEExpansion(const cell_t w0[16], cell_t * w1)
{
	cell_t oldtemp;
	cell_t newtemp;
	int i;

	// create w1 by expansion
	// first w0 >>> 1

	oldtemp = 0;
	for (i = 0; i<16; i++)
	{
		newtemp = w0[i] & 0x1;
		w1[i] = (w0[i] >>  1) & 0xf;
		w1[i] = w1[i] ^ oldtemp;
		oldtemp = (newtemp << 3);
	}
	w1[0]  ^= oldtemp;

	// then add w0 >> 63

	w1[15] ^= (w0[0] >> 3);
}

void W2Expansion(const cell_t w0[16], cell_t * w1)
{
	cell_t oldtemp;
	cell_t newtemp;
	int i,c;

	// create w1 by expansion
	// first w0 >>> 1

	for (c = 0; c < 4; c ++)
	{
		oldtemp = 0;
		for (i = 0; i < 4; i ++)
		{
			newtemp = w0[i*4+c] & 0x1;
			w1[i*4+c] = (w0[i*4+c] >>  1) & 0xf;
			w1[i*4+c] = w1[i*4+c] ^ oldtemp;
			oldtemp = (newtemp << 3);
		}
		w1[c]  ^= oldtemp;

		// then add w0 >> 15

		w1[c+12] ^= (w0[c] >> 3);
	}
}

void KeySpecialisation(const cell_t k0[16], const cell_t w0[16],
	cell_t * k1, cell_t * k1_M, cell_t * w1)
{
	int i;
	
	PRINCEExpansion(w0, w1);
	//W2Expansion(w0, w1);

#if 0
	oldtemp = 0;
	for (i = 15; i>=0; i--)
	{
		newtemp = k0[i] & 0x8;
		k1[i] = (k0[i] << 1) & 0xf;
		k1[i] = k1[i] ^ oldtemp;
		oldtemp = (newtemp >> 3);
	}
	k1[15]  ^= oldtemp;
	// then add k0 << 63
	k1[0] ^= ((k0[15] << 3) & 0xF);
#else
	for (i = 0; i<16; i++)
		k1[i] = k0[i];
#endif

	for (i = 0; i<16; i++)
		k1_M[i] = k1[i];

    MixColumns(k1_M,ROTATION_A_MID,ROTATION_B_MID,ROTATION_C_MID);	
}
