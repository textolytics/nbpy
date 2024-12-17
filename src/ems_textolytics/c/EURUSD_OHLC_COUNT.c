//Analysis Type - TS_Reg 
#include <stdio.h>
#include <ncurses.h>
#include <math.h>
#include <stdlib.h>


double SANN_CPP_Merge_Variables_1_MLP_6_4_1_input_hidden_weights[4][6]=
{
 {3.77626256778892e-001, -1.55385088895632e+000, -1.75643689827005e+000, -1.81176284940475e+000, -4.04023752310921e-001, 1.50538014511425e-001 },
 {-2.56435686695319e-001, -4.40831664149999e+000, -4.51817312162062e+000, -4.58355036659628e+000, -7.38974530981654e-001, -1.08295375018061e-001 },
 {6.34279768479918e-001, -2.73486414397199e+000, -2.68155566394318e+000, -2.73427440835657e+000, -2.81943111722498e-002, -1.78495771971287e-001 },
 {-3.10738271325240e-002, -3.03827550570365e+000, -3.02936041995839e+000, -2.97142904482975e+000, -8.68171833949755e-002, -2.70075998646513e-001 } 
};

double SANN_CPP_Merge_Variables_1_MLP_6_4_1_hidden_bias[4]={ 2.73443747586307e+000, 1.43057702293546e+000, -2.60764652030138e-001, -1.67210244460939e+000 };

double SANN_CPP_Merge_Variables_1_MLP_6_4_1_hidden_output_wts[1][4]=
{
 {-1.50223994885692e+000, -2.88476218892684e+000, 2.06031983947922e-001, 1.41876875534021e+000 }
};

double SANN_CPP_Merge_Variables_1_MLP_6_4_1_output_bias[1]={ 1.19971077425759e-001 };

double SANN_CPP_Merge_Variables_1_MLP_6_4_1_max_input[6]={ 2.01701182100000e+009, 1.13056000000000e+000, 1.13108000000000e+000, 1.13030000000000e+000, 3.30000000000000e+001, 1.80000000000000e+001 };

double SANN_CPP_Merge_Variables_1_MLP_6_4_1_min_input[6]={ 2.01511300200000e+009, 1.03552000000000e+000, 1.03695000000000e+000, 1.03533000000000e+000, 1.00000000000000e+000, 1.00000000000000e+000 };

double SANN_CPP_Merge_Variables_1_MLP_6_4_1_max_target[1]={ 1.13050000000000e+000 };

double SANN_CPP_Merge_Variables_1_MLP_6_4_1_min_target[1]={ 1.03690000000000e+000 };

double SANN_CPP_Merge_Variables_1_MLP_6_4_1_input[6];
double SANN_CPP_Merge_Variables_1_MLP_6_4_1_hidden[4];
double SANN_CPP_Merge_Variables_1_MLP_6_4_1_output[1];

double SANN_CPP_Merge_Variables_1_MLP_6_4_1_MeanInputs[6]={ 2.01619472639833e+009, 1.07645874651811e+000, 1.07730980501393e+000, 1.07566782729805e+000, 4.68523676880223e+000, 2.82729805013928e+000 };

void SANN_CPP_Merge_Variables_1_MLP_6_4_1_ScaleInputs(double* input, double minimum, double maximum, int nCategoricalInputs, int nContInputs, int steps)
{
 double delta;
 long i,j,n;
 for(j=0,n=0; j<steps; j++, n+=nCategoricalInputs)
 {
   for(i=0; i<nContInputs; i++)
   {
	 delta = (maximum-minimum)/(SANN_CPP_Merge_Variables_1_MLP_6_4_1_max_input[i]-SANN_CPP_Merge_Variables_1_MLP_6_4_1_min_input[i]);
	 input[n] = minimum - delta*SANN_CPP_Merge_Variables_1_MLP_6_4_1_min_input[i]+ delta*input[n];
    n++;
   }
 }
}

void SANN_CPP_Merge_Variables_1_MLP_6_4_1_UnscaleTargets(double* output, double minimum, double maximum, int size)
{
  double delta;
  long i;
  for(i=0; i<size; i++)
  {
    delta = (maximum-minimum)/(SANN_CPP_Merge_Variables_1_MLP_6_4_1_max_target[i]-SANN_CPP_Merge_Variables_1_MLP_6_4_1_min_target[i]);
    output[i] = (output[i] - minimum + delta*SANN_CPP_Merge_Variables_1_MLP_6_4_1_min_target[i])/delta;
   }
}

