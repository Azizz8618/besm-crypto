#!/usr/bin/env python3
"""Сборка деки bd_203.b6 из фрагментов (идемпотентно).

Структура деки (по образцу re-mars/small.b6 + golden):
  шапка: шифр 419999, лен 40(2348), *name Pascal, *call yesmemory,
         *perso:402570
  *assem DTRAN-преамбула МАРСа:
         библиотечные ячейки *bdvect*(168), *erstop*, *bdv*, *bderrn*,
         *bdc*(7) и рабочие области p/bdsys, p/bdtab, p/bdbuf (по 1024);
         без них PASBDI из библиотеки работает с мусорными указателями
         и падает 'ЗАТЕРТО СПО'
  *stand, *call *pascal
  program Main(input,output,bdvect) - программа (golden-механизм ГОСТ +
         переменные Э63/МАРСа + процедуры Э63/Э50/МАРС + главный диалог)
  .data, *no load list, *main start, *execute, *end file, ЕКОНЕЦ

ВАЖНО: строки Паскаль-исходника длиннее 72 символов обрезаются мониторным
вводом (9 слов УПП) - все строки фрагментов должны быть не длиннее 72.
"""
import os
import sys

WORK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'work')

# Шапка деки: ЛУ 40 = системный диск 2048 со смещением 630 (код МАРСа,
# читается Э70 из PASBDI - 'настройка на код МАРСа' по small.b6),
# ЛУ 41 = диск 2348 (наша библиотека 02570: паскаль+GOST+модули МАРСа),
# лента 203 (том АРФЫ) захватывается Э50 0157 по номеру из BESM6_PATH.
HEADER = """шифр 419999 зс5^
dis 40(2048-630)^
dis 41(2348)^
ОЗУ 32^
АЦПУ 140^
ТРА 37^
ТЕЛЕ^
eeв1а3
*name Pascal
*call yesmemory
*perso:412570"""

PREAMBLE = """*assem
 start:,name,
 *bdvect*:,lc,168
 *erstop*:,lc,1
 *bdv*:,lc,1
 *bderrn*:,lc,1
 *bdc*:,lc,7
 p/bdsys:,pc,1024
 p/bdtab:,pc,1024
 p/bdbuf:,pc,1024
 main:,subp,
 ,uj,main
 ,bss,377b . to make bdvect start from 01400
 ,end,"""

def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read().splitlines()

def main():
    deck = read(f'{WORK}/bd_203.b6')
    procs = read(f'{WORK}/bd_procs.txt')
    main_txt = read(f'{WORK}/bd_main.txt')

    # Швы.
    idx_prog = next(i for i, l in enumerate(deck) if l.startswith('program Main'))
    idx_banner = next(i for i, l in enumerate(deck)
                      if 'ДИАЛОГОВАЯ ПРОГРАММА' in l) - 1
    idx_data = max(i for i, l in enumerate(deck) if l.startswith('.data'))
    idx_exec = next(i for i, l in enumerate(deck)
                    if i > idx_data and l.startswith('*execute'))
    # .data-секция кончается строкой 'end' в кол.0; между нею и *execute
    # могли накопиться дубли '*no load list/*main start' от прежних сборок.
    idx_end = next(i for i, l in enumerate(deck)
                   if i > idx_data and l == 'end')
    idx_perso = next(i for i, l in enumerate(deck)
                     if l.startswith('*perso:'))
    assert idx_perso < idx_prog < idx_banner < idx_data < idx_exec
    assert deck[idx_prog + 1:idx_prog + 4] == ['%', '%', '%'], deck[idx_prog + 1]

    # Механизм: после строки Label до баннера. Строки 'Label ...'(от кол. 0)
    # в механизме быть не должно (объявление меток программы уже выдано выше);
    # повторное объявление даёт каскад ошибок 'ИДЕНТ НЕ ИДЕНТ ТИПА'.
    idx_label = next(i for i in range(idx_prog, idx_banner)
                     if deck[i].lstrip().lower().startswith('label'))
    mech = []
    have_pad = any('pad16' in l for l in deck[idx_label + 1:idx_banner])
    have_c2 = any('cifr2: alfa' in l for l in deck[idx_label + 1:idx_banner])
    for line in deck[idx_label + 1:idx_banner]:
        if line.startswith('Label ') or line.startswith('label '):
            continue
        if line.strip() == 'cifr, curk: alfa;':
            mech += ['    cifr: alfa;', '    curk: mw;']
        else:
            mech.append(line)
        if not have_pad and line.strip() in ('curk: mw;',
                                             'cifr, curk: alfa;'):
            mech.append('    pad16: array [1..16] of UInt32;')
            have_pad = True
        if not have_c2 and line.strip() == 'pad16: array [1..16] of UInt32;':
            mech.append('    cifr2: alfa;')
            have_c2 = True

    out = []
    out += HEADER.splitlines()         # шапка: ЛУ40=2048-630, ЛУ41=2348
    out += PREAMBLE.splitlines()        # DTRAN-преамбула МАРСа
    out += ['*stand', '*call *pascal']  # запуск компилятора
    out += [deck[idx_prog]]             # program Main
    out += ['%', '%', '%']
    out += ['Label 1,9;']               # только используемые метки
    out += mech                         # механизм golden
    out += procs                        # bd_procs.txt
    out += main_txt                     # bd_main.txt
    out += deck[idx_data:idx_end + 1]  # .data ... end (без накопленных дублей)
    out += ['*     no load list',
            '*main start']              # вход через DTRAN start -> main
    out += deck[idx_exec:]              # *execute, *end file, ЕКОНЕЦ

    # Контроль длины строк (>72 обрезается мониторным вводом).
    longs = [(i + 1, len(l)) for i, l in enumerate(out) if len(l) > 72]
    if longs:
        print('ВНИМАНИЕ: строки длиннее 72 символов:', longs[:10])

    with open(f'{WORK}/bd_203.b6', 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    print(f'собрано: {len(out)} строк -> {WORK}/bd_203.b6 '
          f'(механизм {len(mech)}, procs {len(procs)}, main {len(main_txt)})')

if __name__ == '__main__':
    sys.exit(main())
