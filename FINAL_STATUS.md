# Статус реализации библиотеки ГОСТ 28147-89 для БЭСМ-6

## Диск 2348 - Обновлено 25.10.2026

### Выполнено

**Компилятор Pascal (зона 2000):**
- Pascal Compiler **2026 (25.10.26)** - записан через pascal-re PERSO
- Работает через *perso:402000, *stand, *call *pascal

**Runtime библиотеки (зона 2300):**
- Скопированы с диска 2048 (зоны 1700-1763)
- Содержат: P/WI, P/WL, P/SYS, P/CA, P/CE и др.

**Библиотеки шифрования (зона 2500):**
- Скопированы с диска 2148 (зоны 1000-1077)
- Содержат LIBRA с процедурами GOST

### Структура диска 2348

| Зона | Содержимое |
|------|------------|
| 2000 | Pascal Compiler 2026 (PERSO) |
| 2300 | Runtime библиотеки |
| 2500 | Библиотеки (LIBRA) |

### Тестирование

Финальный тест пройден:
```
=== FINAL TEST ===
Compiler: Pascal 2026
Runtime: OK
GOST lib: available at 2500
100+200= 300
100-50= 50
1 2 3
ALL TESTS PASSED
```

### Расположение

- **Рабочая копия:** `~/Yandex.Disk/simh/BESM6/MD/EC5061/2348`
- **Резервная:** `/usr/local/share/besm6/2348`
- **Локальная:** `~/besm6/2348`

### Запуск тестов

```bash
cd /home/azizz/Yandex.Disk/pascal-re
export BESM6_PATH=~/Yandex.Disk/simh/BESM6/MD/EC5061:/home/azizz/.besm6:/usr/local/share/besm6
./tools/perso-run.sh <program.pas> --zone=2000
```

### Источники

- Pascal compiler source: https://github.com/besm6/pascal-re
- Эмулятор BESM-6: /home/azizz/Yandex.Disk/simh/BESM6/
- DISPAK: /home/azizz/Yandex.Disk/dispak/
