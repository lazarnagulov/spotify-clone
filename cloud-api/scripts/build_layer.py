import shutil
import subprocess
import sys
from pathlib import Path

def run_cmd(cmd, check=True):
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError as e:
        if check:
            raise
        return False

def build_layer(layer_name: str):
    base_dir = Path(__file__).resolve().parent.parent

    layer_dir = base_dir / "layers" / layer_name
    python_dir = layer_dir / "python"

    if not python_dir.exists():
        print(f"Folder {python_dir} not found.")
        sys.exit(1)

    requirements_file = python_dir / "requirements.txt"
    build_path = base_dir / ".build" / f"{layer_name}_build"
    zip_path = base_dir / ".build" / f"{layer_name}.zip"

    shutil.rmtree(build_path, ignore_errors=True)
    zip_path.unlink(missing_ok=True)
    build_path.mkdir(parents=True, exist_ok=True)

    site_packages_path = build_path / "python"
    site_packages_path.mkdir(parents=True, exist_ok=True)

    for item in python_dir.iterdir():
        if item.name != "requirements.txt":
            dest = site_packages_path / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

    if requirements_file.exists():
        print(f"📦 Installing dependencies from {requirements_file}...")

        native_cmd = [
            sys.executable, "-m", "pip", "install",
            "-r", str(requirements_file),
            "-t", str(site_packages_path),
            "--platform", "manylinux2014_x86_64",
            "--only-binary=:all:",
            "--upgrade",
            "--implementation", "cp",
            "--python-version", "3.11"
        ]

        if not run_cmd(native_cmd, check=False):
            print("Native pip install failed, falling back to Docker-based build...")

            docker_cmd = [
                "docker", "run", "--rm",
                "-v", f"{build_path}:/lambda/opt",
                "-v", f"{requirements_file}:/tmp/requirements.txt",
                "public.ecr.aws/sam/build-python3.11",
                "pip", "install",
                "-r", "/tmp/requirements.txt",
                "-t", "/lambda/opt/python"
            ]

            run_cmd(docker_cmd)

    shutil.make_archive(zip_path.with_suffix(''), 'zip', build_path)
    print(f"✅ Layer '{layer_name}' zipped successfully at: {zip_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build_layer.py <layer_name>")
        sys.exit(1)

    build_layer(sys.argv[1])
