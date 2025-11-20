import csv
import json
import os
import hashlib

def get_prompts():
    prompts = []
    # List all directories
    for root, dirs, files in os.walk("."):
        if "prompts.csv" in files:
            category = os.path.basename(root)
            filepath = os.path.join(root, "prompts.csv")

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Clean up keys (remove whitespace)
                        row = {k.strip(): v for k, v in row.items() if k}

                        if 'prompt' not in row:
                            continue

                        prompt_text = row.get('prompt', '').strip()
                        if not prompt_text:
                            continue

                        # Generate a stable ID for the prompt based on its content
                        prompt_id = hashlib.md5(prompt_text.encode('utf-8')).hexdigest()

                        prompts.append({
                            "id": prompt_id,
                            "category": category,
                            "prompt": prompt_text,
                            "contributor": row.get('contributor', '').strip(),
                            "comment": row.get('comment', '').strip()
                        })
            except Exception as e:
                print(f"Error processing {filepath}: {e}")

    return prompts

def main():
    prompts = get_prompts()
    output_dir = "docs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(os.path.join(output_dir, "prompts.json"), "w", encoding='utf-8') as f:
        json.dump(prompts, f, indent=2)

    print(f"Generated {len(prompts)} prompts in docs/prompts.json")

if __name__ == "__main__":
    main()
