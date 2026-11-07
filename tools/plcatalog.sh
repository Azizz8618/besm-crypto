#!/bin/bash
# tools/plcatalog.sh — просмотр каталога библиотеки perso (личной библиотеки)
# по образцу dis.bat из репозитория monitor-re.
#
# Сценарий формирует задание dispak: подключает системный диск и личную
# библиотеку, затем вызывает программу PLCATALOG, которая печатает каталог
# личной библиотеки (имена модулей, зоны, длины).
#
# Использование:
#   tools/plcatalog.sh [perso-том] [системный том]
# по умолчанию: perso 67, системный 705 (как в dis.bat)
#
# Пример:
#   BESM6_PATH=~/Yandex.Disk/simh/BESM6/MD/EC5061:~/.besm6:/usr/local/share/besm6 \
#     tools/plcatalog.sh 67
#
# Результат печатается на stdout; при желании перенаправьте в файл:
#   tools/plcatalog.sh > work/perso.txt

#SYS="${2:-705}"
DISK="${1}"
PERSO="40${2}"

job="plcatalog$$.b6"

cat > "$job" <<EOF
шифр 419999ЗС5^
ОЗУ 32^
дис 40($DISK)^
АЦПУ 140^
ТРА 37^
eeв1а3
*name catperso
*time:24.00
*express
*libra:23
*        disc:$SYS/system,lcross
*        file:libra,$PERSO,r
*perso:$PERSO
*call plcatalog:$PERSO
*end file
\`\`\`\`\`\`
еконец
EOF
cat "$job"
dispak "$job"
rc=$?
rm -f "$job"
exit $rc
