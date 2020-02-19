//Analysis Type - TS_Reg 
#include <stdio.h>
#include <ncurses.h>
#include <math.h>
#include <stdlib.h>


double SANN_CPP_Merge_Variables_3_MLP_6_4_1_input_hidden_weights[4][6]=
{
 {-2.20964315423459e+000, -1.28474751944389e-001, -3.47911533151560e-001, -1.03182530993572e+000, -1.01989816713442e+000, -1.00307932289704e+000 },
 {8.70813375741604e-002, -7.79402422680798e-002, 1.25347155930578e-002, -2.69787180469224e-001, -1.69368852065079e-001, -9.23810605150235e-001 },
 {1.70461695224927e-001, 4.61935365756287e-001, 3.54462495126764e-002, 1.91651133965424e+000, 1.98639019198868e+000, 2.08205650368346e+000 },
 {4.90530855819923e-003, -4.42868350789780e-002, 9.30039001374651e-002, 1.38118043039959e+000, 1.37134071979532e+000, 1.25346383367917e+000 } 
};

double SANN_CPP_Merge_Variables_3_MLP_6_4_1_hidden_bias[4]={ -3.39103530332414e+000, 4.49616803986613e-001, -4.62645187901664e-001, -2.60474919732030e-001 };

double SANN_CPP_Merge_Variables_3_MLP_6_4_1_hidden_output_wts[1][4]=
{
 {1.30201786137178e+000, -1.39885694425342e+000, 1.64054827397407e+000, -2.55496085796297e-001 }
};

double SANN_CPP_Merge_Variables_3_MLP_6_4_1_output_bias[1]={ -1.07171657963266e+000 };

double SANN_CPP_Merge_Variables_3_MLP_6_4_1_max_input[6]={ 2.01701182100000e+009, 3.30000000000000e+001, 1.80000000000000e+001, 1.13056000000000e+000, 1.13108000000000e+000, 1.13030000000000e+000 };

double SANN_CPP_Merge_Variables_3_MLP_6_4_1_min_input[6]={ 2.01511300200000e+009, 1.00000000000000e+000, 1.00000000000000e+000, 1.03552000000000e+000, 1.03695000000000e+000, 1.03533000000000e+000 };

double SANN_CPP_Merge_Variables_3_MLP_6_4_1_max_target[1]={ 1.13050000000000e+000 };

double SANN_CPP_Merge_Variables_3_MLP_6_4_1_min_target[1]={ 1.03690000000000e+000 };

double SANN_CPP_Merge_Variables_3_MLP_6_4_1_input[6];
double SANN_CPP_Merge_Variables_3_MLP_6_4_1_hidden[4];
double SANN_CPP_Merge_Variables_3_MLP_6_4_1_output[1];

double SANN_CPP_Merge_Variables_3_MLP_6_4_1_MeanInputs[6]={ 2.01619472639833e+009, 4.68245125348189e+000, 2.82172701949861e+000, 1.07645874651811e+000, 1.07730980501393e+000, 1.07566782729805e+000 };

void SANN_CPP_Merge_Variables_3_MLP_6_4_1_ScaleInputs(double* input, double minimum, double maximum, int nCategoricalInputs, int nContInputs, int steps)
{
 double delta;
 long i,j,n;
 for(j=0,n=0; j<steps; j++, n+=nCategoricalInputs)
 {
   for(i=0; i<nContInputs; i++)
   {
	 delta = (maximum-minimum)/(SANN_CPP_Merge_Variables_3_MLP_6_4_1_max_input[i]-SANN_CPP_Merge_Variables_3_MLP_6_4_1_min_input[i]);
	 input[n] = minimum - delta*SANN_CPP_Merge_Variables_3_MLP_6_4_1_min_input[i]+ delta*input[n];
    n++;
   }
 }
}

void SANN_CPP_Merge_Variables_3_MLP_6_4_1_UnscaleTargets(double* output, double minimum, double maximum, int size)
{
  double delta;
  long i;
  for(i=0; i<size; i++)
  {
    delta = (maximum-minimum)/(SANN_CPP_Merge_Variables_3_MLP_6_4_1_max_target[i]-SANN_CPP_Merge_Variables_3_MLP_6_4_1_min_target[i]);
    output[i] = (output[i] - minimum + delta*SANN_CPP_Merge_Variables_3_MLP_6_4_1_min_target[i])/delta;
   }
}

