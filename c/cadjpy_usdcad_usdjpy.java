/**Java deployment code of Neural Networks Model**/

/**==========================================================================
Before running the Java deployment code please read the following.

 STATISTICA variable names will be exported as-is into the Java deployment script;
please verify the resulting script to ensure that the variable names follow the Java
naming conventions and modify the names if necessary.

==========================================================================**/

import java.io.*;
import java.util.*;





public class Predict

{

   public static void CAD_JPyUSD_CADUSD_JPYEUR_MLP_2_3_1( double[] ContInputs )

   {

     //"Input Variable" comment is added besides Input(Response) variables.



     int Cont_idx=0;

     double CAD_JPY = ContInputs[Cont_idx++]; //Input Variable

     double USD_CAD = ContInputs[Cont_idx++]; //Input Variable

    double[] __statist_max_input = new double[2];

    __statist_max_input[0]= 8.83410000000000e+001;

    __statist_max_input[1]= 1.33464000000000e+000;



    double[] __statist_min_input = new double[2];

    __statist_min_input[0]= 8.78190000000000e+001;

    __statist_min_input[1]= 1.32807000000000e+000;



    double[] __statist_max_target = new double[1];

    __statist_max_target[0]= 1.17632000000000e+002;



    double[] __statist_min_target = new double[1];

    __statist_min_target[0]= 1.17052000000000e+002;





    double[][] __statist_i_h_wts = new double[3][2];



    __statist_i_h_wts[0][0]=-2.06909102107277e+000;

    __statist_i_h_wts[0][1]=-1.62725322277318e+000;



    __statist_i_h_wts[1][0]=-3.18376091461105e+000;

    __statist_i_h_wts[1][1]=-2.52706622151465e+000;



    __statist_i_h_wts[2][0]=2.30443502810060e+000;

    __statist_i_h_wts[2][1]=1.04883834346862e+001;



    double[][] __statist_h_o_wts = new double[1][3];



    __statist_h_o_wts[0][0]=-1.54533459142975e+001;

    __statist_h_o_wts[0][1]=-1.14710941232035e+001;

    __statist_h_o_wts[0][2]=6.09863479749750e-002;



    double[] __statist_hidden_bias = new double[3];

    __statist_hidden_bias[0]=1.10534425350041e-001;

    __statist_hidden_bias[1]=5.35043837409098e+000;

    __statist_hidden_bias[2]=-4.21061668555058e+000;



    double[] __statist_output_bias = new double[1];

    __statist_output_bias[0]=-3.65142299476921e+000;



    double[] __statist_inputs = new double[2];



    double[] __statist_hidden = new double[3];



    double[] __statist_outputs = new double[1];

    __statist_outputs[0] = -1.0e+307;



    __statist_inputs[0]=CAD_JPY;

    __statist_inputs[1]=USD_CAD;



    double __statist_delta=0;

    double __statist_maximum=1;

    double __statist_minimum=0;

    int __statist_ncont_inputs=2;



    /*scale continuous inputs*/

    for(int __statist_i=0;__statist_i < __statist_ncont_inputs;__statist_i++)

    {

     __statist_delta = (__statist_maximum-__statist_minimum)/(__statist_max_input[__statist_i]-__statist_min_input[__statist_i]);

     __statist_inputs[__statist_i] = __statist_minimum - __statist_delta*__statist_min_input[__statist_i]+ __statist_delta*__statist_inputs[__statist_i];

    }



    int __statist_ninputs=2;

    int __statist_nhidden=3;



    /*Compute feed forward signals from Input layer to hidden layer*/

    for(int __statist_row=0;__statist_row < __statist_nhidden;__statist_row++)

    {

      __statist_hidden[__statist_row]=0.0;

      for(int __statist_col=0;__statist_col < __statist_ninputs;__statist_col++)

      {

       __statist_hidden[__statist_row]= __statist_hidden[__statist_row] + (__statist_i_h_wts[__statist_row][__statist_col]*__statist_inputs[__statist_col]);

      }

     __statist_hidden[__statist_row]=__statist_hidden[__statist_row]+__statist_hidden_bias[__statist_row];

    }



    for(int __statist_row=0;__statist_row < __statist_nhidden;__statist_row++)

    {

      if(__statist_hidden[__statist_row]>100.0)

      {

       __statist_hidden[__statist_row] = 1.0;

      }

      else

      {

       if(__statist_hidden[__statist_row]<-100.0)

       {

        __statist_hidden[__statist_row] = -1.0;

       }

       else

       {

        __statist_hidden[__statist_row] = Math.tanh(__statist_hidden[__statist_row]);

       }

      }

    }



    int __statist_noutputs=1;



    /*Compute feed forward signals from hidden layer to output layer*/

    for(int __statist_row2=0;__statist_row2 < __statist_noutputs;__statist_row2++)

    {

     __statist_outputs[__statist_row2]=0.0;

    for(int __statist_col2=0;__statist_col2 < __statist_nhidden;__statist_col2++)

      {

       __statist_outputs[__statist_row2]= __statist_outputs[__statist_row2] + (__statist_h_o_wts[__statist_row2][__statist_col2]*__statist_hidden[__statist_col2]);

      }

     __statist_outputs[__statist_row2]=__statist_outputs[__statist_row2]+__statist_output_bias[__statist_row2];

    }



    for(int __statist_row=0;__statist_row < __statist_noutputs;__statist_row++)

    {

     if(__statist_outputs[__statist_row]>100.0)

     {

      __statist_outputs[__statist_row] = 1.0;

     }

     else

     {

      if(__statist_outputs[__statist_row]<-100.0)

      {

&gt;

                 __statist_outputs[__statist_row] = 0.0;

      }

      else

      {

&gt;

                 __statist_outputs[__statist_row] = 1.0/(1.0+Math.exp(-__statist_outputs[__statist_row]));

      }

&gt;

               }

    }







    /*Unscale continuous targets*/

    __statist_delta=0;

    for(int __statist_i=0;__statist_i < __statist_noutputs;__statist_i++)

    {

     __statist_delta = (__statist_maximum-__statist_minimum)/(__statist_max_target[__statist_i]-__statist_min_target[__statist_i]);

     __statist_outputs[__statist_i] = (__statist_outputs[__statist_i] - __statist_minimum + __statist_delta*__statist_min_target[__statist_i])/__statist_delta;

    }





      for(int __statist_ii=0; __statist_ii < __statist_noutputs; __statist_ii++)

      {

        System.out.println(" Prediction_"+ __statist_ii + " = " + __statist_outputs[__statist_ii]);

      }





   }



   public static void main (String[] args) {

     int argID = 0;

     double[] ContInputs = new double[2];

     int contID = 0;



     if (args.length >= NaN)

     {

       ContInputs[contID++] =  Double.parseDouble(args[argID++]);

       ContInputs[contID++] =  Double.parseDouble(args[argID++]);

     }

     else

     {

       String Comment = "";

       String Comment1 = "**************************************************************************\n";

       Comment += Comment1;

       String Comment2 = "Please enter at least NaN command line parameters in the following order for \nthe program to Predict.\n";

       Comment += Comment2;

       Comment += Comment1;

       String Comment3 = "CAD_JPY  Type - double (or) integer\n";

       Comment += Comment3;

       String Comment4 = "USD_CAD  Type - double (or) integer\n";

       Comment += Comment4;

       Comment += Comment1;

       System.out.println(Comment);

       System.exit(1);

     }

     CAD_JPyUSD_CADUSD_JPYEUR_MLP_2_3_1( ContInputs );

   }



}

