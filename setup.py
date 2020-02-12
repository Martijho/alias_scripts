from pathlib import Path


LOCAL_BASHRC = '.bashrc_autogen_alias'


def to_alias_line(name, script):
    return f'alias {name}=\"python {script}\"'


def get_alias_name(script):
    lines = Path(script).open('r').read().split('\n')
    override = None
    alias_name = None

    for l in lines:
        if l.startswith('ALIAS_NAME = '):
            alias_name = l.replace('ALIAS_NAME = ', '').strip()
        if l.startswith('ALIAS_OVERRIDE = '):
            override = l.replace('ALIAS_OVERRIDE = ', '').strip()

    if alias_name is None:
        raise ValueError(f'{script} does not have ALIAS_NAME')

    return alias_name, override


if __name__ == '__main__':
    scripts = Path('scripts').glob('*.py')
    root = Path.cwd()

    lines = []
    for script in scripts:
        script = root / script
        name, override = get_alias_name(script)
        print(f'\t-> Adding {script.name} as {name}')
        if override is not None:
            print(f'\t\t -> over riding alias with {override}')
            lines.append(override.replace('<PATH>', str(script)).replace('\'', ''))
        else:
            lines.append(to_alias_line(name, script))

    Path(LOCAL_BASHRC).open('w').write('\n'.join(lines))
    (Path.home() / '.bashrc_alias').open('a').write(f'\n# Autogen alias\nsource {root / LOCAL_BASHRC}\n')