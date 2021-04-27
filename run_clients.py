import platform
import subprocess

import click


@click.command()
@click.argument('n', default=1)
def start(n):
    if platform.system() == 'Windows':
        creation_flags = subprocess.CREATE_NEW_CONSOLE
    else:
        creation_flags = 0

    processes = []
    for i in range(n):
        processes.append(subprocess.Popen(["python", "chat_client.py", f"--username=ivanov{i}"],
                                          creationflags=creation_flags))

    while True:
        command = input('Command list:\t'
                        'q - exit\t')
        if command == 'q':
            break

    for proc in processes:
        proc.wait()


if __name__ == '__main__':

    start()
