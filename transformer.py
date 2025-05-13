import os
import json
import spacy
from spacy.matcher import Matcher

# --- Global Setup ---
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

action_keywords = {"add", "create", "remove", "move", "delete", "extract"}
language_elements = {"method", "class", "field", "parameter", "variable"}
rules = []


def load_rules_from_directory(path="rules"):
    all_rules = []
    for filename in os.listdir(path):
        if filename.endswith(".json"):
            with open(os.path.join(path, filename), "r", encoding="utf-8") as f:
                try:
                    all_rules.extend(json.load(f))
                except json.JSONDecodeError as e:
                    print(f"Error in {filename}: {e}")
    return all_rules


def register_rules(rules):
    for rule in rules:
        matcher.add(rule["label"], rule["patterns"])


def process_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line or not line[0].isdigit():
                continue
            content = line.split('.', 1)[1].strip()
            print(f"\n🔹 Step: {line}")
            transform_definitions(content)


def check_for_potential_new_microstep(doc):
    lemmas = [token.lemma_.lower() for token in doc]

    matched_actions = {word for word in lemmas if word in action_keywords}
    matched_elements = {elem for elem in lemmas if elem in language_elements}

    if matched_actions and matched_elements:
        print("Matched rule: PotentialNewMicrostep")
        print(f"  → Matched action(s): {', '.join(matched_actions)}")
        print(f"  → Matched language element(s): {', '.join(matched_elements)}")
        print(f"  → Trigger: PotentialNewMicrostep (PNM)")
    else:
        print("No known or potential microstep match.")


def transform_definitions(text):
    doc = nlp(text)
    matches = matcher(doc)

    if matches:
        for match_id, start, end in matches:
            rule_name = nlp.vocab.strings[match_id]
            span = doc[start:end]

            # Get the rule dict by matching the label
            rule = next((r for r in rules if r["label"] == rule_name), None)

            print(f"\nMatched rule: {rule_name}")
            print(f"  → Matched phrase: '{span.text}'")
            print(f"  → Trigger: {rule_name}")
            print(f"  → Check Risks: {', '.join(rule['risks'])}")

            return  # stop after first match
    else:
        check_for_potential_new_microstep(doc)


def read_definitions(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line or not line[0].isdigit():
                continue  # skip empty or unnumbered lines

            content = line.split('.', 1)[1].strip()
            print(f"\n▪️ Step: {line}")
            transform_definitions(content)


# Example usage
if __name__ == "__main__":
    rules = load_rules_from_directory("rules")
    register_rules(rules)
    read_definitions("input/pull-up-method.txt")
    #read_definitions("input/replace-inheritance-with-delegation.txt")
