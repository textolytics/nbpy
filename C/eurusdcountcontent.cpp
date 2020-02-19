//Analysis Type - TS_Reg 
#include </usr/include/python2.7/Python.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <math.h>
#include <stdlib.h>
#include <ncurses.h>


double eurusdcountcontent_1_MLP_4_5_1_input_hidden_weights[5][4]=
{
 {3.50480777971178e-001, -1.64008140659244e-002, -6.06962418882281e-002, 6.83926498810405e-003 },
 {-2.70965782764244e-001, 4.60999323508846e-002, 9.13628287816105e-003, 2.27294690443939e-002 },
 {-8.27458050215177e-001, -4.52060559614047e-002, 2.71127710370592e-001, 3.66076040681868e-002 },
 {-6.52655187365829e-001, -4.15922367868444e-002, 5.51564407210124e-002, 6.58603404941953e-003 },
 {1.19041598623413e+000, 1.25926915114728e-001, 2.94318371273159e-002, 1.83733750658600e-002 } 
};

double eurusdcountcontent_1_MLP_4_5_1_hidden_bias[5]={ -9.97384533407635e-003, 8.43124511120086e-003, -1.03634048033625e-001, 2.95626780043985e-001, 6.46227322733564e-002 };

double eurusdcountcontent_1_MLP_4_5_1_hidden_output_wts[1][5]=
{
 {4.55303650913617e-001, -8.52587815488869e-001, 6.19134645711629e-001, -1.30735385051356e+000, 2.27950698831099e-001 }
};

double eurusdcountcontent_1_MLP_4_5_1_output_bias[1]={ 4.37910468757323e-001 };

double eurusdcountcontent_1_MLP_4_5_1_max_input[4]={ 1.14177000000000e+000, 2.01612231800000e+009, 4.10000000000000e+001, 4.20000000000000e+001 };

double eurusdcountcontent_1_MLP_4_5_1_min_input[4]={ 1.03557000000000e+000, 2.01505191500000e+009, 0.00000000000000e+000, 0.00000000000000e+000 };

double eurusdcountcontent_1_MLP_4_5_1_max_target[1]={ 1.14173000000000e+000 };

double eurusdcountcontent_1_MLP_4_5_1_min_target[1]={ 1.03558000000000e+000 };

double eurusdcountcontent_1_MLP_4_5_1_input[4];
double eurusdcountcontent_1_MLP_4_5_1_hidden[5];
double eurusdcountcontent_1_MLP_4_5_1_output[1];

double eurusdcountcontent_1_MLP_4_5_1_MeanInputs[4]={ 1.09680325311203e+000, 2.01536535234689e+009, 2.82406639004149e+000, 2.50539419087137e+000 };

void eurusdcountcontent_1_MLP_4_5_1_ScaleInputs(double* input, double minimum, double maximum, int nCategoricalInputs, int nContInputs, int steps)
{
 double delta;
 long i,j,n;
 for(j=0,n=0; j<steps; j++, n+=nCategoricalInputs)
 {
   for(i=0; i<nContInputs; i++)
   {
	 delta = (maximum-minimum)/(eurusdcountcontent_1_MLP_4_5_1_max_input[i]-eurusdcountcontent_1_MLP_4_5_1_min_input[i]);
	 input[n] = minimum - delta*eurusdcountcontent_1_MLP_4_5_1_min_input[i]+ delta*input[n];
    n++;
   }
 }
}

void eurusdcountcontent_1_MLP_4_5_1_UnscaleTargets(double* output, double minimum, double maximum, int size)
{
  double delta;
  long i;
  for(i=0; i<size; i++)
  {
    delta = (maximum-minimum)/(eurusdcountcontent_1_MLP_4_5_1_max_target[i]-eurusdcountcontent_1_MLP_4_5_1_min_target[i]);
    output[i] = (output[i] - minimum + delta*eurusdcountcontent_1_MLP_4_5_1_min_target[i])/delta;
   }
}

void eurusdcountcontent_1_MLP_4_5_1_ComputeFeedForwardSignals(double* MAT_INOUT,double* V_IN,double* V_OUT, double* V_BIAS,int size1,int size2,int layer)
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

void eurusdcountcontent_1_MLP_4_5_1_RunNeuralNet_TS_Reg () 
{
  eurusdcountcontent_1_MLP_4_5_1_ComputeFeedForwardSignals((double*)eurusdcountcontent_1_MLP_4_5_1_input_hidden_weights,eurusdcountcontent_1_MLP_4_5_1_input,eurusdcountcontent_1_MLP_4_5_1_hidden,eurusdcountcontent_1_MLP_4_5_1_hidden_bias,4, 5,0);
  eurusdcountcontent_1_MLP_4_5_1_ComputeFeedForwardSignals((double*)eurusdcountcontent_1_MLP_4_5_1_hidden_output_wts,eurusdcountcontent_1_MLP_4_5_1_hidden,eurusdcountcontent_1_MLP_4_5_1_output,eurusdcountcontent_1_MLP_4_5_1_output_bias,5, 1,1);
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
     printf("%s","Open");
     scanf("%lg",&eurusdcountcontent_1_MLP_4_5_1_input[inputindex++]);
     printf("%s","Hours");
     scanf("%lg",&eurusdcountcontent_1_MLP_4_5_1_input[inputindex++]);
     printf("%s","count_usd");
     scanf("%lg",&eurusdcountcontent_1_MLP_4_5_1_input[inputindex++]);
     printf("%s","count_eur");
     scanf("%lg",&eurusdcountcontent_1_MLP_4_5_1_input[inputindex++]);
	 inputindex-=4;
     //Substitution of missing continuous variables
//	 for(cont_inps_idx=0;cont_inps_idx<4;cont_inps_idx++)
//	 {
//      if(eurusdcountcontent_1_MLP_4_5_1_input[inputindex] == -9999)
//	   eurusdcountcontent_1_MLP_4_5_1_input[inputindex]=eurusdcountcontent_1_MLP_4_5_1_MeanInputs[cont_inps_idx];
//	  inputindex++;
//	 }
    }
    eurusdcountcontent_1_MLP_4_5_1_ScaleInputs(eurusdcountcontent_1_MLP_4_5_1_input,0,1,0,4,1);
    eurusdcountcontent_1_MLP_4_5_1_RunNeuralNet_TS_Reg();
    eurusdcountcontent_1_MLP_4_5_1_UnscaleTargets(eurusdcountcontent_1_MLP_4_5_1_output,0,1,1);
    printf("%s%.14e",eurusdcountcontent_1_MLP_4_5_1_output[0],"\n");
	//printf("\n\n%s\n","Press any key to make another prediction or enter 0 to quit the program.");
	//keyin=getch();
	//if(keyin==48)break;
//	return eurusdcountcontent_1_MLP_4_5_1_output[0];
//  }
// return eurusdcountcontent_1_MLP_4_5_1_output[0];
//}

    return eurusdcountcontent_1_MLP_4_5_1_output[0];
   }
  return eurusdcountcontent_1_MLP_4_5_1_output[0];
}

