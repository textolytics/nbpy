#include </usr/include/python2.7/Python.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <math.h>
#include <stdlib.h>
#include <ncurses.h>


double countquotesday_14_MLP_11_7_1_input_hidden_weights[7][11]=
{
 {4.90333378912911e-001, 1.15107288829619e+000, -1.42818463950155e-002, -5.39512145907880e-002, -2.32448482071111e-001, -6.07257269706870e-002, -5.57961189788901e-003, -3.89955050060996e-002, 2.81920174303006e-001, -1.01651629123087e-001, -2.71670712587232e-001 },
 {1.28419537959152e-001, 1.95692194329255e+000, 6.32424307454134e-002, 1.24094043155973e-002, -1.85674297411882e-001, -1.51170479142101e-001, -1.41755180180790e-001, -1.04955025981840e-001, -2.21866912841900e-002, 3.73927204729470e-002, 1.88354411841137e-001 },
 {-1.25712950546113e-002, 8.52026707040237e-001, 7.00503739459497e-002, -1.17553248816481e-002, -1.32163557560126e-001, -1.14373158250508e-001, -1.85244658023281e-001, -1.86511926345805e-001, -1.21338587104900e-001, -2.06599431093846e-001, 2.31970085299200e-001 },
 {2.64608451475234e-001, -7.69745621245285e-001, -9.11641148329850e-002, 3.29227108103399e-002, 5.83488599944810e-002, -6.40445134015058e-002, -7.09382304997353e-003, 1.73119682108136e-002, -8.86070086935912e-002, -3.35296666653784e-001, -1.88521535399193e-001 },
 {6.57625721146100e-001, 9.46887203641294e-001, 6.59295935251111e-002, -2.36225284696817e-002, -1.94295729836423e-001, -2.46186716219434e-001, -5.32293991725835e-002, -1.25210374985107e-001, -1.10926512017122e-001, -1.97773953235689e-001, 5.53550792659053e-001 },
 {-2.82478105910492e-001, 7.66428196302984e-001, -1.09265906553989e-001, -2.45835121781333e-002, -1.67686142968687e-001, -2.32813603911352e-001, -1.93189587938887e-001, -1.43143478225632e-001, -1.42795575081290e-001, -1.13839890217588e-001, 3.33036350780556e-001 },
 {3.59340100036710e-001, 6.36291484701162e-001, 1.67774753533637e-002, 3.82335533074045e-002, 5.01732471058320e-002, -4.16346394288216e-002, 1.08119478294250e-001, 9.02633804462718e-002, -1.10038114462802e-001, -2.14252340381888e-002, -2.85852293564292e-001 } 
};

double countquotesday_14_MLP_11_7_1_hidden_bias[7]={ -4.24162458312237e-001, -3.23185444492419e-001, -5.91101747966612e-001, -6.03757071115733e-001, -3.08491837209794e-001, -6.30872057495154e-001, -7.78576032012216e-002 };

double countquotesday_14_MLP_11_7_1_hidden_output_wts[1][7]=
{
 {1.72872635923170e-001, -1.23081131349966e-001, 1.02274794684560e+000, -5.13000999022882e-001, -2.47475618244082e-001, 4.45213177129799e-001, 4.90355881958806e-001 }
};

double countquotesday_14_MLP_11_7_1_output_bias[1]={ -7.36118559823822e-001 };

double countquotesday_14_MLP_11_7_1_max_input[4]={ 2.01612231800000e+009, 1.14043000000000e+000, 3.40000000000000e+001, 4.20000000000000e+001 };

double countquotesday_14_MLP_11_7_1_min_input[4]={ 2.01505191500000e+009, 1.03557000000000e+000, 0.00000000000000e+000, 0.00000000000000e+000 };

double countquotesday_14_MLP_11_7_1_max_target[1]={ 1.14173000000000e+000 };

double countquotesday_14_MLP_11_7_1_min_target[1]={ 1.03558000000000e+000 };

double countquotesday_14_MLP_11_7_1_input[11];
double countquotesday_14_MLP_11_7_1_hidden[7];
double countquotesday_14_MLP_11_7_1_output[1];

double countquotesday_14_MLP_11_7_1_MeanInputs[4]={ 2.01533691178091e+009, 1.09671389211618e+000, 2.76680497925311e+000, 2.48713692946058e+000 };

void countquotesday_14_MLP_11_7_1_ScaleInputs(double* input, double minimum, double maximum, int nCategoricalInputs, int nContInputs, int steps)
{
 double delta;
 long i,j,n;
 for(j=0,n=0; j<steps; j++, n+=nCategoricalInputs)
 {
   for(i=0; i<nContInputs; i++)
   {
	 delta = (maximum-minimum)/(countquotesday_14_MLP_11_7_1_max_input[i]-countquotesday_14_MLP_11_7_1_min_input[i]);
	 input[n] = minimum - delta*countquotesday_14_MLP_11_7_1_min_input[i]+ delta*input[n];
    n++;
   }
 }
}

void countquotesday_14_MLP_11_7_1_UnscaleTargets(double* output, double minimum, double maximum, int size)
{
  double delta;
  long i;
  for(i=0; i<size; i++)
  {
    delta = (maximum-minimum)/(countquotesday_14_MLP_11_7_1_max_target[i]-countquotesday_14_MLP_11_7_1_min_target[i]);
    output[i] = (output[i] - minimum + delta*countquotesday_14_MLP_11_7_1_min_target[i])/delta;
   }
}

