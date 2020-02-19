//Analysis Type - Regression 
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <ncurses.h>


double cadjpy_usdcad_usdjpy_1_MLP_2_7_1_input_hidden_weights[7][2]=
{
 {2.10395118898584e+000, -1.82748467179558e+001 },
 {3.82547288784428e+000, -7.55085573717115e+000 },
 {-3.29737867177981e+000, -1.00708731935011e+001 },
 {3.24354390812611e+000, -1.03747893829617e+001 },
 {-1.57503804953772e+000, -8.63761127869375e+000 },
 {1.24429761524643e+001, -3.65706681804107e+001 },
 {6.48791316084654e-001, -1.89727437935126e+000 } 
};

double cadjpy_usdcad_usdjpy_1_MLP_2_7_1_hidden_bias[7]={ -7.86749616885103e+000, -1.05795349964204e+000, -7.19787250468776e+000, -2.67332755847839e+000, -1.23363843038192e+001, -7.71099894150198e+000, -9.27731273164324e-001 };

double cadjpy_usdcad_usdjpy_1_MLP_2_7_1_hidden_output_wts[1][7]=
{
 {-6.54312646223654e-001, -4.06215752851568e-001, 9.87804971702417e+000, -5.79020006270368e+000, 1.26671049667836e+001, -1.43456770338381e+001, -6.58885759839564e+000 }
};

double cadjpy_usdcad_usdjpy_1_MLP_2_7_1_output_bias[1]={ 6.02191037724633e-001 };

double cadjpy_usdcad_usdjpy_1_MLP_2_7_1_max_input[2]={ 1.32671000000000e+000, 1.16356000000000e+002 };

double cadjpy_usdcad_usdjpy_1_MLP_2_7_1_min_input[2]={ 1.32389000000000e+000, 1.15657000000000e+002 };

double cadjpy_usdcad_usdjpy_1_MLP_2_7_1_max_target[1]={ 8.77230000000000e+001 };

double cadjpy_usdcad_usdjpy_1_MLP_2_7_1_min_target[1]={ 8.72660000000000e+001 };

double cadjpy_usdcad_usdjpy_1_MLP_2_7_1_input[2];
double cadjpy_usdcad_usdjpy_1_MLP_2_7_1_hidden[7];
double cadjpy_usdcad_usdjpy_1_MLP_2_7_1_output[1];

double cadjpy_usdcad_usdjpy_1_MLP_2_7_1_MeanInputs[2]={ 1.32558344463972e+000, 1.15998025776216e+002 };

void cadjpy_usdcad_usdjpy_1_MLP_2_7_1_ScaleInputs(double* input, double minimum, double maximum, int size)
{
 double delta;
 long i;
 for(i=0; i<size; i++)
 {
	delta = (maximum-minimum)/(cadjpy_usdcad_usdjpy_1_MLP_2_7_1_max_input[i]-cadjpy_usdcad_usdjpy_1_MLP_2_7_1_min_input[i]);
	input[i] = minimum - delta*cadjpy_usdcad_usdjpy_1_MLP_2_7_1_min_input[i]+ delta*input[i];
 }
}

void cadjpy_usdcad_usdjpy_1_MLP_2_7_1_UnscaleTargets(double* output, double minimum, double maximum, int size)
{
  double delta;
  long i;
  for(i=0; i<size; i++)
  {
    delta = (maximum-minimum)/(cadjpy_usdcad_usdjpy_1_MLP_2_7_1_max_target[i]-cadjpy_usdcad_usdjpy_1_MLP_2_7_1_min_target[i]);
    output[i] = (output[i] - minimum + delta*cadjpy_usdcad_usdjpy_1_MLP_2_7_1_min_target[i])/delta;
   }
}

double cadjpy_usdcad_usdjpy_1_MLP_2_7_1_logistic(double x)
{
  if(x > 100.0) x = 1.0;
  else if (x < -100.0) x = 0.0;
  else x = 1.0/(1.0+exp(-x));
  return x;
}

void cadjpy_usdcad_usdjpy_1_MLP_2_7_1_ComputeFeedForwardSignals(double* MAT_INOUT,double* V_IN,double* V_OUT, double* V_BIAS,int size1,int size2,int layer)
{
  int row,col;
  for(row=0;row < size2; row++) 
    {
      V_OUT[row]=0.0;
      for(col=0;col<size1;col++)V_OUT[row]+=(*(MAT_INOUT+(row*size1)+col)*V_IN[col]);
      V_OUT[row]+=V_BIAS[row];
      if(layer==0) V_OUT[row] = cadjpy_usdcad_usdjpy_1_MLP_2_7_1_logistic(V_OUT[row]);
      if(layer==1) V_OUT[row] = exp(V_OUT[row]);
   }
}

void cadjpy_usdcad_usdjpy_1_MLP_2_7_1_RunNeuralNet_Regression () 
{
  cadjpy_usdcad_usdjpy_1_MLP_2_7_1_ComputeFeedForwardSignals((double*)cadjpy_usdcad_usdjpy_1_MLP_2_7_1_input_hidden_weights,cadjpy_usdcad_usdjpy_1_MLP_2_7_1_input,cadjpy_usdcad_usdjpy_1_MLP_2_7_1_hidden,cadjpy_usdcad_usdjpy_1_MLP_2_7_1_hidden_bias,2, 7,0);
  cadjpy_usdcad_usdjpy_1_MLP_2_7_1_ComputeFeedForwardSignals((double*)cadjpy_usdcad_usdjpy_1_MLP_2_7_1_hidden_output_wts,cadjpy_usdcad_usdjpy_1_MLP_2_7_1_hidden,cadjpy_usdcad_usdjpy_1_MLP_2_7_1_output,cadjpy_usdcad_usdjpy_1_MLP_2_7_1_output_bias,7, 1,1);
}

int main()
{
  int cont_inps;
  int i=0;
  int keyin=1;
  while(1)
  {
	//printf("\n%s\n","Enter values for Continuous inputs (To skip a continuous input please enter -9999)");
	printf("%s","USD_CAD\n");
	scanf("%lg",&cadjpy_usdcad_usdjpy_1_MLP_2_7_1_input[0]);
	printf("%s","USD_JPY\n");
	scanf("%lg",&cadjpy_usdcad_usdjpy_1_MLP_2_7_1_input[1]);
	for(cont_inps=0;cont_inps<2;cont_inps++)
	{
     //Substitution of missing continuous variables
     if(cadjpy_usdcad_usdjpy_1_MLP_2_7_1_input[cont_inps] == -9999)
	  cadjpy_usdcad_usdjpy_1_MLP_2_7_1_input[cont_inps]=cadjpy_usdcad_usdjpy_1_MLP_2_7_1_MeanInputs[cont_inps];
	}
    cadjpy_usdcad_usdjpy_1_MLP_2_7_1_ScaleInputs(cadjpy_usdcad_usdjpy_1_MLP_2_7_1_input,0,1,2);
	cadjpy_usdcad_usdjpy_1_MLP_2_7_1_RunNeuralNet_Regression();
	cadjpy_usdcad_usdjpy_1_MLP_2_7_1_UnscaleTargets(cadjpy_usdcad_usdjpy_1_MLP_2_7_1_output,0,1,1);
	printf("\n%s%f%d",cadjpy_usdcad_usdjpy_1_MLP_2_7_1_output[0],"\n");
	//printf("\n\n%s\n","Press any key to make another prediction or enter 0 to quit the program.");
	//keyin=getch();
	//if(keyin==48)break;
     return 0;
  }
  //return cadjpy_usdcad_usdjpy_2_MLP_2_3_1_output[0];	
}

