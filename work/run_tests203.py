#!/usr/bin/env python3
"""Прогон тестов раздела АРФА на ленте 203 под pty.

Готовит свежий том АРФЫ (копия work/203.clean -> work/tstage/203),
запускает деки на псевдотерминале и отвечает на приглашения PASRED:

    t1      цикл создания хеш-пароля (лента не нужна)
    t2      создание раздела АРФЫ + запись шифртекста
    t3      чтение из раздела + расшифровка хеш-паролем (PASS)
    t3neg   то же с неверным паролем (ожидается FAIL)

Использование:
    python3 work/run_tests203.py          # все тесты по порядку
    python3 work/run_tests203.py t2 t3    # выборочно
Логи: work/t1_hash.log, work/t2_wr203.log, work/t3_rd203.log,
work/t3neg_rd203.log. После t2 печатается дамп зоны 0 области из
образа ленты (контроль физической записи шифртекста).
"""
import os
import pty
import select
import shutil
import subprocess
import sys
import time

ROOT = '/home/z/my-project/besm-crypto'
WORK = f'{ROOT}/work'
DISPAK_DIR = '/home/z/my-project/dispak/build/dispak'
STAGE = f'{WORK}/tstage'

PASS1 = 'parol-privat-1'        # пароль (хеш-пароль от него)
WRONGPASS = 'parol-ne-vernyi'   # неверный пароль для негативного теста
AREA_PASS = '3999'              # шифр доступа к области ТЕСТ
MSG = 'test-arfa-203'           # контрольное сообщение

ANSWERS = {
    't1': [PASS1, PASS1, PASS1, WRONGPASS],
    't2': [AREA_PASS, PASS1, PASS1, MSG],
    't3': [PASS1, MSG],
    't3neg': [WRONGPASS, MSG],
}

DECKS = {
    't1': f'{WORK}/t1_hash.b6',
    't2': f'{WORK}/t2_wr203.b6',
    't3': f'{WORK}/t3_rd203.b6',
    't3neg': f'{WORK}/t3_rd203.b6',
}

LOGS = {
    't1': f'{WORK}/t1_hash.log',
    't2': f'{WORK}/t2_wr203.log',
    't3': f'{WORK}/t3_rd203.log',
    't3neg': f'{WORK}/t3neg_rd203.log',
}

EXPECT = {'t1': '*** TEST 1 PASSED ***',
          't2': '*** TEST 2 PASSED ***',
          't3': '*** TEST 3 PASSED ***',
          't3neg': '*** TEST 3 FAILED ***'}


def stage_fresh_volume():
    """Свежий том АРФЫ: work/203.clean -> work/tstage/203."""
    os.makedirs(STAGE, exist_ok=True)
    for f in os.listdir(STAGE):
        os.remove(os.path.join(STAGE, f))
    shutil.copy(f'{WORK}/203.clean', f'{STAGE}/203')


def run_deck(name, timeout=900):
    """Один прогон деки на pty с ответами; возвращает (текст, n, всего)."""
    answers = ANSWERS[name]
    env = dict(os.environ)
    env['BESM6_PATH'] = f'{STAGE}:{WORK}:{DISPAK_DIR}'
    env['PATH'] = f'{DISPAK_DIR}:' + env.get('PATH', '')

    master, slave = pty.openpty()
    cmd = ['dispak'] + env.get('DISPAK_EXTRA', '').split() \
        + ['-p', DECKS[name]]
    proc = subprocess.Popen(cmd, stdin=slave, stdout=slave,
                            stderr=slave, env=env, close_fds=True)
    os.close(slave)

    buf = b''
    sent = 0
    what_sent = 0
    deadline = time.time() + timeout
    progress = open(LOGS[name], 'wb')

    while time.time() < deadline:
        ready, _, _ = select.select([master], [], [], 0.5)
        if ready:
            try:
                chunk = os.read(master, 4096)
            except OSError:
                break
            if not chunk:
                break
            buf += chunk
            progress.write(chunk)
            progress.flush()
            text = buf.decode('utf-8', 'ignore')

            nwhat = text.count('WНАТ=')
            if nwhat > what_sent:
                for _ in range(nwhat - what_sent):
                    os.write(master, b'\n')
                what_sent = nwhat

            nprompt = text.count('\n-\r')
            while sent < len(answers) and nprompt > sent:
                os.write(master,
                         (answers[sent] + '\n').encode('utf-8'))
                sent += 1

        if proc.poll() is not None:
            time.sleep(0.5)
            try:
                while True:
                    chunk = os.read(master, 4096)
                    if not chunk:
                        break
                    buf += chunk
                    progress.write(chunk)
            except OSError:
                pass
            break

    progress.close()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
    os.close(master)
    text = buf.decode('utf-8', 'ignore')
    return text, sent, len(answers)


def dump_area_zone():
    """Дамп зоны 0030 (данные области ТЕСТ) из образа staged-тома."""
    sys.path.insert(0, '/home/z/my-project/scripts')
    from arfa_inspect import read_zone
    words = read_zone(f'{STAGE}/203', 0o30)
    print('  --- зона 0030 тома 203 (зона 0 области ТЕСТ), '
          'первые 20 слов ---')
    for i in range(20):
        l, r = words[i]
        print(f'  {i:04o}: {l:08o} {r:08o}')
    print(f'  слово 0 (длина+IV): {words[0][0]:o} ; '
          f'остальные нулевые: '
          f'{all(w == (0, 0) for w in words[21:])}')


def main():
    which = sys.argv[1:] or ['t1', 't2', 't3', 't3neg']
    # свежий том размечается только перед t2 (создание области);
    # t3/t3neg читают область, записанную предыдущим t2
    if 't2' in which:
        stage_fresh_volume()
        print(f'свежий том АРФЫ: {STAGE}/203 (из 203.clean)')
    elif not os.path.exists(f'{STAGE}/203'):
        print('!!! нет staged-тома: сначала запустите t2')
        return 2
    ok = True
    for name in which:
        if name not in DECKS:
            print(f'неизвестный тест: {name}')
            return 2
        print(f'=== {name}: {DECKS[name]} ===')
        t0 = time.time()
        text, sent, total = run_deck(name)
        dt = time.time() - t0
        print(f'  ответов: {sent}/{total}, время {dt:.0f} с')
        if sent < total:
            print('  !!! НЕ ВСЕ ОТВЕТЫ ОТПРАВЛЕНЫ (зависание?)')
            ok = False
        if 'КОНЕЦ ЗАДАЧИ' in text:
            print('  задача завершилась штатно')
        else:
            print('  !!! ЗАДАЧА НЕ ЗАВЕРШИЛАСЬ')
            ok = False
        if EXPECT[name] in text:
            print(f'  ОЖИДАЕМЫЙ РЕЗУЛЬТАТ: {EXPECT[name]}')
        else:
            print(f'  !!! ОЖИДАЕМЫЙ РЕЗУЛЬТАТ НЕ НАЙДЕН: {EXPECT[name]}')
            ok = False
        if name == 't2':
            dump_area_zone()
    print('=== ИТОГ:', 'ВСЕ ТЕСТЫ ПРОШЛИ' if ok else 'ЕСТЬ ОШИБКИ', '===')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
