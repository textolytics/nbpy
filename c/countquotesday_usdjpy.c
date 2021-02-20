#include </usr/include/python2.7/Python.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <math.h>
#include <stdlib.h>
#include <ncurses.h>

double countquotesdayusdjpy_1_MLP_5_11_1_input_hidden_weights[11][5]=
{
 {5.83380936592199e-002, 1.68383126494387e-001, -4.14451544364869e-002, -7.84213120954493e-002, 2.01899115674494e-002 },
 {-6.28845131813149e-002, 5.01288658311071e-001, 9.90825317556843e-002, 4.83813508577999e-003, -1.00066474557988e-002 },
 {-1.26562301481759e-001, -1.88494062810218e-001, 9.59440000341731e-002, 9.52380221795366e-003, -6.38895334434187e-002 },
 {2.51987551248830e-001, 2.15822597526748e-001, 5.25010824435493e-002, -7.33291655735863e-002, -9.88066290729348e-003 },
 {7.14124991637503e-001, 3.86357102338399e-001, 3.18625330839311e-002, -1.67240139658353e-002, -6.06366960960236e-003 },
 {2.17347588931213e-001, 2.18537086470062e-001, -3.77643329037035e-003, 9.54296974271929e-002, 4.51900956000612e-002 },
 {-3.37625989068344e-001, -9.68001927431340e-002, -4.56892981002569e-002, -1.40790615516142e-002, 1.40717070034346e-002 },
 {-6.29806749142385e-001, -4.25442650135747e-001, -1.19893502756705e-001, 3.20551471080608e-002, 3.13569056927966e-002 },
 {-2.46801675741795e-001, -8.12431567614321e-002, -5.06424411121352e-003, 1.15426545218687e-003, -4.72058510421498e-002 },
 {9.16830042091774e-002, 2.82154988573077e-001, 2.77330254587586e-002, -1.05012561962229e-002, -5.53836078631032e-003 },
 {-4.16213764395076e-001, -1.75124858478594e-001, -2.77583772465487e-002, -1.59709330757709e-002, 3.02313847529501e-002 } 
};

double countquotesdayusdjpy_1_MLP_5_11_1_hidden_bias[11]={ -3.43353910164681e-002, 5.08610593987005e-002, 4.61709125831781e-002, -4.70497376316405e-002, -1.07510295567698e-001, -5.28206420736867e-002, 2.16387184938089e-002, 6.54543269914969e-002, 6.95861434066728e-002, -1.70047847794225e-002, 6.26454007399265e-002 };

double countquotesdayusdjpy_1_MLP_5_11_1_hidden_output_wts[1][11]=
{
 {-1.64115929998073e-001, -8.39131048786399e-001, 9.41730568555810e-002, 8.68996058070216e-002, 6.51564734368150e-001, 1.40055728769021e-001, -1.91179036999749e-001, -2.90591394746230e-001, -4.22342511041621e-001, -2.22495210343410e-001, -2.86870747405252e-001 }
};

double countquotesdayusdjpy_1_MLP_5_11_1_output_bias[1]={ 1.79320034194969e-001 };

double countquotesdayusdjpy_1_MLP_5_11_1_max_input[5]={ 1.18376000000000e+002, 2.01612231700000e+009, 3.30000000000000e+001, 2.20000000000000e+001, 6.00000000000000e+000 };

double countquotesdayusdjpy_1_MLP_5_11_1_min_input[5]={ 1.00035000000000e+002, 2.01608190700000e+009, 0.00000000000000e+000, 0.00000000000000e+000, 1.00000000000000e+000 };

double countquotesdayusdjpy_1_MLP_5_11_1_max_target[1]={ 1.18376000000000e+002 };

double countquotesdayusdjpy_1_MLP_5_11_1_min_target[1]={ 1.00048000000000e+002 };

double countquotesdayusdjpy_1_MLP_5_11_1_input[5];
double countquotesdayusdjpy_1_MLP_5_11_1_hidden[11];
double countquotesdayusdjpy_1_MLP_5_11_1_output[1];

double countquotesdayusdjpy_1_MLP_5_11_1_MeanInputs[5]={ 1.05949115264798e+002, 2.01609641566044e+009, 3.70093457943925e+000, 2.34579439252336e+000, 3.10280373831776e+000 };

