from pathlib import Path


LOCAL_BASHRC = '.bashrc_autogen_alias'


def to_alias_line(name, script):
    return f'alias {name}=\"python {script}\"'


def get_alias_name(script):
    lines = Path(script).open('r').read().split('\n')
    for l in lines:
        if l.startswith('ALIAS_NAME = '):
            return l.replace('ALIAS_NAME = ', '').strip()
    raise ValueError(f'{script} does not have ALIAS_NAME')


if __name__ == '__main__':
    scripts = Path('scripts').glob('*.py')
    root = Path.cwd()

    lines = []
    for script in scripts:
        script = root / script
        name = get_alias_name(script)
        print(f'\t-> Adding {script.name} as {name}')
        lines.append(to_alias_line(name, script))

    Path(LOCAL_BASHRC).open('w').write('\n'.join(lines))
    (Path.home() / '.bashrc_alias').open('a').write(f'\n# Autogen alias\nsource {root / LOCAL_BASHRC}\n')