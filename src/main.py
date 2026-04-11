from gamma import Gamma


def main():
    proxy = Gamma(host='0.0.0.0', port=25565)
    proxy.start()


if __name__ == '__main__':
    main()