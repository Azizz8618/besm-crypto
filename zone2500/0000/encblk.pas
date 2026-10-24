шифр 419999 зс5^
ОЗУ 32^
АЦПУ 140^
ТРА 37^
ТЕЛЕ^

*name EncBlk
*call yesmemory
*full list
*system
*libra: 13
*pascal

program EncryptBlock(output);(*=e+*)

%
%
%
type
  UInt32 = Integer;
  W2 = Array[1..2] of UInt32;
  CtxPtr = @Integer;

var
  mod32: Integer;

(* External: Xor32 from zone2500 *)
Function Xor32(x, y: UInt32): UInt32; external;

(* External: FeistelRound from zone2500 *)
Procedure FeistelRound(ctx: CtxPtr; var txt: W2; r: Integer); external;

(* Encrypt 64-bit block (ECB mode) *)
Procedure EncryptBlock(
  ctx: CtxPtr;
  var txt: W2
);
var i: Integer; tmp: UInt32;
begin
  for i := 1 to 32 do
    FeistelRound(ctx, txt, i);
  tmp := txt[1];
  txt[1] := txt[2];
  txt[2] := tmp
end;

begin
  mod32 := 4294967296
end.

*execute
*end file
