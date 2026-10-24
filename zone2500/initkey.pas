шифр 419999 зс5^
ОЗУ 32^
АЦПУ 140^
ТРА 37^
ТЕЛЕ^

*name InitKey
*call yesmemory
*full list
*system
*libra: 13
*pascal

program InitGostCtx(output);(*=e+*)

%
%
%
type
  UInt32 = Integer;
  W8 = Array[1..8] of UInt32;
  SB8x4 = Array[1..8] of Array[0..15] of Integer;
  CtxPtr = @Integer;

(* Initialize GOST context *)
Procedure InitGostCtx(
  var ctx: CtxPtr;
  key: W8;
  sbox: SB8x4
);
var i, j: Integer;
begin
  (* Set round keys: X0..X7, X0..X7, X0..X7, X7..X0 *)
  for i := 1 to 8 do begin
    ctx@[i] := key[i];
    ctx@[i+8] := key[i];
    ctx@[i+16] := key[i];
    ctx@[33-i] := key[i]
  end;
  (* Set S-boxes *)
  for i := 1 to 8 do
    for j := 0 to 15 do
      ctx@[32+i,j] := sbox[i][j]
end;

begin
end.

*execute
*end file
