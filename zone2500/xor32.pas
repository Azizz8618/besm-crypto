шифр 419999 зс5^
ОЗУ 32^
АЦПУ 140^
ТРА 37^
ТЕЛЕ^

*name Xor32
*call yesmemory
*full list
*system
*libra: 13
*pascal

program Xor32Mod(output);(*=e+*)

%
%
%
type
  UInt32 = Integer;

Function Xor32(x, y: UInt32): UInt32;
var res, val, cur: Integer;
begin
  res := 0; val := 1;
  while (x <> 0) or (y <> 0) do begin
    cur := ((x mod 2) + (y mod 2)) mod 2;
    res := cur * val + res;
    x := x div 2; y := y div 2; val := val * 2
  end;
  Xor32 := res
end;

begin
end.

*execute
*end file
