#include <stdlib.h>
#include <string.h>
#include <math.h>

extern "C" {
#include "aes.h"
#include "aes_rp.h"
#include "aes_rp_prg.h"
#include "share.h"
#include "aes_share.h"
#include "aes_htable.h"
#include "common.h"
#include "prg.h"
}


#include <stdint.h>

//const byte numChars = 32;
//char receivedChars[numChars];
int LEDpin = 33;
boolean newData = false;

uint8_t ck_trig[4] = {0xDE, 0xAD, 0xBE, 0xEF};
uint8_t send_s[4] = {0x00, 0x00, 0x00, 0x00};

void printMes(char *s, byte *m)
{
  printf("%s=", s);
  int i;
  for (i = 0; i < 16; i++) printf("%02x", m[i]);
  printf("\n");
}

int n;
int nt = 1;
int i;
byte keyex[16] = {0x17, 0x17, 0x17, 0x17, 0x17, 0x17, 0x17, 0x17, 0x17, 0x17, 0x17, 0x17, 0x17, 0x17, 0x17, 0x17};

byte inex[16] = {0x32, 0x43, 0xf6, 0xa8, 0x88, 0x5a, 0x30, 0x8d, 0x31, 0x31, 0x98, 0xa2, 0xe0, 0x37, 0x07, 0x34};
byte outex[16] = {0x3f, 0x20, 0xf8, 0x8, 0xdb, 0xe3, 0xcc, 0xb8, 0xf7, 0xf7, 0x73, 0xd5, 0x68, 0xb7, 0xca, 0x26};

byte in[16], out[16];
byte key[16];
int cr = 0;

// run setup at startup
void setup() {
  Serial.begin(9600);
  int got_deadbeef = 0;
  pinMode(LEDpin, OUTPUT);
  digitalWrite(LEDpin, LOW);

  int counter = 0;
  while (counter < 4)
  {
    while (Serial.available() == 0) {}
    Serial.readBytes(&send_s[counter], 1);
    Serial.write(&send_s[counter], 1);
    if (send_s[counter] == ck_trig[counter])
    {
      counter++;
    }
    else
    {
      counter = 0;
    }
  }
}


void loop() {
  byte plaintext[16];
  int dt, base;
  byte deadBeefCheck[4];
  int rprg;
  Serial.flush();

  while(Serial.available() != 16)
  {
    ;
  }

  for(int i=0;i<16;i++){
    plaintext[i] = Serial.read();
  }
  
  for (i = 0; i < 16; i++) key[i] = keyex[i];
  for (i = 0; i < 16; i++) in[i] = plaintext[i];
  
  //Serial.write("Without countermeasure, plain: ");
  //digitalWrite(LEDpin, HIGH);
  //base = run_aes(&aes, in, out, key, outex, nt, 0);
  //digitalWrite(LEDpin, LOW);
      
  //Serial.write("Without countermeasure, RP: ");
  //digitalWrite(LEDpin, HIGH);
  //base = run_aes(&aes_rp,in,out,key,outex,nt,0);
  //digitalWrite(LEDpin, LOW);

  //Serial.print("  With RP countermeasure: ");
  int n = 3;
  digitalWrite(LEDpin, HIGH);
  base = run_aes_share(in, out, key, outex, n, &subbyte_rp_share, nt, 0);
  digitalWrite(LEDpin, LOW);

  //printf("  With RP countermeasure, with flr: ");
  //rprg=rprg_flr(n);
  //digitalWrite(LEDpin, HIGH);
  //base = run_aes_share_prg(in,out,key,outex,n,&subbyte_rp_share_flr,0,nt,rprg);
  //digitalWrite(LEDpin, LOW);

  //printf("  With RP countermeasure, with ilr: ");
  //rprg=rprg_ilr(n);
  //digitalWrite(LEDpin, HIGH);
  //base = run_aes_share_prg(in,out,key,outex,n,&subbyte_rp_share_ilr,0,nt,rprg);
  //digitalWrite(LEDpin, LOW);

  //printf("  With RP countermeasure, with ilr2: ");
  //rprg=rprg_ilr(n);
  //digitalWrite(LEDpin, HIGH);
  //base = run_aes_share_prg(in,out,key,outex,n,&subbyte_rp_share_ilr2,0,nt,rprg);
  //digitalWrite(LEDpin, LOW);

  //printf("  With RP countermeasure, with flr, multiple prg: ");
  //digitalWrite(LEDpin, HIGH);
  //base = run_aes_share_mprg(in,out,key,outex,n,&subbyte_rp_share_flr_mprg,TFLR,0,nt);
  //digitalWrite(LEDpin, LOW);

  //printf("  With RP countermeasure, with ilr, multiple prg: ");
  //digitalWrite(LEDpin, HIGH);
  //base = run_aes_share_mprg(in,out,key,outex,n,&subbyte_rp_share_ilr_mprg,TILR,0,nt);
  //digitalWrite(LEDpin, LOW);

  //printf(" With RP countermeasure, with flr, mprgmat: ");
  //digitalWrite(LEDpin, HIGH);
  //base = run_aes_share_mprgmat(in,out,key,outex,n,0,nt);
  //digitalWrite(LEDpin, LOW);

  //printf("  With randomized table : ");
  //digitalWrite(LEDpin, HIGH);
  //base = run_aes_share(in,out,key,outex,n,&subbyte_htable,0,nt); 
  //digitalWrite(LEDpin, LOW);

  //printf("  With randomized table inc: ");
  //digitalWrite(LEDpin, HIGH);
  //base = run_aes_share(in,out,key,outex,n,&subbyte_htable_inc,0,nt);
  //digitalWrite(LEDpin, LOW); 

  //printf("  With randomized table word: ");
  //digitalWrite(LEDpin, HIGH);
  //base = run_aes_share(in,out,key,outex,n,&subbyte_htable_word,0,nt);
  //digitalWrite(LEDpin, LOW);

  //printf("  With randomized table word inc: ");
  //digitalWrite(LEDpin, HIGH);
  //base = run_aes_share(in,out,key,outex,n,&subbyte_htable_word_inc,0,nt);
  //digitalWrite(LEDpin, LOW); 

  //printf("  With randomized table common shares: ");
  //digitalWrite(LEDpin, HIGH);
  //base = run_aes_common_share(in,out,key,outex,n,&subbyte_cs_htable,0,nt); 
  //digitalWrite(LEDpin, LOW);
    
  //printf("  With randomized table word common shares: ");
  //digitalWrite(LEDpin, HIGH);
  //base = run_aes_common_share(in,out,key,outex,n,&subbyte_cs_htable_word,0,nt);
  //digitalWrite(LEDpin, LOW); 

  //printf("  With randomized table word inc common shares: ");
  //digitalWrite(LEDpin, HIGH);
  //base = run_aes_common_share(in,out,key,outex,n,&subbyte_cs_htable_word_inc,0,nt);
  //digitalWrite(LEDpin, LOW); 
  
  Serial.write(base);
  Serial.flush();
}
