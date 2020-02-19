//Analysis Type - TS_Reg 
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <ncurses.h>

double SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_input_hidden_weights[4][6]=
{
 {-5.88246820479585e-001, -4.18111123398225e-001, -3.88216169579922e-001, -2.47628386473346e-001, 2.78959645904987e-001, -1.71780947186855e-001 },
 {-3.29722598620354e-001, -5.20440424238019e-002, 6.89483055648593e-002, 3.62290662653221e-001, -1.12455500152567e-001, -1.77506469832290e-002 },
 {3.33001055369626e-001, 2.99989798871930e-002, 1.85921064689079e-001, 6.13729007271846e-001, 1.42249110498928e+000, 2.06358485529377e-001 },
 {-1.19694598765012e+000, -3.85976382317017e-001, -4.43102275777392e-001, -3.74387220178814e-001, 1.91838579866418e+000, 2.09013444420300e-002 } 
};

double SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_hidden_bias[4]={ 4.60013449052068e-001, 6.60758594530298e-002, -4.01637243533168e-001, 6.92093664125177e-001 };

double SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_hidden_output_wts[1][4]=
{
 {7.55033430722423e-001, 1.41230361542891e+000, 7.24062831879325e-001, -6.18670870475529e-001 }
};

double SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_output_bias[1]={ 2.44623721771470e-001 };

double SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_max_input[6]={ 2.01701180000000e+009, 1.13046000000000e+000, 1.13095000000000e+000, 1.13027000000000e+000, 3.40000000000000e+001, 1.80000000000000e+001 };

double SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_min_input[6]={ 2.01511300200000e+009, 1.03552000000000e+000, 1.03695000000000e+000, 1.03517000000000e+000, 1.00000000000000e+000, 1.00000000000000e+000 };

double SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_max_target[1]={ 1.13039000000000e+000 };

double SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_min_target[1]={ 1.03555000000000e+000 };

double SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_input[6];
double SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_hidden[4];
double SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_output[1];

double SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_MeanInputs[6]={ 2.01616064721839e+009, 1.07736922413793e+000, 1.07823890804598e+000, 1.07658166666667e+000, 4.67241379310345e+000, 2.87643678160920e+000 };

void SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_ScaleInputs(double* input, double minimum, double maximum, int nCategoricalInputs, int nContInputs, int steps)
{
 double delta;
 long i,j,n;
 for(j=0,n=0; j<steps; j++, n+=nCategoricalInputs)
 {
   for(i=0; i<nContInputs; i++)
   {
	 delta = (maximum-minimum)/(SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_max_input[i]-SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_min_input[i]);
	 input[n] = minimum - delta*SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_min_input[i]+ delta*input[n];
    n++;
   }
 }
}

void SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_UnscaleTargets(double* output, double minimum, double maximum, int size)
{
  double delta;
  long i;
  for(i=0; i<size; i++)
  {
    delta = (maximum-minimum)/(SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_max_target[i]-SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_min_target[i]);
    output[i] = (output[i] - minimum + delta*SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_min_target[i])/delta;
   }
}

void SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_ComputeFeedForwardSignals(double* MAT_INOUT,double* V_IN,double* V_OUT, double* V_BIAS,int size1,int size2,int layer)
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

void SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_RunNeuralNet_TS_Reg () 
{
  SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_ComputeFeedForwardSignals((double*)SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_input_hidden_weights,SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_input,SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_hidden,SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_hidden_bias,6, 4,0);
  SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_ComputeFeedForwardSignals((double*)SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_hidden_output_wts,SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_hidden,SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_output,SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_output_bias,4, 1,1);
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
     scanf("%lg",&SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_input[inputindex++]);
     printf("%s","Cont. Input-1(open): ");
     scanf("%lg",&SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_input[inputindex++]);
     printf("%s","Cont. Input-2(high): ");
     scanf("%lg",&SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_input[inputindex++]);
     printf("%s","Cont. Input-3(low): ");
     scanf("%lg",&SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_input[inputindex++]);
     printf("%s","Cont. Input-4(count_dollar): ");
     scanf("%lg",&SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_input[inputindex++]);
     printf("%s","Cont. Input-5(count_euro): ");
     scanf("%lg",&SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_input[inputindex++]);
	 inputindex-=6;
     //Substitution of missing continuous variables
	 for(cont_inps_idx=0;cont_inps_idx<6;cont_inps_idx++)
	 {
      if(SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_input[inputindex] == -9999)
	   SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_input[inputindex]=SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_MeanInputs[cont_inps_idx];
	  inputindex++;
	 }
    }
    SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_ScaleInputs(SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_input,0,1,0,6,1);
	SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_RunNeuralNet_TS_Reg();
	SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_UnscaleTargets(SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_output,0,1,1);
	printf("\n%s%.14e","Predicted Output of close = ",SANN_Time_Series_(Regression)_(beta)_CPP_Merge_Variables_1_MLP_6_4_1_output[0]);
	printf("\n\n%s\n","Press any key to make another prediction or enter 0 to quit the program.");
	keyin=getch();
	if(keyin==48)break;
  }
	return 0;
}


