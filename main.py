import Dodger1
import Dodger0

def main():
    mode = 0
    if mode == 1:
        dodger = Dodger1()
    else:
        dodger = Dodger0()
    dodger.run()


if __name__ == '__main__':
    main()
