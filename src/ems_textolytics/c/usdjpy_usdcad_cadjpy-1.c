//Analysis Type - Regression 
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <ncurses.h>


double usdjpy_usdcad_cadjpy_1_MLP_2_9_1_input_hidden_weights[9][2]=
{
 {1.08701894213458e+001, -5.66619562566100e+000 },
 {7.47919617162655e+000, -8.98859932218749e+000 },
 {2.56434392948678e+000, -1.00569875626603e+001 },
 {7.44855389394726e+000, -3.98167165885176e+000 },
 {1.42542162198577e+000, -1.42758791149479e+000 },
 {-8.15152564609771e-002, -6.03729785108864e+000 },
 {1.04286170199234e+001, -1.14440832433020e+001 },
 {2.37335972255811e+000, -3.91807967551403e+000 },
 {4.35751231217575e+000, -2.09381198268184e+000 } 
};

double usdjpy_usdcad_cadjpy_1_MLP_2_9_1_hidden_bias[9]={ -3.22410826253989e+000, -4.11698963771399e+000, 1.34821762127009e+000, -2.38980072986635e+000, -1.03409781762193e+000, -4.00961015220644e+000, -6.75190116780186e+000, -5.70948161194517e+000, -3.33410006228814e+000 };

double usdjpy_usdcad_cadjpy_1_MLP_2_9_1_hidden_output_wts[1][9]=
{
 {5.73475176663873e-001, -3.63274019497698e-001, 6.98598087103165e-002, -1.24498277348563e+000, 5.24764698429857e+000, -9.57432550301416e+000, 6.48194322151298e+000, 6.99042194542770e-001, 1.21778185047850e+000 }
};

double usdjpy_usdcad_cadjpy_1_MLP_2_9_1_output_bias[1]={ -6.04705650474997e-001 };

double usdjpy_usdcad_cadjpy_1_MLP_2_9_1_max_input[2]={ 1.17632000000000e+002, 1.33464000000000e+000 };

double usdjpy_usdcad_cadjpy_1_MLP_2_9_1_min_input[2]={ 1.17046000000000e+002, 1.32807000000000e+000 };

double usdjpy_usdcad_cadjpy_1_MLP_2_9_1_max_target[1]={ 8.83410000000000e+001 };

double usdjpy_usdcad_cadjpy_1_MLP_2_9_1_min_target[1]={ 8.78210000000000e+001 };

double usdjpy_usdcad_cadjpy_1_MLP_2_9_1_input[2];
double usdjpy_usdcad_cadjpy_1_MLP_2_9_1_hidden[9];
double usdjpy_usdcad_cadjpy_1_MLP_2_9_1_output[1];

double usdjpy_usdcad_cadjpy_1_MLP_2_9_1_MeanInputs[2]={ 1.17328085668958e+002, 1.33135097831835e+000 };

void usdjpy_usdcad_cadjpy_1_MLP_2_9_1_ScaleInputs(double* input, double minimum, double maximum, int nCategoricalInputs, int nContInputs, int steps)
{
 double delta;
 long i,j,n;
 for(j=0,n=0; j<steps; j++, n+=nCategoricalInputs)
 {
   for(i=0; i<nContInputs; i++)
   {
	 delta = (maximum-minimum)/(usdjpy_usdcad_cadjpy_1_MLP_2_9_1_max_input[i]-usdjpy_usdcad_cadjpy_1_MLP_2_9_1_min_input[i]);
	 input[n] = minimum - delta*usdjpy_usdcad_cadjpy_1_MLP_2_9_1_min_input[i]+ delta*input[n];
    n++;
   }
 }
}

void usdjpy_usdcad_cadjpy_1_MLP_2_9_1_UnscaleTargets(double* output, double minimum, double maximum, int size)
{
  double delta;
  long i;
  for(i=0; i<size; i++)
  {
    delta = (maximum-minimum)/(usdjpy_usdcad_cadjpy_1_MLP_2_9_1_max_target[i]-usdjpy_usdcad_cadjpy_1_MLP_2_9_1_min_target[i]);
    output[i] = (output[i] - minimum + delta*usdjpy_usdcad_cadjpy_1_MLP_2_9_1_min_target[i])/delta;
   }
}

