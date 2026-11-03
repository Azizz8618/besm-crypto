(*=e+*)
(* Ядро ГОСТ 28147-89: контекст, 32-раундовая сеть Фейстеля.
   Все строки короче 72 позиций (ограничение диалекта).
   Точки входа (различны в первых 6 значащих литерах):
     GOSTINI - инициализация контекста ключом и S-боксами (8x16)
     GOSTENC - зашифровать 64-битный блок (2 слова) на месте
     GOSTDEC - расшифровать 64-битный блок на месте
     GOSTSET - установить ключ (та же раскладка, что в GOSTINI)
   Схема ключа: X0..X7,X0..X7,X0..X7,X7..X0 (32 раунда) *)
program gostcore(output);
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
  dummy: Integer;
  gstMod32: Integer;
  gstMod31: Integer;

(* 32-битное сложение по модулю 2^32 *)
function GSTADD(x, y: UInt32): UInt32;
begin
  GSTADD := (x + y) mod gstMod32
end;

(* побитовое исключающее ИЛИ *)
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

(* циклический сдвиг влево на 11 бит *)
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

procedure GOSTSET(var c: Ctx; k: W8);
var i: Integer;
begin
  for i := 1 to 8 do begin
    c.rk[i] := k[i];
    c.rk[i+8] := k[i];
    c.rk[i+16] := k[i];
    c.rk[33-i] := k[i]
  end
end;

(* нелинейный слой: 8 S-боксов по 4 бита *)
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

(* один раунд сети Фейстеля *)
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

procedure GOSTDEC(var c: Ctx; var t: W2);
var i: Integer; tmp: UInt32;
begin
  for i := 1 to 32 do fround(c, t, 33 - i);
  tmp := t[1]; t[1] := t[2]; t[2] := tmp
end;

begin
  gstMod32 := 4294967296;
  gstMod31 := 2147483648;
  dummy := 0
end.
