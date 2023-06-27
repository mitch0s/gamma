def colour_codes(data: str) -> str:
    """
    :param data: string containing data/motd with & colour codes
    :return: string formatted for Minecaft protocol
    """
    data = data.replace('&0', '\\u00A70')
    data = data.replace('&1', '\\u00A71')
    data = data.replace('&2', '\\u00A72')
    data = data.replace('&3', '\\u00A73')
    data = data.replace('&4', '\\u00A74')
    data = data.replace('&5', '\\u00A75')
    data = data.replace('&6', '\\u00A76')
    data = data.replace('&7', '\\u00A77')
    data = data.replace('&8', '\\u00A78')
    data = data.replace('&9', '\\u00A79')
    data = data.replace('&a', '\\u00A7a')
    data = data.replace('&b', '\\u00A7b')
    data = data.replace('&c', '\\u00A7c')
    data = data.replace('&d', '\\u00A7d')
    data = data.replace('&e', '\\u00A7e')
    data = data.replace('&f', '\\u00A7f')
    data = data.replace('&k', '\\u00A7k')
    data = data.replace('&l', '\\u00A7l')
    data = data.replace('&m', '\\u00A7m')
    data = data.replace('&n', '\\u00A7n')
    data = data.replace('&o', '\\u00A7o')
    data = data.replace('&r', '\\u00A7r')

    return data
