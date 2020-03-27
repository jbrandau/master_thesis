// This program is free software; you can redistribute it and/or modify it
// under the terms of the GNU General Public License version 2 as published
// by the Free Software Foundation.

#include "common.h"
#include "share.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void report_time(int dt,int nt,int base,unsigned int nrand)
{
  printf("");
}

void check_ciphertext(byte *out,byte *outex,int nbyte)
{
  //if(out[0] != outex[0])
  if(memcmp(out,outex,nbyte)!=0)
  {
    fprintf(stderr,"Error: incorrect ciphertext\n");
    exit(EXIT_FAILURE);
  }
}

int runalgo(void (*algo)(byte *,byte *,byte *),byte *in,byte *out,byte *key,byte *outex,int nbyte,int nt,int base)
{
  int i;
//  clock_t start,end;
  int dt;

//  start=clock();
//  for(i=0;i<nt;i++)
//    algo(in,out,key);
//  end=clock();
//  dt=(int) (end-start);
//  if (base==0) base=dt;
//  report_time(dt,nt,base,0);
//    check_ciphertext(out,outex,nbyte);
  algo(in,out,key);
  return out[0];
}
