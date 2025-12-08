import feast
import feast.cli
import sys

print(f"Feast version: {feast.__version__}")
print(f"Feast file: {feast.__file__}")
print(f"Feast cli dir: {dir(feast.cli)}")
print(f"Type of feast.cli: {type(feast.cli)}")

try:
    from feast.cli import cli
    print(f"Type of imported cli: {type(cli)}")
    print(f"Dir of imported cli: {dir(cli)}")
except ImportError as e:
    print(f"ImportError: {e}")
