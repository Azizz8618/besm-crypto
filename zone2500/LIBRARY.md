# Библиотека зоны 2500 (диск 2348)

Набор подпрограмм ГОСТ 28147-89 для вызова как external.

## Структура библиотеки

Базовые операции (арифметика):

- `add32.pas` - Add32: сложение по модулю 2^32
- `xor32.pas` - Xor32: побитовое XOR
- `rot11.pas` - Rot11: циклический сдвиг на 11 бит

Трансформации:

- `sbox8x4.pas` - Sbox8x4: 8 S-боксов по 4 бита
- `feistel.pas` - FeistelRound: один раунд Фейстеля

Шифрование:

- `encblk.pas` - EncryptBlock: полное шифрование блока (ECB)
- `decblk.pas` - DecryptBlock: расшифрование блока (ECB)

Управление:

- `initkey.pas` - InitGostCtx: инициализация контекста

Тестирование:

- `testzone.pas` - TestZone2500: тест всех подпрограмм

## Запись на диск 2348

### Подготовка

Файлы подготовлены в формате БЭСМ-6:
- Заголовки: шифр, ОЗУ, АЦПУ, ТРА, ТЕЛЕ
- Директивы: `*name`, `*libra: 13`, `*pascal`
- Конец файла: `*execute`, `*end file`

### Компиляция

```bash
pascal add32.pas      # → зона 2501
pascal xor32.pas      # → зона 2502
pascal rot11.pas      # → зона 2503
pascal sbox8x4.pas    # → зона 2504
pascal feistel.pas    # → зона 2505
pascal encblk.pas     # → зона 2506
pascal decblk.pas     # → зона 2507
pascal initkey.pas    # → зона 2508
pascal testzone.pas   # → зона 2509
```

### Карта зон

| Зона | Файл | Точка входа |
|------|------|-------------|
| 2500 | - | Заголовок библиотеки |
| 2501 | add32.pas | Add32 |
| 2502 | xor32.pas | Xor32 |
| 2503 | rot11.pas | Rot11 |
| 2504 | sbox8x4.pas | Sbox8x4 |
| 2505 | feistel.pas | FeistelRound |
| 2506 | encblk.pas | EncryptBlock |
| 2507 | decblk.pas | DecryptBlock |
| 2508 | initkey.pas | InitGostCtx |
| 2509 | testzone.pas | TestZone2500 |

## Вызов из программ

```pascal
(* External declarations *)
Function Add32(x, y: UInt32): UInt32; external;
Function Xor32(x, y: UInt32): UInt32; external;
Function Rot11(x: UInt32): UInt32; external;

(* Usage *)
x := Add32(a, b);
x := Xor32(a, b);
x := Rot11(a);
```

## Обязательные соглашения

Для вызова подпрограмм из зоны 2500:

```pascal
program MyProgram(output);
type
  UInt32 = Integer;
var
  mod32: Integer;

Function Add32(x, y: UInt32): UInt32; external;

begin
  mod32 := 4294967296;  (* Required for external ref *)
  x := Add32(100, 200)
end.
```

## Тестирование

```bash
pascal testzone.pas
run testzone
```

Ожидаемый вывод:
```
=== Testing Zone 2500 Library ===
Test 1: Add32(100, 200) = 300
  PASS
Test 2: Xor32(5, 3) = 6
  PASS
...
All tests PASSED!
```

## Совместимость

- Диалект: Паскаль для БЭСМ-6
- Директива: `(*=e+*)`
- Макс. длина строки: 72 символа
- External-вызовы: поддерживаются

## Проблемы и решения

### Проблема: External не найден

**Решение**: Убедитесь, что подпрограмма скомпилирована в правильную зону.

### Проблема: Переполнение

**Решение**: Используйте mod32 := 4294967296 в вызывающей программе.

## Использование в прикладных программах

```pascal
program MyApp(output);
type
  W2 = Array[1..2] of Integer;
  CtxPtr = @Integer;

Procedure InitGostCtx(var c: CtxPtr; k: W8; s: SB8x4); external;
Procedure EncryptBlock(c: CtxPtr; var t: W2); external;
Procedure DecryptBlock(c: CtxPtr; var t: W2); external;

var
  ctx: Array[1..160] of Integer;
  data: W2;

begin
  InitGostCtx(ctx, key, sboxes);
  EncryptBlock(ctx, data);
  DecryptBlock(ctx, data)
end.
```