double SANN_CPP_Merge_Variables_1_MLP_6_4_1_logistic(double x)
{
  if(x > 100.0) x = 1.0;
  else if (x < -100.0) x = 0.0;
  else x = 1.0/(1.0+exp(-x));
  return x;
}

void SANN_CPP_Merge_Variables_1_MLP_6_4_1_ComputeFeedForwardSignals(double* MAT_INOUT,double* V_IN,double* V_OUT, double* V_BIAS,int size1,int size2,int layer)
{
  int row,col;
  for(row=0;row < size2; row++) 
    {
      V_OUT[row]=0.0;
      for(col=0;col<size1;col++)V_OUT[row]+=(*(MAT_INOUT+(row*size1)+col)*V_IN[col]);
      V_OUT[row]+=V_BIAS[row];
      if(layer==0) V_OUT[row] = SANN_CPP_Merge_Variables_1_MLP_6_4_1_logistic(V_OUT[row]);
      if(layer==1) V_OUT[row] = exp(V_OUT[row]);
   }
}

void SANN_CPP_Merge_Variables_1_MLP_6_4_1_RunNeuralNet_TS_Reg () 
{
  SANN_CPP_Merge_Variables_1_MLP_6_4_1_ComputeFeedForwardSignals((double*)SANN_CPP_Merge_Variables_1_MLP_6_4_1_input_hidden_weights,SANN_CPP_Merge_Variables_1_MLP_6_4_1_input,SANN_CPP_Merge_Variables_1_MLP_6_4_1_hidden,SANN_CPP_Merge_Variables_1_MLP_6_4_1_hidden_bias,6, 4,0);
  SANN_CPP_Merge_Variables_1_MLP_6_4_1_ComputeFeedForwardSignals((double*)SANN_CPP_Merge_Variables_1_MLP_6_4_1_hidden_output_wts,SANN_CPP_Merge_Variables_1_MLP_6_4_1_hidden,SANN_CPP_Merge_Variables_1_MLP_6_4_1_output,SANN_CPP_Merge_Variables_1_MLP_6_4_1_output_bias,4, 1,1);
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
     scanf("%lg",&SANN_CPP_Merge_Variables_1_MLP_6_4_1_input[inputindex++]);
     printf("%s","Cont. Input-1(open): ");
     scanf("%lg",&SANN_CPP_Merge_Variables_1_MLP_6_4_1_input[inputindex++]);
     printf("%s","Cont. Input-2(high): ");
     scanf("%lg",&SANN_CPP_Merge_Variables_1_MLP_6_4_1_input[inputindex++]);
     printf("%s","Cont. Input-3(low): ");
     scanf("%lg",&SANN_CPP_Merge_Variables_1_MLP_6_4_1_input[inputindex++]);
     printf("%s","Cont. Input-4(count_dollar): ");
     scanf("%lg",&SANN_CPP_Merge_Variables_1_MLP_6_4_1_input[inputindex++]);
     printf("%s","Cont. Input-5(count_euro): ");
     scanf("%lg",&SANN_CPP_Merge_Variables_1_MLP_6_4_1_input[inputindex++]);
	 inputindex-=6;
     //Substitution of missing continuous variables
	 for(cont_inps_idx=0;cont_inps_idx<6;cont_inps_idx++)
	 {
      if(SANN_CPP_Merge_Variables_1_MLP_6_4_1_input[inputindex] == -9999)
	   SANN_CPP_Merge_Variables_1_MLP_6_4_1_input[inputindex]=SANN_CPP_Merge_Variables_1_MLP_6_4_1_MeanInputs[cont_inps_idx];
	  inputindex++;
	 }
    }
    SANN_CPP_Merge_Variables_1_MLP_6_4_1_ScaleInputs(SANN_CPP_Merge_Variables_1_MLP_6_4_1_input,0,1,0,6,1);
	SANN_CPP_Merge_Variables_1_MLP_6_4_1_RunNeuralNet_TS_Reg();
	SANN_CPP_Merge_Variables_1_MLP_6_4_1_UnscaleTargets(SANN_CPP_Merge_Variables_1_MLP_6_4_1_output,0,1,1);
	printf("\n%s%.14e","Predicted Output of close = ",SANN_CPP_Merge_Variables_1_MLP_6_4_1_output[0]);
	printf("\n\n%s\n","Press any key to make another prediction or enter 0 to quit the program.");
	keyin=getch();
	if(keyin==48)break;
  }
	return 0;
}