void countquotesdayusdjpy_1_MLP_5_11_1_ScaleInputs(double* input, double minimum, double maximum, int size)
{
 double delta;
 long i;
 for(i=0; i<size; i++)
 {
	delta = (maximum-minimum)/(countquotesdayusdjpy_1_MLP_5_11_1_max_input[i]-countquotesdayusdjpy_1_MLP_5_11_1_min_input[i]);
	input[i] = minimum - delta*countquotesdayusdjpy_1_MLP_5_11_1_min_input[i]+ delta*input[i];
 }
}

void countquotesdayusdjpy_1_MLP_5_11_1_UnscaleTargets(double* output, double minimum, double maximum, int size)
{
  double delta;
  long i;
  for(i=0; i<size; i++)
  {
    delta = (maximum-minimum)/(countquotesdayusdjpy_1_MLP_5_11_1_max_target[i]-countquotesdayusdjpy_1_MLP_5_11_1_min_target[i]);
    output[i] = (output[i] - minimum + delta*countquotesdayusdjpy_1_MLP_5_11_1_min_target[i])/delta;
   }
}

void countquotesdayusdjpy_1_MLP_5_11_1_ComputeFeedForwardSignals(double* MAT_INOUT,double* V_IN,double* V_OUT, double* V_BIAS,int size1,int size2,int layer)
{
  int row,col;
  for(row=0;row < size2; row++) 
    {
      V_OUT[row]=0.0;
      for(col=0;col<size1;col++)V_OUT[row]+=(*(MAT_INOUT+(row*size1)+col)*V_IN[col]);
      V_OUT[row]+=V_BIAS[row];
      if(layer==1) V_OUT[row] = sin(V_OUT[row]);
   }
}

void countquotesdayusdjpy_1_MLP_5_11_1_RunNeuralNet_Regression () 
{
  countquotesdayusdjpy_1_MLP_5_11_1_ComputeFeedForwardSignals((double*)countquotesdayusdjpy_1_MLP_5_11_1_input_hidden_weights,countquotesdayusdjpy_1_MLP_5_11_1_input,countquotesdayusdjpy_1_MLP_5_11_1_hidden,countquotesdayusdjpy_1_MLP_5_11_1_hidden_bias,5, 11,0);
  countquotesdayusdjpy_1_MLP_5_11_1_ComputeFeedForwardSignals((double*)countquotesdayusdjpy_1_MLP_5_11_1_hidden_output_wts,countquotesdayusdjpy_1_MLP_5_11_1_hidden,countquotesdayusdjpy_1_MLP_5_11_1_output,countquotesdayusdjpy_1_MLP_5_11_1_output_bias,11, 1,1);
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
	scanf("%lg",&countquotesdayusdjpy_1_MLP_5_11_1_input[0]);
	printf("%s","\n");
	scanf("%lg",&countquotesdayusdjpy_1_MLP_5_11_1_input[1]);
	printf("%s","\n");
	scanf("%lg",&countquotesdayusdjpy_1_MLP_5_11_1_input[2]);
	printf("%s","\n");
	scanf("%lg",&countquotesdayusdjpy_1_MLP_5_11_1_input[3]);
	printf("%s","\n");
	scanf("%lg",&countquotesdayusdjpy_1_MLP_5_11_1_input[4]);
	for(cont_inps=0;cont_inps<5;cont_inps++)
	{
     //Substitution of missing continuous variables
     if(countquotesdayusdjpy_1_MLP_5_11_1_input[cont_inps] == -9999)
	  countquotesdayusdjpy_1_MLP_5_11_1_input[cont_inps]=countquotesdayusdjpy_1_MLP_5_11_1_MeanInputs[cont_inps];
	}
    countquotesdayusdjpy_1_MLP_5_11_1_ScaleInputs(countquotesdayusdjpy_1_MLP_5_11_1_input,0,1,5);
	countquotesdayusdjpy_1_MLP_5_11_1_RunNeuralNet_Regression();
	countquotesdayusdjpy_1_MLP_5_11_1_UnscaleTargets(countquotesdayusdjpy_1_MLP_5_11_1_output,0,1,1);
	printf("\n%s%f%d",countquotesdayusdjpy_1_MLP_5_11_1_output[0],"\n");
	//printf("\n\n%s\n","Press any key to make another prediction or enter 0 to quit the program.");
	//keyin=getch();
	//if(keyin==48)break;
     return 0;
  }
	
}
