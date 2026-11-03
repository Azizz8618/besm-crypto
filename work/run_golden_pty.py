#!/usr/bin/env python3
"""Интерактивный прогон golden-программы под pty.

Запускает `dispak -p <deck>` на псевдотерминале и отвечает на приглашения
PASRED по очереди. Нужен потому, что golden-задача объявлена как `ТЕЛЕ^`
и читает ввод с терминала, а не из деки.

Проверено: полный диалог — спецноситель лента 203, создание пароля,
шифрование и расшифрование HELLO, штатное завершение `КОНЕЦ ЗАДАЧИ`.
Требуется dispak с реализованным Е50 0157 (захват тома); лог прогона —
`work/golden_pty.log`, описание — `docs/GOLDEN-DIALOG.md`.

Использование:
    python3 work/run_golden_pty.py work/golden_1task_h.b6
"""
import os
import pty
import select
import shutil
import subprocess
import sys
import tempfile
import time

DECK = sys.argv[1] if len(sys.argv) > 1 else 'work/golden_1task_h.b6'
CARRIER = '203'    # спецноситель - лента БЭСМ (тома <2048 = НМЛ); 2061 занят системой
STZONE = '100'     # начальная зона массива
LENGTH = '10'      # длина массива в зонах
ETX = '\x7f'       # ETX: завершить ввод параметров носителя

# Ответы в порядке появления приглашений PASRED (одиночное '-' в начале
# строки).  Сначала параметры спецносителя, затем пароль и шифрование,
# затем параметры носителя для записи.
ANSWERS = [
    CARRIER,        # номер носителя
    '1',            # режим: 1 = чтение
    STZONE,         # номер начальной зоны
    LENGTH,         # длина массива в зонах
    ETX,            # завершить ввод параметров
    '1',            # меню: создать новый пароль
    'testpass123',  # пароль
    'testpass123',  # пароль ещё раз
    '1',            # тип работы: шифрование
    '1',            # источник: терминал
    'HELLO',        # строка сообщения
    '!!кнц',        # конец сообщения
    CARRIER,        # носитель для записи
    '0',            # режим записи
    STZONE,         # начальная зона записи
    LENGTH,         # длина массива записи
    ETX,            # завершить ввод параметров
    '2',            # выход
]

env = dict(os.environ)
search = env.get('BESM6_PATH', '').split(':')
search = [p for p in search if p]

# Рабочая копия носителя: golden может писать на него, оригинал не трогаем.
tmpdir = tempfile.mkdtemp(prefix='besm6-disks-')
for d in search:
    src = os.path.join(d, CARRIER)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(tmpdir, CARRIER))
        break
env['BESM6_PATH'] = ':'.join([tmpdir] + search)

master, slave = pty.openpty()
proc = subprocess.Popen(['dispak', '-p', DECK], stdin=slave, stdout=slave,
                        stderr=slave, env=env, close_fds=True)
os.close(slave)

buf = b''
sent = 0
what_sent = 0
deadline = time.time() + 180

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
        text = buf.decode('utf-8', 'ignore')

        # Monitor печатает WНАТ= на непонятых картах и ждёт оператора.
        nwhat = text.count('WНАТ=')
        if nwhat > what_sent:
            for _ in range(nwhat - what_sent):
                os.write(master, b'\n')
            what_sent = nwhat

        # Приглашение PASRED — одиночный '-' в начале строки.
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
        except OSError:
            pass
        break

try:
    proc.wait(timeout=10)
except subprocess.TimeoutExpired:
    proc.kill()
    proc.wait()
os.close(master)
shutil.rmtree(tmpdir, ignore_errors=True)

sys.stdout.write(buf.decode('utf-8', 'ignore'))
print('\n=== ПРИГЛАШЕНИЙ ОТВЕЧЕНО: %d/%d ===' % (sent, len(ANSWERS)),
      file=sys.stderr)
