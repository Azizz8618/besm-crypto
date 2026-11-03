шифр 419999 зс5^
ОЗУ 32^
АЦПУ 140^
ТРА 37^
ТЕЛЕ^

*name Add32
*call yesmemory
*full list
*system
*libra: 13
*pascal

program Add32Mod(output);(*=e+*)

%
%
%
type
  UInt32 = Integer;

var
  mod32: Integer;

Function Add32(x, y: UInt32): UInt32;
begin
  Add32 := (x + y) mod mod32
end;

begin
  mod32 := 4294967296
end.

*execute
*end file