void SANN_CPP_Merge_Variables_3_MLP_6_4_1_ComputeFeedForwardSignals(double* MAT_INOUT,double* V_IN,double* V_OUT, double* V_BIAS,int size1,int size2,int layer)
{
  int row,col;
  for(row=0;row < size2; row++) 
    {
      V_OUT[row]=0.0;
      for(col=0;col<size1;col++)V_OUT[row]+=(*(MAT_INOUT+(row*size1)+col)*V_IN[col]);
      V_OUT[row]+=V_BIAS[row];
      if(layer==0) V_OUT[row] = tanh(V_OUT[row]);
      if(layer==1) V_OUT[row] = exp(V_OUT[row]);
   }
}

void SANN_CPP_Merge_Variables_3_MLP_6_4_1_RunNeuralNet_TS_Reg () 
{
  SANN_CPP_Merge_Variables_3_MLP_6_4_1_ComputeFeedForwardSignals((double*)SANN_CPP_Merge_Variables_3_MLP_6_4_1_input_hidden_weights,SANN_CPP_Merge_Variables_3_MLP_6_4_1_input,SANN_CPP_Merge_Variables_3_MLP_6_4_1_hidden,SANN_CPP_Merge_Variables_3_MLP_6_4_1_hidden_bias,6, 4,0);
  SANN_CPP_Merge_Variables_3_MLP_6_4_1_ComputeFeedForwardSignals((double*)SANN_CPP_Merge_Variables_3_MLP_6_4_1_hidden_output_wts,SANN_CPP_Merge_Variables_3_MLP_6_4_1_hidden,SANN_CPP_Merge_Variables_3_MLP_6_4_1_output,SANN_CPP_Merge_Variables_3_MLP_6_4_1_output_bias,4, 1,1);
}

int main()
{
  int i=0;
  int keyin=1;
  int stepcntr;
  int inputindex;
  int cont_inps_idx;
  int nsteps;
  while(1)
  {
	stepcntr=1;
	inputindex=0;
	printf("\n%s\n","Enter values for Continuous inputs (To skip a continuous input please enter -9999)");
    for(nsteps=0;nsteps<1;nsteps++)
    {
     printf("\n%s%d\n","Enter Input values for Step ", stepcntr++);
     printf("%s","Cont. Input-0(hours): ");
     scanf("%lg",&SANN_CPP_Merge_Variables_3_MLP_6_4_1_input[inputindex++]);
     printf("%s","Cont. Input-1(count_dollar1): ");
     scanf("%lg",&SANN_CPP_Merge_Variables_3_MLP_6_4_1_input[inputindex++]);
     printf("%s","Cont. Input-2(count_euro1): ");
     scanf("%lg",&SANN_CPP_Merge_Variables_3_MLP_6_4_1_input[inputindex++]);
     printf("%s","Cont. Input-3(open): ");
     scanf("%lg",&SANN_CPP_Merge_Variables_3_MLP_6_4_1_input[inputindex++]);
     printf("%s","Cont. Input-4(high): ");
     scanf("%lg",&SANN_CPP_Merge_Variables_3_MLP_6_4_1_input[inputindex++]);
     printf("%s","Cont. Input-5(low): ");
     scanf("%lg",&SANN_CPP_Merge_Variables_3_MLP_6_4_1_input[inputindex++]);
	 inputindex-=6;
     //Substitution of missing continuous variables
	 for(cont_inps_idx=0;cont_inps_idx<6;cont_inps_idx++)
	 {
      if(SANN_CPP_Merge_Variables_3_MLP_6_4_1_input[inputindex] == -9999)
	   SANN_CPP_Merge_Variables_3_MLP_6_4_1_input[inputindex]=SANN_CPP_Merge_Variables_3_MLP_6_4_1_MeanInputs[cont_inps_idx];
	  inputindex++;
	 }
    }
    SANN_CPP_Merge_Variables_3_MLP_6_4_1_ScaleInputs(SANN_CPP_Merge_Variables_3_MLP_6_4_1_input,0,1,0,6,1);
	SANN_CPP_Merge_Variables_3_MLP_6_4_1_RunNeuralNet_TS_Reg();
	SANN_CPP_Merge_Variables_3_MLP_6_4_1_UnscaleTargets(SANN_CPP_Merge_Variables_3_MLP_6_4_1_output,0,1,1);
	printf("\n%s%.14e","Predicted Output of close = ",SANN_CPP_Merge_Variables_3_MLP_6_4_1_output[0]);
	printf("\n\n%s\n","Press any key to make another prediction or enter 0 to quit the program.");
	keyin=getch();
	if(keyin==48)break;
  }
	return 0;
}


