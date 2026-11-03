шифр 419999 зс5^
ОЗУ 32^
АЦПУ 140^
ТРА 37^
ТЕЛЕ^

*name Feistel
*call yesmemory
*full list
*system
*libra: 13
*pascal

program FeistelRound(output);(*=e+*)

%
%
%
type
  UInt32 = Integer;
  W2 = Array[1..2] of UInt32;
  CtxPtr = @Integer;

var
  mod32: Integer;
  mod31: Integer;

(* External: Add32 from zone2500 *)
Function Add32(x, y: UInt32): UInt32; external;

(* External: Xor32 from zone2500 *)
Function Xor32(x, y: UInt32): UInt32; external;

(* External: Rot11 from zone2500 *)
Function Rot11(x: UInt32): UInt32; external;

(* External: Sbox8x4 from zone2500 *)
Function Sbox8x4(box: CtxPtr; x: UInt32): UInt32; external;

(* LSX transformation: Add Key, S-box, Rotate *)
Function LSX(ctx: CtxPtr; x: UInt32; r: Integer): UInt32;
var tmp: UInt32;
begin
  tmp := Add32(ctx@[r], x);
  tmp := Sbox8x4(ctx, tmp);
  LSX := Rot11(tmp)
end;

(* One Feistel round *)
Procedure FeistelRound(
  ctx: CtxPtr;
  var txt: W2;
  round: Integer
);
var left, right, tmp: UInt32;
begin
  left := txt[1];
  right := txt[2];
  tmp := LSX(ctx, right, round);
  txt[1] := right;
  txt[2] := Xor32(left, tmp)
end;

begin
  mod32 := 4294967296;
  mod31 := 2147483648
end.

*execute
*end file
