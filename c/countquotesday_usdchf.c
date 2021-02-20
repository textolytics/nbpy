#include </usr/include/python2.7/Python.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <math.h>
#include <stdlib.h>
#include <ncurses.h>


double countquotesday_usdchf_5_MLP_5_6_1_input_hidden_weights[6][5]=
{
 {-2.41330981089994e+000, 3.81877889873806e+000, -5.37186035699760e-001, 7.87864757015981e-001, -7.07233725809496e-002 },
 {9.77998484563375e+000, -1.08124646277292e+000, -3.04011866502403e-001, 3.05555303623095e-001, 2.61008685552772e-002 },
 {-1.32597764142759e+001, -1.25736201999596e+001, -2.19352777175044e-002, -1.84193799334280e-001, 1.11631348588678e+000 },
 {4.27131822017048e+000, -4.35631498662408e-001, 1.42905598002115e-001, -2.19621437726248e-002, 2.70906183421537e-001 },
 {-7.57653067605635e+000, 3.25480961901800e+000, 1.06598968673754e+000, -1.44080306961005e-001, -2.86700695757009e-001 },
 {8.71777113731067e-001, -5.37196633539741e+000, 1.11871514774227e-001, -4.88490328662020e-001, 1.32929234025097e+000 } 
};

double countquotesday_usdchf_5_MLP_5_6_1_hidden_bias[6]={ -3.83107043716767e-001, -9.93057847621748e+000, -1.47262347043278e+000, -1.67479344686718e-001, -2.60709434435188e+000, 1.99109542052909e+000 };

double countquotesday_usdchf_5_MLP_5_6_1_hidden_output_wts[1][6]=
{
 {-4.84896101029303e-001, 1.28400046665341e+001, -4.81772858613069e+000, 4.87724659525563e+000, -5.60654899032002e+000, -1.29184959280075e+000 }
};

double countquotesday_usdchf_5_MLP_5_6_1_output_bias[1]={ -3.18214414345792e+000 };

double countquotesday_usdchf_5_MLP_5_6_1_max_input[5]={ 1.03131000000000e+000, 2.01612231800000e+009, 2.70000000000000e+001, 2.20000000000000e+001, 6.00000000000000e+000 };

double countquotesday_usdchf_5_MLP_5_6_1_min_input[5]={ 9.55190000000000e-001, 2.01608190800000e+009, 0.00000000000000e+000, 0.00000000000000e+000, 1.00000000000000e+000 };

double countquotesday_usdchf_5_MLP_5_6_1_max_target[1]={ 1.03104000000000e+000 };

double countquotesday_usdchf_5_MLP_5_6_1_min_target[1]={ 9.55120000000000e-001 };

double countquotesday_usdchf_5_MLP_5_6_1_input[5];
double countquotesday_usdchf_5_MLP_5_6_1_hidden[6];
double countquotesday_usdchf_5_MLP_5_6_1_output[1];

double countquotesday_usdchf_5_MLP_5_6_1_MeanInputs[5]={ 9.88602049689440e-001, 2.01609688781056e+009, 3.70496894409938e+000, 2.33540372670807e+000, 3.13975155279503e+000 };

void countquotesday_usdchf_5_MLP_5_6_1_ScaleInputs(double* input, double minimum, double maximum, int size)
{
 double delta;
 long i;
 for(i=0; i<size; i++)
 {
	delta = (maximum-minimum)/(countquotesday_usdchf_5_MLP_5_6_1_max_input[i]-countquotesday_usdchf_5_MLP_5_6_1_min_input[i]);
	input[i] = minimum - delta*countquotesday_usdchf_5_MLP_5_6_1_min_input[i]+ delta*input[i];
 }
}

void countquotesday_usdchf_5_MLP_5_6_1_UnscaleTargets(double* output, double minimum, double maximum, int size)
{
  double delta;
  long i;
  for(i=0; i<size; i++)
  {
    delta = (maximum-minimum)/(countquotesday_usdchf_5_MLP_5_6_1_max_target[i]-countquotesday_usdchf_5_MLP_5_6_1_min_target[i]);
    output[i] = (output[i] - minimum + delta*countquotesday_usdchf_5_MLP_5_6_1_min_target[i])/delta;
   }
}

