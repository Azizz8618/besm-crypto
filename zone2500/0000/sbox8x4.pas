шифр 419999 зс5^
ОЗУ 32^
АЦПУ 140^
ТРА 37^
ТЕЛЕ^

*name Sbox8x4
*call yesmemory
*full list
*system
*libra: 13
*pascal

program SboxLayer(output);(*=e+*)

%
%
%
type
  UInt32 = Integer;
  SB8x4 = Array[1..8] of Array[0..15] of Integer;

(* Apply 8 S-boxes, 4 bits each *)
Function Sbox8x4(box: SB8x4; x: UInt32): UInt32;
var i, res, val, cur: Integer;
begin
  res := 0; val := 1;
  for i := 1 to 8 do begin
    cur := x mod 16;
    cur := box[i][cur];
    res := res + cur * val;
    val := val * 16;
    x := x div 16
  end;
  Sbox8x4 := res
end;

begin
end.

*execute
*end file
