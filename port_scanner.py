import socket
import threading


def start(func_name):
    global start_port, end_port
    if default_ports:
        start_port, end_port = 1, 10000
    threads = []
    for port in range(start_port, end_port + 1):
        t = threading.Thread(target=func_name, args=(host, port))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()


def get_applied_protocol(port, protocol):
    try:
        applied_protocol_name = socket.getservbyport(port, protocol).upper()
    except Exception:
        return ''
    else:
        return applied_protocol_name


def TCP_scan(host_ip, port):
    # Не всё показывает: соединение через connect
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        if s.connect_ex((host_ip, port)):
            pass
        else:
            applied_protocol = get_applied_protocol(port, 'tcp')
            with locker:
                print('TCP', port, applied_protocol)


def UDP_scan(host_ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as udp_socket:
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as icmp_socket:
            try:
                icmp_msg = "ping"
                udp_socket.sendto(icmp_msg.encode('utf-8'), (host_ip, port))
                icmp_socket.settimeout(1)
                icmp_socket.recvfrom(1024)
            except socket.timeout:
                applied_protocol = get_applied_protocol(port, 'udp')
                if not applied_protocol:
                    pass
                else:
                    with locker:
                        print('UDP', port, applied_protocol)


host = input('Введите адрес хоста: ')
print(
    '\nСканирование по умолчанию от 1 до 10001',
    '-t - сканировать TCP протокол',
    '-u - сканировать UDP протокол',
    '-p N1 N2 - задать диапазон портов',
    '-e - выйти',
    sep='\n'
)

start_port, end_port = 1, 10000
default_ports = True
locker = threading.Lock()

while True:
    command = input()
    if command == '-t':
        print('Вывод открытых TCP портов:')
        start(TCP_scan)
        print('Сканирование портов завершено')
        continue
    if command == '-u':
        print('Вывод открытых UDP портов:')
        start(UDP_scan)
        print('Сканирование портов завершено')
        continue
    if command.split()[0] == '-p':
        default_ports = False
        command_flag = False
        if len(command.split()) < 3:
            print('Вы не задали диапазон портов')
            continue
        start_port, end_port = int(command.split()[1]), int(command.split()[2])
        while (start_port < 1 or start_port > 65535) or (end_port < 1 or end_port > 65535) or (start_port > end_port):
            command = input(f'Неверно задан диапазон; исправьте, введя номера от 1 до 65536, '
                            f'либо выйдите из выбора диапазона портов, нажав -a: ')
            if command == '-a':
                command_flag = True
                print('Сканирование портов вернулось в исходное состояние по умолчанию')
                break
            else:
                start_port, end_port = int(command.split()[0]), int(command.split()[1])
        if command_flag:
            default_ports = True
            continue
        print(f'Задан диапазон от {start_port} до {end_port}')
        continue
    if command == '-e':
        print('Работа программы окончена')
        break
    print('Команда не распознана')
