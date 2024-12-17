//Analysis Type - Regression 
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <ncurses.h>


double cadjpy_usdcad_usdjpy_2_MLP_2_3_1_input_hidden_weights[3][2]=
{
 {-2.06909102107277e+000, -1.62725322277318e+000 },
 {-3.18376091461105e+000, -2.52706622151465e+000 },
 {2.30443502810060e+000, 1.04883834346862e+001 } 
};

double cadjpy_usdcad_usdjpy_2_MLP_2_3_1_hidden_bias[3]={ 1.10534425350041e-001, 5.35043837409098e+000, -4.21061668555058e+000 };

double cadjpy_usdcad_usdjpy_2_MLP_2_3_1_hidden_output_wts[1][3]=
{
 {-1.54533459142975e+001, -1.14710941232035e+001, 6.09863479749750e-002 }
};

double cadjpy_usdcad_usdjpy_2_MLP_2_3_1_output_bias[1]={ -3.65142299476921e+000 };

double cadjpy_usdcad_usdjpy_2_MLP_2_3_1_max_input[2]={ 8.83410000000000e+001, 1.33464000000000e+000 };

double cadjpy_usdcad_usdjpy_2_MLP_2_3_1_min_input[2]={ 8.78190000000000e+001, 1.32807000000000e+000 };

double cadjpy_usdcad_usdjpy_2_MLP_2_3_1_max_target[1]={ 1.17632000000000e+002 };

double cadjpy_usdcad_usdjpy_2_MLP_2_3_1_min_target[1]={ 1.17052000000000e+002 };

double cadjpy_usdcad_usdjpy_2_MLP_2_3_1_input[2];
double cadjpy_usdcad_usdjpy_2_MLP_2_3_1_hidden[3];
double cadjpy_usdcad_usdjpy_2_MLP_2_3_1_output[1];

double cadjpy_usdcad_usdjpy_2_MLP_2_3_1_MeanInputs[2]={ 8.81147477572558e+001, 1.33135357783641e+000 };

void cadjpy_usdcad_usdjpy_2_MLP_2_3_1_ScaleInputs(double* input, double minimum, double maximum, int size)
{
 double delta;
 long i;
 for(i=0; i<size; i++)
 {
	delta = (maximum-minimum)/(cadjpy_usdcad_usdjpy_2_MLP_2_3_1_max_input[i]-cadjpy_usdcad_usdjpy_2_MLP_2_3_1_min_input[i]);
	input[i] = minimum - delta*cadjpy_usdcad_usdjpy_2_MLP_2_3_1_min_input[i]+ delta*input[i];
 }
}

void cadjpy_usdcad_usdjpy_2_MLP_2_3_1_UnscaleTargets(double* output, double minimum, double maximum, int size)
{
  double delta;
  long i;
  for(i=0; i<size; i++)
  {
    delta = (maximum-minimum)/(cadjpy_usdcad_usdjpy_2_MLP_2_3_1_max_target[i]-cadjpy_usdcad_usdjpy_2_MLP_2_3_1_min_target[i]);
    output[i] = (output[i] - minimum + delta*cadjpy_usdcad_usdjpy_2_MLP_2_3_1_min_target[i])/delta;
   }
}

double cadjpy_usdcad_usdjpy_2_MLP_2_3_1_logistic(double x)
{
  if(x > 100.0) x = 1.0;
  else if (x < -100.0) x = 0.0;
  else x = 1.0/(1.0+exp(-x));
  return x;
}

void cadjpy_usdcad_usdjpy_2_MLP_2_3_1_ComputeFeedForwardSignals(double* MAT_INOUT,double* V_IN,double* V_OUT, double* V_BIAS,int size1,int size2,int layer)
{
  int row,col;
  for(row=0;row < size2; row++) 
    {
      V_OUT[row]=0.0;
      for(col=0;col<size1;col++)V_OUT[row]+=(*(MAT_INOUT+(row*size1)+col)*V_IN[col]);
      V_OUT[row]+=V_BIAS[row];
      if(layer==0) V_OUT[row] = tanh(V_OUT[row]);
      if(layer==1) V_OUT[row] = cadjpy_usdcad_usdjpy_2_MLP_2_3_1_logistic(V_OUT[row]);
   }
}

void cadjpy_usdcad_usdjpy_2_MLP_2_3_1_RunNeuralNet_Regression () 
{
  cadjpy_usdcad_usdjpy_2_MLP_2_3_1_ComputeFeedForwardSignals((double*)cadjpy_usdcad_usdjpy_2_MLP_2_3_1_input_hidden_weights,cadjpy_usdcad_usdjpy_2_MLP_2_3_1_input,cadjpy_usdcad_usdjpy_2_MLP_2_3_1_hidden,cadjpy_usdcad_usdjpy_2_MLP_2_3_1_hidden_bias,2, 3,0);
  cadjpy_usdcad_usdjpy_2_MLP_2_3_1_ComputeFeedForwardSignals((double*)cadjpy_usdcad_usdjpy_2_MLP_2_3_1_hidden_output_wts,cadjpy_usdcad_usdjpy_2_MLP_2_3_1_hidden,cadjpy_usdcad_usdjpy_2_MLP_2_3_1_output,cadjpy_usdcad_usdjpy_2_MLP_2_3_1_output_bias,3, 1,1);
}

int main()
{
  int cont_inps;
  int i=0;
  int keyin=1;
  while(1)
  {
	//printf("\n%s\n","Enter values for Continuous inputs (To skip a continuous input please enter -9999)");
	printf("%s","CAD_JPY\n");
	scanf("%lg",&cadjpy_usdcad_usdjpy_2_MLP_2_3_1_input[0]);
	printf("%s","USD_CAD\n");
	scanf("%lg",&cadjpy_usdcad_usdjpy_2_MLP_2_3_1_input[1]);
	for(cont_inps=0;cont_inps<2;cont_inps++)
	{
     //Substitution of missing continuous variables
     if(cadjpy_usdcad_usdjpy_2_MLP_2_3_1_input[cont_inps] == -9999)
	  cadjpy_usdcad_usdjpy_2_MLP_2_3_1_input[cont_inps]=cadjpy_usdcad_usdjpy_2_MLP_2_3_1_MeanInputs[cont_inps];
	}
    cadjpy_usdcad_usdjpy_2_MLP_2_3_1_ScaleInputs(cadjpy_usdcad_usdjpy_2_MLP_2_3_1_input,0,1,2);
	cadjpy_usdcad_usdjpy_2_MLP_2_3_1_RunNeuralNet_Regression();
	cadjpy_usdcad_usdjpy_2_MLP_2_3_1_UnscaleTargets(cadjpy_usdcad_usdjpy_2_MLP_2_3_1_output,0,1,1);
	printf("\n%s%f%d",cadjpy_usdcad_usdjpy_2_MLP_2_3_1_output[0],"\n");
	//printf("\n\n%s\n","Press any key to make another prediction or enter 0 to quit the program.");
	//keyin=getch();
	//if(keyin==48)break;
     return 0;
  }
  //return cadjpy_usdcad_usdjpy_2_MLP_2_3_1_output[0];	
}

