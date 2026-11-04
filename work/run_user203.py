#!/usr/bin/env python3
"""Прогон пользовательских программ раздела АРФЫ (лента 203) под pty.

Программы вызываются по имени из библиотеки 02570 тома 2348 (записаны
деками par203_save.b6, zap203_save.b6, pro203_save.b6):

    par    ПАР203 - задание хеш-пароля (лента не нужна)
    zap    ЗАП203 - захват 203, создание раздела, запись шифртекста
                   (перед прогоном ставится свежий том: 203.clean)
    pro    ПРО203 - чтение шифртекста и расшифровка хеш-паролем
    proneg ПРО203 - то же с неверным паролем (ожидаются нечитаемые
                   данные - негативная демонстрация)

Использование:
    python3 work/run_user203.py            # par, zap, pro
    python3 work/run_user203.py par zap    # выборочно

Логи: work/par203_run.log, work/zap203_run.log, work/pro203_run.log,
work/proneg_run.log.

АЦПУ печатает кириллицу вперемешку с латинскими двойниками (A, B, C,
E, H, K, M, O, P, T, X, Y), поэтому ожидаемые строки сверяются после
нормировки обеих сторон к кириллице (fold()).
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

PASS1 = 'parol-privat-1'        # секретный пароль пользователя
WRONGPASS = 'parol-ne-vernyi'   # неверный пароль (негативный прогон)
AREA_PASS = '3999'              # шифр доступа к разделу ТЕСТ
MSG = 'user-arfa-203'           # сообщение пользователя

ANSWERS = {
    # Passgen спрашивает пароль дважды (внутренний контроль), Passver - один раз
    'par': [PASS1, PASS1],
    'zap': [AREA_PASS, PASS1, PASS1, MSG],
    'pro': [PASS1],
    'proneg': [WRONGPASS],
}

DECKS = {
    'par': f'{WORK}/par203_run.b6',
    'zap': f'{WORK}/zap203_run.b6',
    'pro': f'{WORK}/pro203_run.b6',
    'proneg': f'{WORK}/pro203_run.b6',
}

LOGS = {
    'par': f'{WORK}/par203_run.log',
    'zap': f'{WORK}/zap203_run.log',
    'pro': f'{WORK}/pro203_run.log',
    'proneg': f'{WORK}/proneg_run.log',
}

EXPECT = {
    'par': 'ХЕШ-ПАРОЛЬ (8 СЛОВ',
    'zap': 'ГОТОВО: СООБЩЕНИЕ ЗАШИФРОВАНО',
    'pro': 'РАСШИФРОВАННОЕ СООБЩЕНИЕ',
    'proneg': 'ТОМ 203 ОСВОБОЖДЕН',
}

# латинские двойники, которыми АЦПУ заменяет кириллицу
_LAT = 'ABCEHKMOPTXY'
_CYR = 'АВСЕНКМОРТХУ'


def fold(s):
    """Нормировка к кириллице: латинские двойники -> кириллица."""
    res = []
    for ch in s:
        i = _LAT.find(ch)
        res.append(_CYR[i] if i >= 0 else ch)
    return ''.join(res).upper()


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
    MAXOUT = 4 * 1024 * 1024
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
            if len(buf) <= MAXOUT:
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
                    if len(buf) <= MAXOUT:
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


def main():
    which = sys.argv[1:] or ['par', 'zap', 'pro']
    if 'zap' in which:
        stage_fresh_volume()
        print(f'свежий том АРФЫ: {STAGE}/203 (из 203.clean)')
    elif 'pro' in which or 'proneg' in which:
        if not os.path.exists(f'{STAGE}/203'):
            print('!!! нет staged-тома: сначала запустите zap')
            return 2
    ok = True
    for name in which:
        if name not in DECKS:
            print(f'неизвестный прогон: {name}')
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
        ftext = fold(text)
        if fold(EXPECT[name]) in ftext:
            print(f'  ОЖИДАЕМЫЙ РЕЗУЛЬТАТ НАЙДЕН: {EXPECT[name]}')
        else:
            print(f'  !!! ОЖИДАЕМОЕ НЕ НАЙДЕНО: {EXPECT[name]}')
            ok = False
    print('=== ИТОГ:', 'ВСЕ ПРОГОНЫ ПРОШЛИ' if ok else 'ЕСТЬ ОШИБКИ',
          '===')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
