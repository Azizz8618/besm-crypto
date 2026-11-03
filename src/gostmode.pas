(*=e+*)
(* Режимы шифрования ГОСТ 28147-89: CTR, hash и др.
   Все строки короче 72 позиций (ограничение диалекта). *)
program gostmode(output);
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

function GSTADD(x, y: UInt32): UInt32;
begin
  GSTADD := (x + y) mod gstMod32
end;

function GSTXOR(x, y: UInt32): UInt32;
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

function GSTROT(x: UInt32): UInt32;
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

procedure GOSTINI(var c: Ctx; k: W8; b: SB);
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

function nlin(c: Ctx; x: UInt32): UInt32;
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
  nlin := res
end;

procedure fround(c: Ctx; var t: W2; i: Integer);
var l, r, tmp: UInt32;
begin
  l := t[1]; r := t[2];
  tmp := GSTADD(c.rk[i], r);
  tmp := nlin(c, tmp);
  tmp := GSTROT(tmp);
  t[1] := r;
  t[2] := GSTXOR(l, tmp)
end;

procedure GOSTENC(var c: Ctx; var t: W2);
var i: Integer; tmp: UInt32;
begin
  for i := 1 to 32 do fround(c, t, i);
  tmp := t[1]; t[1] := t[2]; t[2] := tmp
end;

(* Сложение по модулю 2^256 *)
procedure ADD256(var ss: W8; xs: W8);
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

(* Линейное преобразование для хеша *)
procedure LINSTP(var hs: W8; ss: W8; ms: W8);
var i: Integer;
begin
  for i := 1 to 8 do
    hs[i] := GSTXOR(GSTXOR(hs[i], ss[i]), ms[i])
end;

(* Шаг хеш-функции ГОСТ Р 34.11-94 *)
procedure HSHSTP(var hs: W8; ms: W8; c: Ctx);
var ss: W8; i: Integer; t: W2;
begin
  for i := 1 to 8 do ss[i] := ms[i];
  for i := 1 to 8 do begin
    t[1] := hs[i];
    t[2] := ss[i];
    GOSTENC(c, t);
    hs[i] := GSTXOR(t[1], t[2])
  end;
  ADD256(hs, ss);
  LINSTP(hs, ss, ms)
end;

(* Режим CTR: зашифрование *)
procedure ENCCTR(c: Ctx; var txt: W2; cnt: W2; num: Integer);
var i: Integer; gamma: W2; tmp: UInt32;
begin
  gamma[1] := cnt[1]; gamma[2] := cnt[2];
  for i := 1 to num do begin
    GOSTENC(c, gamma);
    txt[1] := GSTXOR(txt[1], gamma[1]);
    txt[2] := GSTXOR(txt[2], gamma[2]);
    tmp := gamma[2];
    gamma[2] := GSTADD(gamma[2], 1);
    if gamma[2] < tmp then gamma[1] := GSTADD(gamma[1], 1)
  end
end;

(* Режим CTR: расшифрование (то же самое) *)
procedure DECCTR(c: Ctx; var txt: W2; cnt: W2; num: Integer);
begin
  ENCCTR(c, txt, cnt, num)
end;

begin
  gstMod32 := 4294967296;
  gstMod31 := 2147483648
end.
