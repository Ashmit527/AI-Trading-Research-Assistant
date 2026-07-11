import json

with open("data/evaluation/eval_results.json", "r", encoding="utf-8") as f:
    results = json.load(f)

total = len(results)

# --- Core accuracy stats ---
retrieval_ok = sum(1 for r in results if r.get("retrieval_correct") == True)
answer_ok = sum(1 for r in results if r.get("answer_correct") == True)
citation_ok = sum(1 for r in results if r.get("citation_correct") == True)

print(f"Total questions: {total}")
print(f"Retrieval accuracy: {retrieval_ok}/{total} ({100*retrieval_ok/total:.0f}%)")
print(f"Answer accuracy: {answer_ok}/{total} ({100*answer_ok/total:.0f}%)")
print(f"Citation accuracy: {citation_ok}/{total} ({100*citation_ok/total:.0f}%)")

# --- Declined-to-answer breakdown ---
declined_on_real_questions = sum(
    1 for r in results
    if r.get("model_declined_to_answer") == True and r.get("type") != "trap"
)
declined_on_trap_questions = sum(
    1 for r in results
    if r.get("model_declined_to_answer") == True and r.get("type") == "trap"
)
answered_trap_questions = sum(
    1 for r in results
    if r.get("model_declined_to_answer") == False and r.get("type") == "trap"
)

print("\n--- Decline-to-answer breakdown ---")
print(f"Declined on real (answerable) questions: {declined_on_real_questions}  <- likely retrieval or generation failure")
print(f"Declined on trap questions (correctly): {declined_on_trap_questions}  <- good, grounding working")
print(f"Answered trap questions anyway (hallucination risk): {answered_trap_questions}  <- bad, check these closely")

# --- Cross-tab: retrieval_correct vs model_declined_to_answer ---
retrieval_ok_but_declined = sum(
    1 for r in results
    if r.get("retrieval_correct") == True and r.get("model_declined_to_answer") == True
)
retrieval_failed_and_declined = sum(
    1 for r in results
    if r.get("retrieval_correct") == False and r.get("model_declined_to_answer") == True
)
retrieval_failed_but_answered = sum(
    1 for r in results
    if r.get("retrieval_correct") == False and r.get("model_declined_to_answer") == False
)

print("\n--- Failure diagnosis (for declined/no-answer cases) ---")
print(f"Retrieval correct, but model declined anyway (generation problem): {retrieval_ok_but_declined}")
print(f"Retrieval failed, model correctly declined (expected honesty): {retrieval_failed_and_declined}")
print(f"Retrieval failed, but model answered anyway (hallucination risk): {retrieval_failed_but_answered}")

# --- List specific failures for manual review ---
print("\n--- Answer failures (answer_correct == False) ---")
for r in results:
    if r.get("answer_correct") == False:
        print(f"Q{r['id']} ({r['type']}): {r['question']}")

print("\n--- Citation failures (citation_correct == False) ---")
for r in results:
    if r.get("citation_correct") == False:
        print(f"Q{r['id']} ({r['type']}): {r['question']}")

print("\n--- Cases where model declined on a real (non-trap) question ---")
for r in results:
    if r.get("model_declined_to_answer") == True and r.get("type") != "trap":
        print(f"Q{r['id']}: {r['question']}  | retrieval_correct={r.get('retrieval_correct')}")