#!/bin/bash
# Проверка файлов зоны 2500

echo "=== Checking Zone 2500 Files ==="
echo

echo "1. File count:"
count=$(ls zone2500/*.pas 2>/dev/null | wc -l)
echo "   $count Pascal files"
echo

echo "2. Line length (max 72 chars):"
for f in zone2500/*.pas; do
    long=$(awk 'length($0) > 71' "$f" | wc -l)
    if [ "$long" -eq 0 ]; then
        echo "   ✓ $(basename $f)"
    else
        echo "   ✗ $(basename $f) - $long lines > 72 chars"
    fi
done
echo

echo "3. Required directives:"
for f in zone2500/*.pas; do
    name=$(grep "^\*name" "$f" | awk '{print $2}')
    if [ -n "$name" ]; then
        echo "   ✓ $(basename $f) - name: $name"
    else
        echo "   ✗ $(basename $f) - missing *name"
    fi
done
echo

echo "4. External declarations:"
for f in zone2500/*.pas; do
    ext=$(grep -c "external;" "$f" 2>/dev/null || echo "0")
    if [ "$ext" -gt 0 ]; then
        echo "   $(basename $f) - $ext external refs"
    fi
done
echo

echo "5. Input/Output points:"
for f in zone2500/*.pas; do
    funcs=$(grep "^Function\|^Procedure" "$f" | grep -v "external" | wc -l)
    if [ "$funcs" -gt 0 ]; then
        echo "   $(basename $f) - $funcs entry points"
    fi
done
echo

echo "=== Check Complete ==="