double usdjpy_usdcad_cadjpy_1_MLP_2_9_1_logistic(double x)
{
  if(x > 100.0) x = 1.0;
  else if (x < -100.0) x = 0.0;
  else x = 1.0/(1.0+exp(-x));
  return x;
}

void usdjpy_usdcad_cadjpy_1_MLP_2_9_1_ComputeFeedForwardSignals(double* MAT_INOUT,double* V_IN,double* V_OUT, double* V_BIAS,int size1,int size2,int layer)
{
  int row,col;
  for(row=0;row < size2; row++) 
    {
      V_OUT[row]=0.0;
      for(col=0;col<size1;col++)V_OUT[row]+=(*(MAT_INOUT+(row*size1)+col)*V_IN[col]);
      V_OUT[row]+=V_BIAS[row];
      if(layer==0) V_OUT[row] = usdjpy_usdcad_cadjpy_1_MLP_2_9_1_logistic(V_OUT[row]);
      if(layer==1) V_OUT[row] = tanh(V_OUT[row]);
   }
}

void usdjpy_usdcad_cadjpy_1_MLP_2_9_1_RunNeuralNet_TS_Reg () 
{
  usdjpy_usdcad_cadjpy_1_MLP_2_9_1_ComputeFeedForwardSignals((double*)usdjpy_usdcad_cadjpy_1_MLP_2_9_1_input_hidden_weights,usdjpy_usdcad_cadjpy_1_MLP_2_9_1_input,usdjpy_usdcad_cadjpy_1_MLP_2_9_1_hidden,usdjpy_usdcad_cadjpy_1_MLP_2_9_1_hidden_bias,2, 9,0);
  usdjpy_usdcad_cadjpy_1_MLP_2_9_1_ComputeFeedForwardSignals((double*)usdjpy_usdcad_cadjpy_1_MLP_2_9_1_hidden_output_wts,usdjpy_usdcad_cadjpy_1_MLP_2_9_1_hidden,usdjpy_usdcad_cadjpy_1_MLP_2_9_1_output,usdjpy_usdcad_cadjpy_1_MLP_2_9_1_output_bias,9, 1,1);
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
	//printf("\n%s\n","Enter values for Continuous inputs (To skip a continuous input please enter -9999)");
    for(nsteps=0;nsteps<1;nsteps++)
    {
     //printf("\n%s%d\n","Enter Input values for Step ", stepcntr++);
     printf("%s","USD_JPY\n");
     scanf("%lg",&usdjpy_usdcad_cadjpy_1_MLP_2_9_1_input[inputindex++]);
     printf("%s","USD_CAD\n");
     scanf("%lg",&usdjpy_usdcad_cadjpy_1_MLP_2_9_1_input[inputindex++]);
	 inputindex-=2;
     //Substitution of missing continuous variables
	 for(cont_inps_idx=0;cont_inps_idx<2;cont_inps_idx++)
	 {
      if(usdjpy_usdcad_cadjpy_1_MLP_2_9_1_input[inputindex] == -9999)
	   usdjpy_usdcad_cadjpy_1_MLP_2_9_1_input[inputindex]=usdjpy_usdcad_cadjpy_1_MLP_2_9_1_MeanInputs[cont_inps_idx];
	  inputindex++;
	 }
    }
    usdjpy_usdcad_cadjpy_1_MLP_2_9_1_ScaleInputs(usdjpy_usdcad_cadjpy_1_MLP_2_9_1_input,0,1,0,2,1);
	usdjpy_usdcad_cadjpy_1_MLP_2_9_1_RunNeuralNet_TS_Reg();
	usdjpy_usdcad_cadjpy_1_MLP_2_9_1_UnscaleTargets(usdjpy_usdcad_cadjpy_1_MLP_2_9_1_output,0,1,1);
	printf("\n%s%f%d",usdjpy_usdcad_cadjpy_1_MLP_2_9_1_output[0],"\n");
	//printf("\n\n%s\n","Press any key to make another prediction or enter 0 to quit the program.");
	//keyin=getch();
	//if(keyin==48)break;
     return 0;
  }
  //return cadjpy_usdcad_usdjpy_2_MLP_2_3_1_output[0];	
}

