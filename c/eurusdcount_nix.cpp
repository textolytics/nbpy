#include </usr/include/python2.7/Python.h>
//#include <giostream.h>

#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <math.h>
#include <stdlib.h>
#include <ncurses.h>


double eurusd_5_xx_10_MLP_4_4_3_input_hidden_weights[4][4]=
{
 {-1.74387228848419e-001, 1.58363122202525e+000, -1.68991590405601e-001, -1.80366519609300e-001 },
 {-3.28436874961063e-001, 3.34130154518935e+000, -4.47313925350529e-001, 8.31963300790102e-001 },
 {-9.75592464764508e-003, -1.23092745300263e+000, -9.13025315479538e-003, -3.97576246262869e-002 },
 {1.24084249200849e-003, 2.02824427146866e+000, -1.79505814597813e-002, -8.79530021804219e-002 }
};

double eurusd_5_xx_10_MLP_4_4_3_hidden_bias[4]={ -2.49511463403550e-001, -6.29129596791594e-001, 1.17426660987046e+000, -1.27416825112386e-001 };

double eurusd_5_xx_10_MLP_4_4_3_hidden_output_wts[3][4]=
{
 {1.73814893223150e-001, -6.64719867377515e-002, -6.47829094998344e-001, 2.96707436194524e-001 },
 {3.22274254305461e-001, -1.51324599844809e-001, -5.40993861063116e-001, 3.32465022820288e-001 },
 {1.37133149657171e-001, -7.82911608977750e-002, -6.47944563327952e-001, 3.55904527163052e-001 }
};

double eurusd_5_xx_10_MLP_4_4_3_output_bias[3]={ 5.84161107006781e-001, 5.00815273334323e-001, 5.69949825707867e-001 };

double eurusd_5_xx_10_MLP_4_4_3_max_input[4]={ 5.00000000000000e+000, 1.14022994041443e+000, 4.00000000000000e+000, 2.01608251000000e+009 };

double eurusd_5_xx_10_MLP_4_4_3_min_input[4]={ 0.00000000000000e+000, 1.05631005764008e+000, 0.00000000000000e+000, 2.01505190300000e+009 };

double eurusd_5_xx_10_MLP_4_4_3_max_target[3]={ 1.14014995098114e+000, 1.14199995994568e+000, 1.13880002498627e+000 };

double eurusd_5_xx_10_MLP_4_4_3_min_target[3]={ 1.05690002441406e+000, 1.05701005458832e+000, 1.05613005161285e+000 };

double eurusd_5_xx_10_MLP_4_4_3_input[4];
double eurusd_5_xx_10_MLP_4_4_3_hidden[4];
double eurusd_5_xx_10_MLP_4_4_3_output[3];

double eurusd_5_xx_10_MLP_4_4_3_MeanInputs[4]={ 2.35294117647059e-001, 1.09991227743522e+000, 3.54838709677419e-001, 2.01514823731879e+009 };

void eurusd_5_xx_10_MLP_4_4_3_ScaleInputs(double* input, double minimum, double maximum, int nCategoricalInputs, int nContInputs, int steps)
{
 double delta;
 long i,j,n;
 for(j=0,n=0; j<steps; j++, n+=nCategoricalInputs)
 {
   for(i=0; i<nContInputs; i++)
   {
     delta = (maximum-minimum)/(eurusd_5_xx_10_MLP_4_4_3_max_input[i]-eurusd_5_xx_10_MLP_4_4_3_min_input[i]);
     input[n] = minimum - delta*eurusd_5_xx_10_MLP_4_4_3_min_input[i]+ delta*input[n];
    n++;
   }
 }
}

void eurusd_5_xx_10_MLP_4_4_3_UnscaleTargets(double* output, double minimum, double maximum, int size)
{
  double delta;
  long i;
  for(i=0; i<size; i++)
  {
    delta = (maximum-minimum)/(eurusd_5_xx_10_MLP_4_4_3_max_target[i]-eurusd_5_xx_10_MLP_4_4_3_min_target[i]);
    output[i] = (output[i] - minimum + delta*eurusd_5_xx_10_MLP_4_4_3_min_target[i])/delta;
   }
}

