#!/usr/bin/env python3
"""Сборка дек тестов раздела АРФЫ (лента 203) из фрагментов.

Три деки (по образцу golden_1task_h.b6, БЕЗ МАРС-преамбулы):
  work/t1_hash.b6   - тест 1: цикл создания хеш-пароля (ГОСТ 34.11-94)
  work/t2_wr203.b6  - тест 2: создание раздела АРФЫ (Э63) + запись
                      шифртекста (ключ = хеш-пароль) в зону области
  work/t3_rd203.b6  - тест 3: чтение шифртекста из раздела и
                      расшифровка хеш-паролем (ГОСТ 28147-89)

Механизм (типы/переменные/криптопроцедуры Passgen/HashMessage/...)
извлекается из проверенной деки work/bd_203.b6: от строки 'program
Main' до конца Passver. Процедуры Э63 - work/t_procs.txt (имя области
'ТЕСТ/419999'), главные модули - work/t{1,2,3}_main.txt.

ВАЖНО: строки длиннее 72 символов обрезаются мониторным вводом.
"""
import sys

WORK = '/home/z/my-project/besm-crypto/work'

# Шапка по образцу golden_1task_h.b6: ЛУ40 = том 2348 с библиотекой
# 02570 (паскаль-runtime + pasred). Лента 203 в паспорте не нужна:
# том захватывается Э50 0157 и заказывается Э63 12 из программы.
HEADER = """шифр 419999 зс5^
лен 40(2348)^
ОЗУ 32^
АЦПУ 140^
ТРА 37^
ТЕЛЕ^
eeв1а3
*name
*call yesmemory
*perso:402570
*stand
*call *pascal"""

# Заголовок программы - как в golden (файлы pastel/fres/result/keyf/ctxt
# объявлены и в механизме, и в заголовке; s7 - без контроля диапазонов,
# l3 - уровень главной программы для файлового ввода-вывода).
PROG = ("program Main(input,output,pastel,fres,result,keyf,ctxt);"
        "(*=s7,l3,Y+*)")

# Дополнительные переменные тестов (вставляются в раздел var механизма).
EXTRA_VARS = """    tmsg: Array[1..100] of Integer;
    tct: Array[1..101] of Integer;
    tdec: Array[1..100] of Integer;
    mlen, mlen2, iv, nwords: Integer;"""

TAIL = """*execute
*end file
``````
ЕКОНЕЦ"""


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read().splitlines()


def extract_mechanism(deck, label_line):
    """bd_203.b6: от 'program Main' до конца Passver (последний
    'PASTEL[16] ... - [10]' + 'end;'), без golden-процедур носителей."""
    idx_prog = next(i for i, l in enumerate(deck)
                    if l.startswith('program Main'))
    idx_pastel = max(i for i, l in enumerate(deck)
                     if l.strip() == 'PASTEL[16] := PASTEL[16] - [10];')
    idx_end = next(i for i in range(idx_pastel, len(deck))
                   if deck[i] == 'end;')
    mech = deck[idx_prog:idx_end + 1]
    mech[0] = PROG
    # метки главного блока: у каждого теста свои (в t1 меток нет;
    # объявленная, но не определённая метка - ошибка трансляции)
    idx_label = next(i for i, l in enumerate(mech)
                     if l.strip().lower().startswith('label'))
    if label_line:
        mech[idx_label] = label_line
    else:
        del mech[idx_label]
    # вставка доп. переменных после 'connected, opened: boolean;'
    idx_vars = next(i for i, l in enumerate(mech)
                    if l.strip() == 'connected, opened: boolean;')
    mech = (mech[:idx_vars + 1] + EXTRA_VARS.splitlines()
            + mech[idx_vars + 1:])
    return mech


def extract_data(deck):
    idx_data = next(i for i, l in enumerate(deck)
                    if l.startswith('.data'))
    idx_end = next(i for i in range(idx_data, len(deck))
                   if deck[i] == 'end')
    return deck[idx_data:idx_end + 1]


def build(main_txt, out_path, deck, procs, label_line):
    out = []
    out += HEADER.splitlines()
    out += extract_mechanism(deck, label_line)
    out += read(procs)
    out += read(main_txt)
    out += extract_data(deck)
    out += TAIL.splitlines()
    longs = [(i + 1, len(l)) for i, l in enumerate(out) if len(l) > 72]
    if longs:
        print('ВНИМАНИЕ: строки длиннее 72 символов:', longs[:10])
        return 1
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    print(f'собрано: {len(out)} строк -> {out_path}')
    return 0


def main():
    deck = read(f'{WORK}/bd_203.b6')
    rc = 0
    for out_name, main, label in (('t1_hash.b6', 't1_main.txt', ''),
                                  ('t2_wr203.b6', 't2_main.txt', 'Label 9;'),
                                  ('t3_rd203.b6', 't3_main.txt', 'Label 9;')):
        rc |= build(f'{WORK}/{main}', f'{WORK}/{out_name}',
                    deck, f'{WORK}/t_procs.txt', label)
    return rc


if __name__ == '__main__':
    sys.exit(main())
