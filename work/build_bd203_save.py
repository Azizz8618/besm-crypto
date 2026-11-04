#!/usr/bin/env python3
"""Сборка деки сохранения bd203_save.b6: компиляция диалоговой программы
и запись её модуля BD203 в библиотеку 02570 тома 2348 (персональная
библиотека ДИСПАКа, *to perso).

Основа - чистая bd_203.b6 (после build_bd_203.py). Отличия:
  - dis 41(2348-wr)          - том 2348 смонтирован с разрешением записи;
  - program bd203(...)        - имя программы = имя модуля в каталоге
                                (не длиннее 8 букв, как ARFALIB/PASCOMPL);
  - преамбула DTRAN: bd203:,subp / ,uj,bd203 - точка входа START прыгает
    на главную программу bd203 (связка по имени);
  - хвост: *to perso:412570 вместо *execute - временный каталог задачи
    (библиотека 02570 + модули этой задачи) записывается обратно на том;
    монитор печатает 'ДЛИНА LIBRARY <NNN> ЗОН'.

Запуск (том 2348 ищется по BESM6_PATH, нужен диск 2048 и системный 2053):
  BESM6_PATH=work:<системные диски> dispak -p work/bd203_save.b6
"""
import sys

WORK = '/home/z/my-project/besm-crypto/work'


def main():
    with open(f'{WORK}/bd_203.b6', encoding='utf-8') as f:
        deck = f.read().splitlines()

    out = []
    for l in deck:
        if l.startswith('dis 41(2348)'):
            l = 'dis 41(2348-wr)^'                # запись в том 2348
        elif l == ' main:,subp,':
            l = ' bd203:,subp,'                    # внешняя главная программа
        elif l == ' ,uj,main':
            l = ' ,uj,bd203'                       # вход START -> bd203
        elif l.startswith('program Main('):
            l = l.replace('program Main(', 'program bd203(', 1)
        elif l == '*     no load list':
            continue                              # хвост заменяем целиком
        elif l == '*main start':
            continue
        elif l == '*execute':
            # вместо выполнения - запись временного каталога на том
            out.append('*to perso:412570')
            continue
        out.append(l)

    with open(f'{WORK}/bd203_save.b6', 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    n = len(out)
    print(f'собрано: {n} строк -> {WORK}/bd203_save.b6')
    # контроль: главная программа переименована, хвост заменён
    txt = '\n'.join(out)
    assert 'program bd203(' in txt, 'program bd203 не переименована'
    assert 'bd203:,subp,' in txt, 'преамбула DTRAN не переименована'
    assert '*to perso:412570' in txt, 'нет *to perso'
    assert '*execute' not in txt, 'остался *execute'
    assert '*main start' not in txt, 'остался *main start'
    print('контроль: переименования и хвост в порядке')


if __name__ == '__main__':
    sys.exit(main())
