#!/bin/bash
# Проверка библиотеки ГОСТ для БЭСМ-6

echo "=== Проверка файлов библиотеки ГОСТ ==="
echo

echo "1. Проверка наличия файлов:"
for f in gostcore.pas gostmode.pas gstutil.pas gostbox.pas testgost.pas testall.pas; do
    if [ -f "src/$f" ]; then
        echo "  ✓ src/$f"
    else
        echo "  ✗ src/$f - ОТСУТСТВУЕТ"
    fi
done
echo

echo "2. Проверка длины строк (max 72 символа):"
for f in src/*.pas; do
    long=$(awk 'length($0) > 71 {print NR": "length($0)}' "$f" | wc -l)
    if [ "$long" -eq 0 ]; then
        echo "  ✓ $f - все строки <= 72 символов"
    else
        echo "  ✗ $f - $long строк длиннее 72 символов"
    fi
done
echo

echo "3. Проверка директив компилятора:"
for f in src/*.pas; do
    if grep -q "^(\*=e+\*)" "$f"; then
        echo "  ✓ $f - директива (*=e+*) найдена"
    else
        echo "  ✗ $f - директива (*=e+*) не найдена"
    fi
done
echo

echo "4. Проверка external-функций:"
for f in src/*.pas; do
    ext=$(grep -c "external;" "$f" || echo 0)
    if [ "$ext" -eq 0 ]; then
        echo "  ✓ $f - нет external-функций"
    else
        echo "  ✗ $f - найдено $ext external-функций"
    fi
done
echo

echo "5. Статистика:"
echo "  Всего строк кода: $(cat src/*.pas | wc -l)"
echo "  Количество файлов: $(ls src/*.pas | wc -l)"
echo

echo "=== Проверка завершена ==="
