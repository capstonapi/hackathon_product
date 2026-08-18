# AI and RAG

Questions are deterministically routed by intent. Historical questions use article, vector, entity-graph, and external retrieval; simple definitions use official/reference retrieval. Documents are deduplicated and ranked by relevance and centralized source trust.

Conversation context is restricted to the current article and six recent messages. Prompts instruct the model to treat retrieved content as untrusted evidence, never instructions. If Gemini fails, the service returns retrieved evidence or clearly states that reliable context was unavailable.