void countquotesday_14_MLP_11_7_1_ComputeFeedForwardSignals(double* MAT_INOUT,double* V_IN,double* V_OUT, double* V_BIAS,int size1,int size2,int layer)
{
  int row,col;
  for(row=0;row < size2; row++) 
    {
      V_OUT[row]=0.0;
      for(col=0;col<size1;col++)V_OUT[row]+=(*(MAT_INOUT+(row*size1)+col)*V_IN[col]);
      V_OUT[row]+=V_BIAS[row];
      if(layer==0) V_OUT[row] = exp(V_OUT[row]);
   }
}

void countquotesday_14_MLP_11_7_1_RunNeuralNet_TS_Reg () 
{
  countquotesday_14_MLP_11_7_1_ComputeFeedForwardSignals((double*)countquotesday_14_MLP_11_7_1_input_hidden_weights,countquotesday_14_MLP_11_7_1_input,countquotesday_14_MLP_11_7_1_hidden,countquotesday_14_MLP_11_7_1_hidden_bias,11, 7,0);
  countquotesday_14_MLP_11_7_1_ComputeFeedForwardSignals((double*)countquotesday_14_MLP_11_7_1_hidden_output_wts,countquotesday_14_MLP_11_7_1_hidden,countquotesday_14_MLP_11_7_1_output,countquotesday_14_MLP_11_7_1_output_bias,7, 1,1);
}

int main()
{
  float dummy;
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
     printf("%s","\n");
     scanf("%lg",&countquotesday_14_MLP_11_7_1_input[inputindex++]);
     printf("%s","\n");
     scanf("%lg",&countquotesday_14_MLP_11_7_1_input[inputindex++]);
     printf("%s","\n");
     scanf("%lg",&countquotesday_14_MLP_11_7_1_input[inputindex++]);
     printf("%s","\n");
     scanf("%lg",&countquotesday_14_MLP_11_7_1_input[inputindex++]);
	 inputindex-=4;
     //Substitution of missing continuous variables
//	 for(cont_inps_idx=0;cont_inps_idx<4;cont_inps_idx++)
//	 {
//      if(countquotesday_14_MLP_11_7_1_input[inputindex] == -9999)
//	   countquotesday_14_MLP_11_7_1_input[inputindex]=countquotesday_14_MLP_11_7_1_MeanInputs[cont_inps_idx];
//	  inputindex++;
//	 }
	 //printf("%s","Enter a value for Categorical inputs ");
	 //printf("\n%s\n","Categorical Input Name: weekday");
     //printf("\n%s\n","Categories    NumericValues:");
	// printf("%s\n","1           1");
	// printf("%s\n","2           2");
	// printf("%s\n","3           3");
	 //printf("%s\n","4           4");
	 //printf("%s\n","5           5");
	 //printf("%s\n","6           6");
	 //printf("%s\n","7           7");
l1: printf("%s","\n");
    scanf("%f",&dummy);
    if(dummy!=1 && dummy!=2 && dummy!=3 && dummy!=4 && dummy!=5 && dummy!=6 && dummy!=7)goto l1;
	 if(dummy==1)countquotesday_14_MLP_11_7_1_input[inputindex++]=1;
	 else countquotesday_14_MLP_11_7_1_input[inputindex++]=0;
	 if(dummy==2)countquotesday_14_MLP_11_7_1_input[inputindex++]=1;
	 else countquotesday_14_MLP_11_7_1_input[inputindex++]=0;
	 if(dummy==3)countquotesday_14_MLP_11_7_1_input[inputindex++]=1;
	 else countquotesday_14_MLP_11_7_1_input[inputindex++]=0;
	 if(dummy==4)countquotesday_14_MLP_11_7_1_input[inputindex++]=1;
	 else countquotesday_14_MLP_11_7_1_input[inputindex++]=0;
	 if(dummy==5)countquotesday_14_MLP_11_7_1_input[inputindex++]=1;
	 else countquotesday_14_MLP_11_7_1_input[inputindex++]=0;
	 if(dummy==6)countquotesday_14_MLP_11_7_1_input[inputindex++]=1;
	 else countquotesday_14_MLP_11_7_1_input[inputindex++]=0;
	 if(dummy==7)countquotesday_14_MLP_11_7_1_input[inputindex++]=1;
	 else countquotesday_14_MLP_11_7_1_input[inputindex++]=0;
    }
    countquotesday_14_MLP_11_7_1_ScaleInputs(countquotesday_14_MLP_11_7_1_input,0,1,7,4,1);
	countquotesday_14_MLP_11_7_1_RunNeuralNet_TS_Reg();
	countquotesday_14_MLP_11_7_1_UnscaleTargets(countquotesday_14_MLP_11_7_1_output,0,1,1);
	printf("%s%.14e",countquotesday_14_MLP_11_7_1_output[0],"\n");
	//printf("\n\n%s\n","Press any key to make another prediction or enter 0 to quit the program.");
	//keyin=getch();
	//if(keyin==48)break;
      
    return countquotesday_14_MLP_11_7_1_output[0];
   }
//	return 0;
  return countquotesday_14_MLP_11_7_1_output[0];
}

