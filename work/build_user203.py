#!/usr/bin/env python3
"""Сборка пользовательских программ раздела АРФЫ (лента 203) для записи
в библиотеку 02570 тома 2348.

По образцу тестов t1/t2/t3 (build_tests203.py) и записи диалоговой
программы bd203 (build_bd203_save.py). Три программы:

  par203 (ПАР203) - задание хеш-пароля пользователя (ГОСТ 34.11-94);
  zap203 (ЗАП203) - монопольный захват 203 (Э50 0157), создание раздела
                    ТЕСТ/419999 (Э63 01/03), шифрование сообщения
                    хеш-паролем (ГОСТ 28147-89, гаммирование) и запись
                    в зону 0 раздела;
  pro203 (ПРО203) - чтение шифртекста из раздела и расшифровка
                    хеш-паролем.

Деки (результат сборки):
  par203_save.b6, zap203_save.b6, pro203_save.b6 - трансляция + запись
      модуля в библиотеку 02570 (*to perso:412570); DTRAN-обвязка:
      входы parol/zapis/prosm -> uj на главную программу (как СТАРТ ->
      bd203 у диалоговой программы);
  par203_run.b6, zap203_run.b6, pro203_run.b6 - вызов по имени
      (*call parol/zapis/prosm), без трансляции.

Механизм (типы, переменные, криптопроцедуры Passgen/HashMessage/
InitGostCtx/EncryptBlock/Xor/CurrTime) извлекается из проверенной деки
work/bd_203.b6; процедуры Э63/Э50 - work/t_procs.txt; главные модули -
work/u_{par,zap,pro}_main.txt.

ВАЖНО: строки деки длиннее 72 символов обрезаются мониторным вводом.
"""
import sys

WORK = '/home/z/my-project/besm-crypto/work'

# Шапка деки записи: том 2348 монтируется с разрешением записи (ЛУ 41),
# библиотека 02570 - компилятор + runtime + GOSTLIB + МАРС-модули.
SAVE_HEADER = """шифр 419999 зс5^
dis 41(2348-wr)^
ОЗУ 32^
АЦПУ 140^
ТРА 37^
ТЕЛЕ^
eeв1а3
*name
*call yesmemory
*perso:412570"""

# Шапка деки вызова: том 2348 только для чтения (как у тестов t1-t3).
RUN_HEADER = """шифр 419999 зс5^
лен 40(2348)^
ОЗУ 32^
АЦПУ 140^
ТРА 37^
ТЕЛЕ^
eeв1а3
*name
*call yesmemory
*perso:402570
*no list"""

# Заголовок программы: файлы pastel/fres/result/keyf/ctxt объявлены в
# механизме; s7 - без контроля диапазонов, l3 - уровень главной
# программы для файлового ввода-вывода.
PROG = ("program {name}(input,output,pastel,fres,result,keyf,ctxt);"
        "(*=s7,l3,Y+*)")

# Дополнительные переменные (вставляются в раздел var механизма).
EXTRA_VARS = """    tmsg: Array[1..100] of Integer;
    tct: Array[1..101] of Integer;
    tdec: Array[1..100] of Integer;
    mlen, mlen2, iv, nwords: Integer;"""

# DTRAN-обвязка модуля: вход <entry> (модуль ПАРОЛ/ЗАПИС/ПРОСМ) прыгает
# на главную программу <name> (модуль ПАР203/ЗАП203/ПРО203) - как
# СТАРТ -> bd203 у диалоговой программы. Имена входов и программ
# различны, чтобы не столкнуться в общем каталоге библиотеки.
ASSEM = """*assem
 {entry}:,name,
 {name}:,subp,
 ,uj,{name}
 ,end,"""

SAVE_TAIL = """*to perso:412570
*end file
``````
ЕКОНЕЦ"""

RUN_TAIL = """*end file
``````
ЕКОНЕЦ"""

PROGRAMS = (
    # (имя программы, имя входа, главный модуль, метки главного блока)
    ('par203', 'parol', 'u_par_main.txt', ''),
    ('zap203', 'zapis', 'u_zap_main.txt', 'Label 9;'),
    ('pro203', 'prosm', 'u_pro_main.txt', 'Label 9;'),
)


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read().splitlines()


def extract_mechanism(deck, label_line, progname):
    """bd_203.b6: от 'program Main' до конца Passver (последний
    'PASTEL[16] ... - [10]' + 'end;'), без golden-процедур носителей."""
    idx_prog = next(i for i, l in enumerate(deck)
                    if l.startswith('program Main'))
    idx_pastel = max(i for i, l in enumerate(deck)
                     if l.strip() == 'PASTEL[16] := PASTEL[16] - [10];')
    idx_end = next(i for i in range(idx_pastel, len(deck))
                   if deck[i] == 'end;')
    mech = deck[idx_prog:idx_end + 1]
    mech[0] = PROG.format(name=progname)
    # метки главного блока: у каждой программы свои (объявленная, но
    # не определённая метка - ошибка трансляции)
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


def build_save(progname, entry, main_txt, label_line, deck):
    out = []
    out += SAVE_HEADER.splitlines()
    out += ASSEM.format(entry=entry, name=progname).splitlines()
    out += ['*stand', '*call *pascal']
    out += extract_mechanism(deck, label_line, progname)
    out += read(f'{WORK}/t_procs.txt')
    out += read(f'{WORK}/{main_txt}')
    out += extract_data(deck)
    out += SAVE_TAIL.splitlines()
    return out


def build_run(entry):
    out = RUN_HEADER.splitlines()
    out += [f'*call {entry}']
    out += RUN_TAIL.splitlines()
    return out


def check_lines(out, what):
    longs = [(i + 1, len(l)) for i, l in enumerate(out) if len(l) > 72]
    if longs:
        print(f'ВНИМАНИЕ: строки длиннее 72 символов в {what}:',
              longs[:10])
        return False
    return True


def main():
    deck = read(f'{WORK}/bd_203.b6')
    ok = True
    for progname, entry, main_txt, label_line in PROGRAMS:
        save = build_save(progname, entry, main_txt, label_line, deck)
        ok &= check_lines(save, f'{progname}_save.b6')
        with open(f'{WORK}/{progname}_save.b6', 'w',
                  encoding='utf-8') as f:
            f.write('\n'.join(save) + '\n')
        print(f'собрано: {len(save)} строк -> '
              f'{WORK}/{progname}_save.b6 (вход {entry})')
        run = build_run(entry)
        ok &= check_lines(run, f'{progname}_run.b6')
        with open(f'{WORK}/{progname}_run.b6', 'w',
                  encoding='utf-8') as f:
            f.write('\n'.join(run) + '\n')
        print(f'собрано: {len(run)} строк -> {WORK}/{progname}_run.b6')
    # контроль структуры дек записи
    for progname, entry, _, _ in PROGRAMS:
        txt = open(f'{WORK}/{progname}_save.b6',
                   encoding='utf-8').read()
        assert f'program {progname}(' in txt, \
            f'{progname}: программа не переименована'
        assert f' {entry}:,name,' in txt, f'{progname}: нет входа {entry}'
        assert f',uj,{progname}' in txt, f'{progname}: нет uj'
        assert '*to perso:412570' in txt, f'{progname}: нет *to perso'
        assert '*execute' not in txt, f'{progname}: остался *execute'
        assert '*bdvect*:' not in txt, \
            f'{progname}: лишние МАРС-ячейки *bdvect* в DTRAN'
    print('контроль: имена программ, входы DTRAN и хвосты в порядке')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