void eurusd_5_xx_10_MLP_4_4_3_ComputeFeedForwardSignals(double* MAT_INOUT,double* V_IN,double* V_OUT, double* V_BIAS,int size1,int size2,int layer)
{
  int row,col;
  for(row=0;row < size2; row++)
    {
      V_OUT[row]=0.0;
      for(col=0;col<size1;col++)V_OUT[row]+=(*(MAT_INOUT+(row*size1)+col)*V_IN[col]);
      V_OUT[row]+=V_BIAS[row];
      if(layer==0) V_OUT[row] = tanh(V_OUT[row]);
   }
}

void eurusd_5_xx_10_MLP_4_4_3_RunNeuralNet_TS_Reg ()
{
  eurusd_5_xx_10_MLP_4_4_3_ComputeFeedForwardSignals((double*)eurusd_5_xx_10_MLP_4_4_3_input_hidden_weights,eurusd_5_xx_10_MLP_4_4_3_input,eurusd_5_xx_10_MLP_4_4_3_hidden,eurusd_5_xx_10_MLP_4_4_3_hidden_bias,4, 4,0);
  eurusd_5_xx_10_MLP_4_4_3_ComputeFeedForwardSignals((double*)eurusd_5_xx_10_MLP_4_4_3_hidden_output_wts,eurusd_5_xx_10_MLP_4_4_3_hidden,eurusd_5_xx_10_MLP_4_4_3_output,eurusd_5_xx_10_MLP_4_4_3_output_bias,4, 3,1);
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
    
    for(nsteps=0;nsteps<1;nsteps++)
    {
     
     printf("%s","How many times the word dollar appeared last hour?[e.g.:2] : \n");
     scanf("%lg",&eurusd_5_xx_10_MLP_4_4_3_input[inputindex++]);
     printf("%s","Enter current EURUSD price[e.g.:1.28765] : \n");
     scanf("%lg",&eurusd_5_xx_10_MLP_4_4_3_input[inputindex++]);
     printf("%s","How many times the word euro appeared last hour?[e.g.:5] : \n");
     scanf("%lg",&eurusd_5_xx_10_MLP_4_4_3_input[inputindex++]);
     printf("%s","What time is it ?[e.g.:2016082503] : \n");
     scanf("%lg",&eurusd_5_xx_10_MLP_4_4_3_input[inputindex++]);
     inputindex-=4;
     //Substitution of missing continuous variables
    // for(cont_inps_idx=0;cont_inps_idx<4;cont_inps_idx++)
    // {
    //  if(eurusd_5_xx_10_MLP_4_4_3_input[inputindex] == -9999)
    //   eurusd_5_xx_10_MLP_4_4_3_input[inputindex]=eurusd_5_xx_10_MLP_4_4_3_MeanInputs[cont_inps_idx];
    //  inputindex++;
     //}
    }
    eurusd_5_xx_10_MLP_4_4_3_ScaleInputs(eurusd_5_xx_10_MLP_4_4_3_input,0,1,0,4,1);
    eurusd_5_xx_10_MLP_4_4_3_RunNeuralNet_TS_Reg();
    eurusd_5_xx_10_MLP_4_4_3_UnscaleTargets(eurusd_5_xx_10_MLP_4_4_3_output,0,1,3);
    printf("%s%.14e",eurusd_5_xx_10_MLP_4_4_3_output[0],"\n");
    //printf("\n\n%s\n","Press any key to make another prediction or enter 0 to quit the program.");
    //keyin=getch();
    //if(keyin==48)break;
    return eurusd_5_xx_10_MLP_4_4_3_output[0];
   }
  return eurusd_5_xx_10_MLP_4_4_3_output[0];
}
