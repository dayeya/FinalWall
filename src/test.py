from src.waf_err import AttackDetected


def main():
    b = False
    assert b, AttackDetected


if __name__ == "__main__":
    main()