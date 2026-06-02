import yaml
import sys
import subprocess
from pathlib import Path


def convert_rmd_files(convert_script: str = "convert.py") -> None:
    """Convert all .Rmd files to .qmd with underscore prefix."""
    
    for rmd_file in Path('.').glob('*.Rmd'):
        qmd_file = f"_{rmd_file.stem}.qmd"
        print(f"Converting {rmd_file} → {qmd_file}")
        subprocess.run(['python', convert_script, str(rmd_file), qmd_file])
    
    print("✓ Conversion complete!")


def generate_index_qmd(yaml_file: str, output_file: str = "index.qmd") -> None:
    """Generate index.qmd from a YAML chapter file."""
    
    with open(yaml_file, 'r') as f:
        config = yaml.safe_load(f)
    
    title = config.get('title', 'Untitled')
    content_items = config.get('content', [])
    
    lines = [f"# {title}", ""]
    
    for item in content_items:
        if item.get('type') == 'text':
            src = item.get('src')
            if src:
                # Replace .Rmd with .qmd and add underscore prefix
                qmd_file = src.replace('.Rmd', '.qmd')
                qmd_file = f"_{qmd_file}"
                lines.append(f"{{{{< include {qmd_file} >}}}}")
                lines.append("")
    
    with open(output_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ {output_file} created successfully!")


def main():
    convert_script = sys.argv[1] if len(sys.argv) > 1 else "convert.py"
    yaml_file = sys.argv[2] if len(sys.argv) > 2 else "_chapter.yml"
    
    print("=" * 50)
    print("Step 1: Converting Rmd files to Qmd")
    print("=" * 50)
    convert_rmd_files(convert_script)
    
    print("\n" + "=" * 50)
    print("Step 2: Generating index.qmd")
    print("=" * 50)
    generate_index_qmd(yaml_file)
    
    print("\n" + "=" * 50)
    print("All done!")
    print("=" * 50)


if __name__ == "__main__":
    main()
