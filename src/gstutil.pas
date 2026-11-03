(*=e+*)
(* GOST-BESM библиотека: дополнительные 32-битные примитивы.
   Точки входа (имена различаются в первых 6 значащих литерах):
     GSTRVS  - x -> обращение 32 бит
     GSTSWP  - обмен двух 32-битных слов по ссылке
     GSTA256 - (ss,xs) -> ss := (ss+xs) mod 2^256, по 8 слов *)
program gstutil(output);
type
  UInt32 = Integer;
  W8 = Array[1..8] of UInt32;
var
  gstMod32: Integer;

function GSTRVS(x: UInt32): UInt32;
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

procedure GSTSWP(var a, b: UInt32);
var t: UInt32;
begin
  t := a; a := b; b := t
end;

procedure GSTA256(var ss: W8; xs: W8);
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

begin
  gstMod32 := 4294967296
end.
