#!/bin/bash
# Компиляция всех модулей библиотеки ГОСТ 28147-89

DISPAK=~/Yandex.Disk/rezerv/build/dispak/dispak
DISK=~/Yandex.Disk/simh/BESM6/MD/EC5061/2348
WORKDIR=~/Yandex.Disk/besm-crypto

# Карта зон
declare -A ZONES=(
    ["add32.pas"]=2501
    ["xor32.pas"]=2502
    ["rot11.pas"]=2503
    ["sbox8x4.pas"]=2504
    ["feistel.pas"]=2505
    ["encblk.pas"]=2506
    ["decblk.pas"]=2507
    ["initkey.pas"]=2508
)

# Компиляция каждого модуля
for file in "${!ZONES[@]}"; do
    zone=${ZONES[$file]}
    echo "Compiling $file to zone $zone..."
    
    # Создаём задачу с указанием зоны вывода
    cat > /tmp/pascal_task.txt << EOF
ШИФР 419999 ЗС5^
ОЗУ 32^
ТРА 100^
АЦП 128^
ЕЕВ1А3
$(cat zone2500/$file)
*EXECUTE
*END FILE

\`\`\`\`\`\`
ЕКОНЕЦ
EOF
    
    $DISPAK /tmp/pascal_task.txt -p 2>&1 | head -100
    echo "---"
done

echo "All modules compiled!"