double countquotesday_usdchf_5_MLP_5_6_1_logistic(double x)
{
  if(x > 100.0) x = 1.0;
  else if (x < -100.0) x = 0.0;
  else x = 1.0/(1.0+exp(-x));
  return x;
}

void countquotesday_usdchf_5_MLP_5_6_1_ComputeFeedForwardSignals(double* MAT_INOUT,double* V_IN,double* V_OUT, double* V_BIAS,int size1,int size2,int layer)
{
  int row,col;
  for(row=0;row < size2; row++) 
    {
      V_OUT[row]=0.0;
      for(col=0;col<size1;col++)V_OUT[row]+=(*(MAT_INOUT+(row*size1)+col)*V_IN[col]);
      V_OUT[row]+=V_BIAS[row];
      if(layer==0) V_OUT[row] = countquotesday_usdchf_5_MLP_5_6_1_logistic(V_OUT[row]);
      if(layer==1) V_OUT[row] = countquotesday_usdchf_5_MLP_5_6_1_logistic(V_OUT[row]);
   }
}

void countquotesday_usdchf_5_MLP_5_6_1_RunNeuralNet_Regression () 
{
  countquotesday_usdchf_5_MLP_5_6_1_ComputeFeedForwardSignals((double*)countquotesday_usdchf_5_MLP_5_6_1_input_hidden_weights,countquotesday_usdchf_5_MLP_5_6_1_input,countquotesday_usdchf_5_MLP_5_6_1_hidden,countquotesday_usdchf_5_MLP_5_6_1_hidden_bias,5, 6,0);
  countquotesday_usdchf_5_MLP_5_6_1_ComputeFeedForwardSignals((double*)countquotesday_usdchf_5_MLP_5_6_1_hidden_output_wts,countquotesday_usdchf_5_MLP_5_6_1_hidden,countquotesday_usdchf_5_MLP_5_6_1_output,countquotesday_usdchf_5_MLP_5_6_1_output_bias,6, 1,1);
}

int main()
{
  int cont_inps;
  int i=0;
  int keyin=1;
  while(1)
  {
	//printf("\n%s\n","Enter values for Continuous inputs (To skip a continuous input please enter -9999)");
	printf("%s","\n");
	scanf("%lg",&countquotesday_usdchf_5_MLP_5_6_1_input[0]);
	printf("%s","\n");
	scanf("%lg",&countquotesday_usdchf_5_MLP_5_6_1_input[1]);
	printf("%s","\n");
	scanf("%lg",&countquotesday_usdchf_5_MLP_5_6_1_input[2]);
	printf("%s","\n");
	scanf("%lg",&countquotesday_usdchf_5_MLP_5_6_1_input[3]);
	printf("%s","\n");
	scanf("%lg",&countquotesday_usdchf_5_MLP_5_6_1_input[4]);
	for(cont_inps=0;cont_inps<5;cont_inps++)
	{
     //Substitution of missing continuous variables
     if(countquotesday_usdchf_5_MLP_5_6_1_input[cont_inps] == -9999)
	  countquotesday_usdchf_5_MLP_5_6_1_input[cont_inps]=countquotesday_usdchf_5_MLP_5_6_1_MeanInputs[cont_inps];
	}
    countquotesday_usdchf_5_MLP_5_6_1_ScaleInputs(countquotesday_usdchf_5_MLP_5_6_1_input,0,1,5);
	countquotesday_usdchf_5_MLP_5_6_1_RunNeuralNet_Regression();
	countquotesday_usdchf_5_MLP_5_6_1_UnscaleTargets(countquotesday_usdchf_5_MLP_5_6_1_output,0,1,1);
	printf("\n%s%f%d",countquotesday_usdchf_5_MLP_5_6_1_output[0],"\n");
	//printf("\n\n%s\n","Press any key to make another prediction or enter 0 to quit the program.");
	//keyin=getch();
	//if(keyin==48)break;
     return 0;
  }
	
}

