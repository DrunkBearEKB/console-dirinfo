import argparse
import os


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--depth', type=int, default=0, nargs='?')
    parser.add_argument('-n', '--not-tree', action='store_true')
    parser.add_argument('-i', '--info', action='store_true')

    return parser.parse_args()


def walk(directory: str, depth_max: int = -1) -> list[str]:
    list_should_be_visited = [('dir', directory, 0)]

    stat = {'Amount Files': 0,
            'Amount Directories': 0,
            'Amount Hiden Directories': 0,
            'Largest Files': list()}

    while len(list_should_be_visited) != 0:
        type_current, path_current, depth_current = \
            list_should_be_visited.pop(0)
        yield type_current, path_current, depth_current

        if os.path.isdir(path_current):
            stat['Amount Directories'] += 1
            try:
                list_dirs = os.listdir(path_current)

                list_folders = list()
                list_files = list()

                for p in list_dirs:
                    if os.path.isdir(f'{path_current}\\{p}'):
                        list_folders.append(p)
                    else:
                        list_files.append(p)

                for path in list_folders + list_files:
                    _path = f'{path_current}\\{path}'
                    if depth_current <= depth_max or depth_max == -1:
                        list_should_be_visited.insert(
                            0, ('dir' if os.path.isdir(_path) else 'file',
                                _path, depth_current + 1))

            except PermissionError:
                stat['Amount Hiden Directories'] += 1

        else:
            try:
                size = os.stat(path_current).st_size
                stat['Largest Files'].append((path_current, size))
                stat['Largest Files'].sort(key=lambda x: -x[1])
                if len(stat['Largest Files']) > 20:
                    stat['Largest Files'].pop(-1)

            except FileNotFoundError:
                pass

            stat['Amount Files'] += 1

        yield stat


def format_size(size: int) -> str:
    if size < 2 ** 10:
        return f'{size} B'
    elif size < 2 ** 20:
        return f'{round(size / 2 ** 10, 3)} KB'
    elif size < 2 ** 30:
        return f'{round(size / 2 ** 20, 3)} MB'
    elif size < 2 ** 40:
        return f'{round(size / 2 ** 30, 3)} GB'
    return f'{size} B'


def main():
    args = parse_args()

    arrow = '|---> '
    sep = ' ' * len(arrow)
    if not args.not_tree:
        print('#' * 70 + '\n'
              'Files tree:')
        for value in walk(os.getcwd(), args.depth - 1):
            try:
                if type(value) == tuple:
                    _type, path, depth = value
                    temp1 = '/' if _type == 'dir' else ''
                    temp2 = '[' + format_size(os.stat(path).st_size) + ']' \
                        if _type == 'file' else ''
                    if depth == 0:
                        print(f'{temp1 + os.path.basename(path)}')
                    else:
                        print(' ' * (depth - 1) * 6 + arrow +
                              f'{temp1 + os.path.basename(path)} '
                              f'{temp2}')
                else:
                    stat = value

            except FileNotFoundError:
                pass

    else:
        for value in walk(os.getcwd(), args.depth - 1):
            if type(value) == tuple:
                pass
            else:
                stat = value

    if args.info:
        print('#' * 70 + '\n'
              'Information:')
        for index, (k, v) in enumerate(stat.items()):
            if type(v) == list:
                print(f'{index + 1}. {k}:')
                for i, (file, size) in enumerate(v):
                    print(f'{sep}{i + 1}){" " * (2 - len(str(i + 1)))} '
                          f'{file} [{format_size(size)}]')

            else:
                print(f'{index + 1}. {k}: {v}')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
