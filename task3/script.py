import re
import sys

def extract_mapped_percentage(file_content):
    lines = file_content.strip().split('\n')
    
    for line in lines:
        if 'mapped' in line and '%' in line:
        
            match = re.search(r'\((\d+\.\d+)%', line)
            if match:
                return float(match.group(1))
    return None


def main():
    output = sys.stdin.read()

    percentage = extract_mapped_percentage(output)

    if percentage is None:
        print("Error: No mapped percentage found", file=sys.stderr)
        return

    if percentage < 90:
        print(f"NOT OK, percentage = {percentage}", file=sys.stderr)
        return

    print("OK")

if __name__ == "__main__":
    main()
