#!/usr/bin/env python3
"""Интерактивный прогон БД хешей паролей (лента 203, том АРФЫ) под pty.

Запускает `dispak -p <deck>` на псевдотерминале и отвечает на приглашения
PASRED. Отвечает по одному ответу на каждое приглашение '-' в начале
строки. Режимы:
    python3 work/run_bd_pty.py work/bd_203.b6 create    # создание БД + записи
    python3 work/run_bd_pty.py work/bd_203.b6 verify    # проверка содержимого
    python3 work/run_bd_pty.py work/bd_203.b6 <файл>    # ответы из файла

Лента 203 (том АРФЫ) модифицируется in-place; перед прогоном снимается
копия work/203.prev.
"""
import os
import pty
import select
import shutil
import subprocess
import sys
import time

DECK = sys.argv[1] if len(sys.argv) > 1 else 'work/bd_203.b6'
MODE = sys.argv[2] if len(sys.argv) > 2 else 'create'

PASS1 = 'parol-privat-1'
PASS2 = 'parol-privat-2'
SHIFR1 = '419900'
SHIFR2 = '419901'
AREA_PASS = '3999'

if MODE == 'create':
    ANSWERS = [
        '1',            # меню: создать область и базу данных
        AREA_PASS,      # шифр доступа к области (1-4095)
        '2',            # меню: добавить/заменить пользователя
        SHIFR1,         # шифр первого пользователя
        PASS1,          # пароль
        PASS1,          # пароль ещё раз
        '2',            # меню: добавить второго пользователя
        SHIFR2,         # шифр второго пользователя
        PASS2,          # пароль
        PASS2,          # пароль ещё раз
        '5',            # меню: сведения об области
        '0',            # меню: конец работы
    ]
elif MODE == 'verify':
    ANSWERS = [
        '5',            # сведения об области
        '3', SHIFR1,    # хеш первого пользователя
        '3', SHIFR2,    # хеш второго пользователя
        '0',            # конец работы
    ]
else:
    ANSWERS = [l.rstrip('\n') for l in open(MODE, encoding='utf-8') if l.strip()]

env = dict(os.environ)

# Копия ленты перед прогоном (лента модифицируется in-place).
if os.path.exists('work/203'):
    shutil.copy('work/203', 'work/203.prev')

master, slave = pty.openpty()
cmd = ['dispak'] + os.environ.get('DISPAK_EXTRA', '').split() + ['-p', DECK]
proc = subprocess.Popen(cmd, stdin=slave, stdout=slave,
                        stderr=slave, env=env, close_fds=True)
os.close(slave)

buf = b''
sent = 0
what_sent = 0
deadline = time.time() + 600
MAXOUT = 4 * 1024 * 1024          # защита от циклического вывода
progress = open(DECK + '.log', 'wb')   # пишем на лету - лог останется и при таймауте

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

        # Приглашение PASRED - одиночный '-' в начале строки.
        nprompt = text.count('\n-\r')
        while sent < len(ANSWERS) and nprompt > sent:
            os.write(master, (ANSWERS[sent] + '\n').encode('utf-8'))
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

sys.stdout.write(buf.decode('utf-8', 'ignore'))
print('\n=== ПРИГЛАШЕНИЙ ОТВЕЧЕНО: %d/%d ===' % (sent, len(ANSWERS)),
      file=sys.stderr)
