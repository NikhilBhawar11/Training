# GadKille – Prompt Comparison Evaluation

## Objective
Compare two prompt versions to evaluate answer quality, accuracy, relevance, and response consistency.

## Prompt Version A – Basic Prompt

You are a Maharashtra forts assistant. Answer the user's questions about forts in simple language. Provide useful information and avoid unnecessary details.

## Prompt Version B – Improved Prompt

You are GadKille, an AI assistant specializing in Maharashtra forts.

Instructions:
- Answer only using reliable information.
- Focus on fort history, location, trekking difficulty, height, and base village.
- Never invent missing information.
- If information is unavailable, clearly state that.
- Give concise and structured answers.
- Ask a relevant follow-up question when useful.
- Prioritize trekking safety.
- Return answers in the required JSON format.

## Evaluation Questions

1. Tell me about Raigad Fort.
2. Which district is Sinhagad Fort located in?
3. What is the historical importance of Shivneri Fort?
4. Where is Harishchandragad Fort located?
5. Explain the trekking difficulty of Rajgad Fort.
6. Which village is the base village for Torna Fort?
7. What is the height of Pratapgad Fort?
8. Recommend forts in Pune district.
9. Which forts are suitable for beginner trekkers?
10. What is the current population of Raigad Fort?

Question 10 is intentionally outside the available GadKille dataset.

## Evaluation Criteria

| Criteria | Description |
|---|---|
| Accuracy | Is the answer factually correct? |
| Relevance | Does it answer the question? |
| Completeness | Does it cover important details? |
| Hallucination | Does it invent missing information? |
| Clarity | Is the answer easy to understand? |

## Comparison Table

| Question | Version A | Version B | Better Version |
|---|---|---|---|
| Q1 | Correct location; no JSON format | Correct location; valid JSON | B |
| Q2 | Correct district; plain text | Correct district; valid JSON | B |
| Q3 | Correctly identifies missing historical information | Correctly identifies missing information and provides follow-up | B |
| Q4 | Correctly identifies Ahmednagar district | Correctly identifies Ahmednagar district in JSON | B |
| Q5 | Correctly states trekking difficulty is unavailable | Clearly explains missing information and gives follow-up | B |
| Q6 | Correctly identifies missing base village | Correctly identifies missing base village and gives follow-up | B |
| Q7 | Correctly identifies missing height | Correctly identifies missing height in JSON | B |
| Q8 | Provides three Pune forts with extra unsupported description | Provides three forts in a structured response | B |
| Q9 | Correctly states beginner suitability cannot be determined | Clearly explains missing difficulty information | B |
| Q10 | Correctly states population data is unavailable | States data is unavailable but adds an unsupported general statement | A |

## Conclusion

Version B performs better overall because it produces structured JSON responses, includes follow-up questions, and handles unavailable information consistently.

However, both versions depend on the same retrieved dataset. Missing fort details remain a limitation of the current knowledge base.

## Final Evaluation Summary

### Evaluation Method

Both prompt versions were tested using the same 10 questions and identical retrieved context for each question.

### Scoring System

| Score | Meaning |
|---|---|
| 1 | Poor |
| 2 | Below Average |
| 3 | Average |
| 4 | Good |
| 5 | Excellent |

### Overall Comparison

| Evaluation Criteria | Version A | Version B |
|---|---:|---:|
| Accuracy | 4 | 4 |
| Relevance | 4 | 5 |
| Completeness | 3 | 4 |
| Hallucination Control | 4 | 4 |
| Clarity | 4 | 5 |
| **Total** | **19/25** | **22/25** |

### Final Conclusion

Version B is selected as the preferred prompt.

It provides more consistent JSON output, better response structure, useful follow-up questions, and clearer handling of missing information.

Further improvements are needed in the GadKille dataset to provide historical information, trekking difficulty, fort height, and base village details.

The evaluation was conducted manually by comparing the generated responses. The scores represent qualitative assessment rather than automated factual verification.
