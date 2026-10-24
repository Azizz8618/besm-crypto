шифр 419999 зс5^
ОЗУ 32^
АЦПУ 140^
ТРА 37^
ТЕЛЕ^

*name Pascal
*call yesmemory
*full list
*system
*libra: 13
*pascal

program GostLibrary(input,output);(*=e+*)

%
%
%
Label 1,2,3,4,5,6,7,8,9;
%
%
%
(* GOST 28147-89 cryptographic library for BESM-6 *)
(* All lines <= 72 chars (dialect restriction) *)
(* Entry points differ in first 6 significant chars *)

type
  UInt32 = Integer;
  W2 = Array[1..2] of UInt32;
  W8 = Array[1..8] of UInt32;
  SB = Array[1..8] of Array[0..15] of Integer;
  Ctx = record
    rk: Array[1..32] of Integer;
    box: SB
  end;

var
  gstMod32: Integer;
  gstMod31: Integer;

%
%
%
(* 32-bit addition modulo 2^32 *)
Function GSTADD(x, y: UInt32): UInt32;
begin
  GSTADD := (x + y) mod gstMod32
end;

%
%
%
(* bitwise exclusive OR *)
Function GSTXOR(x, y: UInt32): UInt32;
var res, val, cur: Integer;
begin
  res := 0; val := 1;
  while (x <> 0) or (y <> 0) do begin
    cur := ((x mod 2) + (y mod 2)) mod 2;
    res := cur * val + res;
    x := x div 2; y := y div 2; val := val * 2
  end;
  GSTXOR := res
end;

%
%
%
(* cyclic rotation left by 11 bits *)
Function GSTROT(x: UInt32): UInt32;
var i, firstbit: Integer; res: UInt32;
begin
  res := x;
  for i := 1 to 11 do begin
    firstbit := res div gstMod31;
    res := (res * 2) mod gstMod32;
    res := GSTXOR(res, firstbit)
  end;
  GSTROT := res
end;

%
%
%
(* Initialize GOST context with key and S-boxes *)
Procedure GOSTINI(
  var c: Ctx;
  k: W8;
  b: SB
);
var i, j: Integer;
begin
  for i := 1 to 8 do begin
    c.rk[i] := k[i];
    c.rk[i+8] := k[i];
    c.rk[i+16] := k[i];
    c.rk[33-i] := k[i]
  end;
  for i := 1 to 8 do
    for j := 0 to 15 do
      c.box[i][j] := b[i][j]
end;

%
%
%
(* Set encryption key *)
Procedure GOSTSET(var c: Ctx; k: W8);
var i: Integer;
begin
  for i := 1 to 8 do begin
    c.rk[i] := k[i];
    c.rk[i+8] := k[i];
    c.rk[i+16] := k[i];
    c.rk[33-i] := k[i]
  end
end;

%
%
%
(* nonlinear layer: 8 S-boxes, 4 bits each *)
Function NLAYER(c: Ctx; x: UInt32): UInt32;
var i, res, val, cur: Integer;
begin
  res := 0; val := 1;
  for i := 1 to 8 do begin
    cur := x mod 16;
    cur := c.box[i][cur];
    res := res + cur * val;
    val := val * 16;
    x := x div 16
  end;
  NLAYER := res
end;

%
%
%
(* one Feistel round *)
Procedure FROUND(c: Ctx; var t: W2; i: Integer);
var l, r, tmp: UInt32;
begin
  l := t[1]; r := t[2];
  tmp := GSTADD(c.rk[i], r);
  tmp := NLAYER(c, tmp);
  tmp := GSTROT(tmp);
  t[1] := r;
  t[2] := GSTXOR(l, tmp)
end;

%
%
%
(* Encrypt 64-bit block in place *)
Procedure GOSTENC(var c: Ctx; var t: W2);
var i: Integer; tmp: UInt32;
begin
  for i := 1 to 32 do FROUND(c, t, i);
  tmp := t[1]; t[1] := t[2]; t[2] := tmp
end;

%
%
%
(* Decrypt 64-bit block in place *)
Procedure GOSTDEC(var c: Ctx; var t: W2);
var i: Integer; tmp: UInt32;
begin
  for i := 1 to 32 do FROUND(c, t, 33 - i);
  tmp := t[1]; t[1] := t[2]; t[2] := tmp
end;

%
%
%
(* Addition modulo 2^256 *)
Procedure GSTA256(var ss: W8; xs: W8);
var i, j, carry, curr: Integer;
begin
  carry := 0;
  for i := 1 to 8 do begin
    j := 8 - i + 1;
    curr := ss[j] + xs[j] + carry;
    ss[j] := curr mod gstMod32;
    carry := curr div gstMod32
  end
end;

%
%
%
(* Bit reversal of 32-bit word *)
Function GSTRVS(x: UInt32): UInt32;
var i: Integer; curr: UInt32;
begin
  curr := 0;
  for i := 1 to 32 do begin
    curr := curr * 2;
    curr := curr + (x mod 2);
    x := x div 2
  end;
  GSTRVS := curr
end;

%
%
%
(* Swap two 32-bit words *)
Procedure GSTSWP(var a, b: UInt32);
var t: UInt32;
begin
  t := a; a := b; b := t
end;

%
%
%
begin
  gstMod32 := 4294967296;
  gstMod31 := 2147483648
end.

*execute
*end file
