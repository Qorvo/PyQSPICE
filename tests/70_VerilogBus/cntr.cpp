// Automatically generated C++ file on Sun Dec 31 14:40:30 2023
//
// To build with Digital Mars C++ Compiler:
//
//    dmc -mn -WD cntr.cpp Vcntr*.cpp verilated.lib kernel32.lib
//
// The intended design of the Verilog interface is such that this
// file should not need editing unless you change the symbol.

#include <verilated.h>
#include "Vcntr.h"

extern "C" __declspec(dllexport) void Destroy(Vcntr *instance)
{
   if(instance)
      delete(instance);
}

extern "C" __declspec(dllexport) void cntr(Vcntr **instance, double t, union uData *data)
{
   if(!*instance)
      *instance = new Vcntr;
   (*instance)->c = data[0].b;

   (*instance)->eval();

   data[1].b = (*instance)->o_3_;
   data[2].b = (*instance)->o_2_;
   data[3].b = (*instance)->o_1_;
   data[4].b = (*instance)->o_0_;
}
