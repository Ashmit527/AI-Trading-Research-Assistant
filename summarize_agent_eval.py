import json

with open("data/evaluation/agent_eval_results.json", "r", encoding="utf-8") as f:
    results = json.load(f)

total = len(results)
correct_tools = sum(1 for r in results if r.get("correct_tools_used") == True)
correct_answers = sum(1 for r in results if r.get("answer_correct") == True)
duplicate_issues = sum(1 for r in results if r.get("unnecessary_duplicate_calls") == True)
unsupported_claims = sum(1 for r in results if r.get("unsupported_claims_present") == True)

print(f"Total questions: {total}")
print(f"Correct tool selection: {correct_tools}/{total} ({100*correct_tools/total:.0f}%)")
print(f"Correct final answer: {correct_answers}/{total} ({100*correct_answers/total:.0f}%)")
print(f"Questions with duplicate/redundant calls: {duplicate_issues}/{total}")
print(f"Questions with unsupported claims: {unsupported_claims}/{total}")