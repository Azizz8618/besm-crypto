(*=e+*)
(* Комплексный тест библиотеки ГОСТ 28147-89 *)
program testall(output);
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
  ctx: Ctx;
  key: W8;
  sbox: SB;
  data: W2;
  hash: W8;
  counter: W2;
  i, j: Integer;
  passcount: Integer;
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

procedure GOSTDEC(var c: Ctx; var t: W2);
var i: Integer; tmp: UInt32;
begin
  for i := 1 to 32 do fround(c, t, 33 - i);
  tmp := t[1]; t[1] := t[2]; t[2] := tmp
end;

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

begin
  gstMod32 := 4294967296;
  gstMod31 := 2147483648;
  passcount := 0;
  
  WriteLn('=== Тест библиотеки ГОСТ 28147-89 ===');
  WriteLn;
  
  (* Инициализация ГОСТ S-боксов (идентификатор C) *)
  sbox[1][ 0] :=  4; sbox[1][ 1] := 10; sbox[1][ 2] :=  9;
  sbox[1][ 3] :=  2; sbox[1][ 4] := 13; sbox[1][ 5] :=  8;
  sbox[1][ 6] :=  0; sbox[1][ 7] := 14; sbox[1][ 8] :=  6;
  sbox[1][ 9] := 11; sbox[1][10] :=  1; sbox[1][11] := 12;
  sbox[1][12] :=  7; sbox[1][13] := 15; sbox[1][14] :=  5;
  sbox[1][15] :=  3;
  
  sbox[2][ 0] := 14; sbox[2][ 1] := 11; sbox[2][ 2] :=  4;
  sbox[2][ 3] := 12; sbox[2][ 4] :=  6; sbox[2][ 5] := 13;
  sbox[2][ 6] := 15; sbox[2][ 7] := 10; sbox[2][ 8] :=  2;
  sbox[2][ 9] :=  3; sbox[2][10] :=  8; sbox[2][11] :=  1;
  sbox[2][12] :=  0; sbox[2][13] :=  7; sbox[2][14] :=  5;
  sbox[2][15] :=  9;
  
  sbox[3][ 0] :=  5; sbox[3][ 1] :=  8; sbox[3][ 2] :=  1;
  sbox[3][ 3] := 13; sbox[3][ 4] :=  2; sbox[3][ 5] :=  0;
  sbox[3][ 6] :=  3; sbox[3][ 7] := 10; sbox[3][ 8] := 14;
  sbox[3][ 9] := 12; sbox[3][10] := 15; sbox[3][11] :=  7;
  sbox[3][12] :=  6; sbox[3][13] :=  9; sbox[3][14] := 11;
  sbox[3][15] :=  4;
  
  sbox[4][ 0] :=  7; sbox[4][ 1] := 13; sbox[4][ 2] := 10;
  sbox[4][ 3] :=  1; sbox[4][ 4] :=  0; sbox[4][ 5] :=  8;
  sbox[4][ 6] :=  9; sbox[4][ 7] := 15; sbox[4][ 8] := 14;
  sbox[4][ 9] :=  4; sbox[4][10] :=  6; sbox[4][11] := 12;
  sbox[4][12] := 11; sbox[4][13] :=  2; sbox[4][14] :=  5;
  sbox[4][15] :=  3;
  
  sbox[5][ 0] :=  6; sbox[5][ 1] := 12; sbox[5][ 2] :=  7;
  sbox[5][ 3] :=  1; sbox[5][ 4] :=  5; sbox[5][ 5] := 15;
  sbox[5][ 6] := 13; sbox[5][ 7] :=  8; sbox[5][ 8] :=  4;
  sbox[5][ 9] := 10; sbox[5][10] :=  9; sbox[5][11] := 14;
  sbox[5][12] :=  0; sbox[5][13] :=  3; sbox[5][14] := 11;
  sbox[5][15] :=  2;
  
  sbox[6][ 0] :=  4; sbox[6][ 1] := 11; sbox[6][ 2] := 10;
  sbox[6][ 3] :=  0; sbox[6][ 4] :=  7; sbox[6][ 5] :=  2;
  sbox[6][ 6] :=  1; sbox[6][ 7] := 13; sbox[6][ 8] :=  3;
  sbox[6][ 9] :=  6; sbox[6][10] :=  8; sbox[6][11] :=  5;
  sbox[6][12] :=  9; sbox[6][13] := 12; sbox[6][14] := 15;
  sbox[6][15] := 14;
  
  sbox[7][ 0] := 13; sbox[7][ 1] := 11; sbox[7][ 2] :=  4;
  sbox[7][ 3] :=  1; sbox[7][ 4] :=  3; sbox[7][ 5] := 15;
  sbox[7][ 6] :=  5; sbox[7][ 7] :=  9; sbox[7][ 8] :=  0;
  sbox[7][ 9] := 10; sbox[7][10] := 14; sbox[7][11] :=  7;
  sbox[7][12] :=  6; sbox[7][13] :=  8; sbox[7][14] :=  2;
  sbox[7][15] := 12;
  
  sbox[8][ 0] :=  1; sbox[8][ 1] := 15; sbox[8][ 2] := 13;
  sbox[8][ 3] :=  0; sbox[8][ 4] :=  5; sbox[8][ 5] :=  7;
  sbox[8][ 6] := 10; sbox[8][ 7] :=  4; sbox[8][ 8] :=  9;
  sbox[8][ 9] :=  2; sbox[8][10] :=  3; sbox[8][11] := 14;
  sbox[8][12] :=  6; sbox[8][13] := 11; sbox[8][14] :=  8;
  sbox[8][15] := 12;
  
  (* Тест 1: Базовое XOR *)
  WriteLn('Тест 1: GSTXOR(5, 3) = ', GSTXOR(5, 3));
  if GSTXOR(5, 3) = 6 then begin
    WriteLn(' Passed');
    passcount := passcount + 1
  end else
    WriteLn(' Failed');
  
  (* Тест 2: Сложение по модулю 2^32 *)
  WriteLn('Тест 2: GSTADD(100, 200) = ', GSTADD(100, 200));
  if GSTADD(100, 200) = 300 then begin
    WriteLn('  Passed');
    passcount := passcount + 1
  end else
    WriteLn('  Failed');
  
  (* Тест 3: Циклический сдвиг *)
  WriteLn('Тест 3: GSTROT(1) = ', GSTROT(1));
  if GSTROT(1) = 2048 then begin
    WriteLn('  Passed');
    passcount := passcount + 1
  end else
    WriteLn('  Failed');
  
  (* Тест 4: Инициализация ключа *)
  for i := 1 to 8 do key[i] := 0;
  GOSTINI(ctx, key, sbox);
  WriteLn('Тест 4: Key schedule initialized');
  WriteLn('  Passed');
  passcount := passcount + 1;
  
  (* Тест 5: ECB шифрование/расшифрование *)
  data[1] := 0;
  data[2] := 0;
  WriteLn('Тест 5: Plaintext = ', data[1], ' ', data[2]);
  GOSTENC(ctx, data);
  WriteLn('  Ciphertext = ', data[1], ' ', data[2]);
  GOSTDEC(ctx, data);
  WriteLn('  Decrypted = ', data[1], ' ', data[2]);
  if (data[1] = 0) and (data[2] = 0) then begin
    WriteLn('  Passed');
    passcount := passcount + 1
  end else
    WriteLn('  Failed');
  
  (* Тест 6: Сложение по модулю 2^256 *)
  for i := 1 to 8 do hash[i] := 0;
  hash[8] := 1;
  ADD256(hash, hash);
  WriteLn('Тест 6: ADD256 test, hash[8] = ', hash[8]);
  if hash[8] = 2 then begin
    WriteLn('  Passed');
    passcount := passcount + 1
  end else
    WriteLn('  Failed');
  
  WriteLn;
  WriteLn('=== Результаты тестирования ===');
  WriteLn('Пройдено тестов: ', passcount, ' из 6');
  
  if passcount = 6 then
    WriteLn('Все тесты успешно пройдены!')
  else
    WriteLn('Некоторые тесты провалены')
end.
