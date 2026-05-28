import os
import subprocess
import sys
import argparse


def main(n: int):
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(repo_root)
    print(f"Running {n} iterations of pages/codingcomplete.py")
    for i in range(1, n + 1):
        print(f"--- Iteration {i} ---")
        proc = subprocess.run([sys.executable, "pages/codingcomplete.py"], capture_output=True, text=True)
        # Print captured stdout and stderr for visibility
        if proc.stdout:
            print(proc.stdout)
        if proc.returncode == 0:
            print(f"Iteration {i} succeeded")
        else:
            print(f"Iteration {i} failed with exit code {proc.returncode}")
            if proc.stderr:
                print(proc.stderr)
            sys.exit(proc.returncode)
    print("All iterations completed successfully")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('n', nargs='?', type=int, default=5, help='Number of iterations')
    args = parser.parse_args()
    main(args.n)
