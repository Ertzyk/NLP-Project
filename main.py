import argparse
from src.stats.runner import run_stats
from src.syntax.runner import run_syntax


def main() -> None:
    parser = argparse.ArgumentParser(description = "NLP Project CLI")
    parser.add_argument("--part", type = int, choices = [1, 2, 3], default = 1,
                        help = "1: Statistical analysis | 2: SVO generator | 3: Kohonen SOM")
    args = parser.parse_args()

    if args.part == 1:
        run_stats()
    elif args.part == 2:
        run_syntax()
    elif args.part == 3:
        raise NotImplementedError("Part 3 (Kohonen SOM semantics) not implemented yet.")


if __name__ == "__main__":
    main()