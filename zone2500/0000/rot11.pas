шифр 419999 зс5^
ОЗУ 32^
АЦПУ 140^
ТРА 37^
ТЕЛЕ^

*name Rot11
*call yesmemory
*full list
*system
*libra: 13
*pascal

program Rot11Mod(output);(*=e+*)

%
%
%
type
  UInt32 = Integer;

var
  mod32: Integer;
  mod31: Integer;

Function Rot11(x: UInt32): UInt32;
var i, firstbit: Integer; res: UInt32;
begin
  res := x;
  for i := 1 to 11 do begin
    firstbit := res div mod31;
    res := (res * 2) mod mod32;
    res := Xor(res, firstbit)
  end;
  Rot11 := res
end;

begin
  mod32 := 4294967296;
  mod31 := 2147483648
end.

*execute
*end file
