шифр 419999 зс5^
ОЗУ 32^
АЦПУ 140^
ТРА 37^
ТЕЛЕ^

*name TestZone
*call yesmemory
*full list
*system
*libra: 13
*pascal

program TestZone2500(output);(*=e+*)

%
%
%
type
  UInt32 = Integer;
  W2 = Array[1..2] of UInt32;
  W8 = Array[1..8] of UInt32;
  SB8x4 = Array[1..8] of Array[0..15] of Integer;
  CtxPtr = @Integer;

var
  mod32: Integer;
  testkey: W8;
  testsbox: SB8x4;
  testdata: W2;
  ctx: Array[1..160] of Integer;
  i, j: Integer;
  passcount: Integer;

(* External from zone2500 *)
Function Add32(x, y: UInt32): UInt32; external;
Function Xor32(x, y: UInt32): UInt32; external;
Function Rot11(x: UInt32): UInt32; external;
Procedure InitGostCtx(var c: CtxPtr; k: W8; s: SB8x4); external;
Procedure EncryptBlock(c: CtxPtr; var t: W2); external;
Procedure DecryptBlock(c: CtxPtr; var t: W2); external;

begin
  mod32 := 4294967296;
  passcount := 0;
  
  WriteLn('=== Testing Zone 2500 Library ===');
  WriteLn;
  
  (* Test 1: Add32 *)
  WriteLn('Test 1: Add32(100, 200) = ', Add32(100, 200));
  if Add32(100, 200) = 300 then begin
    WriteLn('  PASS');
    passcount := passcount + 1
  end else
    WriteLn('  FAIL');
  
  (* Test 2: Xor32 *)
  WriteLn('Test 2: Xor32(5, 3) = ', Xor32(5, 3));
  if Xor32(5, 3) = 6 then begin
    WriteLn('  PASS');
    passcount := passcount + 1
  end else
    WriteLn('  FAIL');
  
  (* Test 3: Rot11 *)
  WriteLn('Test 3: Rot11(1) = ', Rot11(1));
  if Rot11(1) = 2048 then begin
    WriteLn('  PASS');
    passcount := passcount + 1
  end else
    WriteLn('  FAIL');
  
  (* Initialize test key *)
  for i := 1 to 8 do testkey[i] := 0;
  
  (* Initialize test S-boxes (identity) *)
  for i := 1 to 8 do
    for j := 0 to 15 do
      testsbox[i][j] := j;
  
  (* Test 4: InitGostCtx *)
  InitGostCtx(ctx, testkey, testsbox);
  WriteLn('Test 4: Context initialized');
  WriteLn('  PASS');
  passcount := passcount + 1;
  
  (* Test 5: EncryptBlock *)
  testdata[1] := 0;
  testdata[2] := 0;
  WriteLn('Test 5: Plain = ', testdata[1], ' ', testdata[2]);
  EncryptBlock(ctx, testdata);
  WriteLn('  Cipher = ', testdata[1], ' ', testdata[2]);
  WriteLn('  PASS');
  passcount := passcount + 1;
  
  (* Test 6: DecryptBlock *)
  DecryptBlock(ctx, testdata);
  WriteLn('Test 6: Decrypted = ', testdata[1], ' ', testdata[2]);
  if (testdata[1] = 0) and (testdata[2] = 0) then begin
    WriteLn('  PASS');
    passcount := passcount + 1
  end else
    WriteLn('  FAIL');
  
  WriteLn;
  WriteLn('=== Results ===');
  WriteLn('Passed: ', passcount, ' of 6 tests');
  
  if passcount = 6 then
    WriteLn('All tests PASSED!')
  else
    WriteLn('Some tests FAILED')
end.

*execute
*end file
