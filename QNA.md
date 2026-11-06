
---

## Q1. What is the difference between Machine Learning, Deep Learning, and Generative AI?

These are nested concepts, each a narrower subset of the previous one.

**Machine Learning (ML)** is the broad field where systems learn patterns from data instead of following hand-written rules. It includes linear regression, decision trees, SVMs, random forests and clustering. These methods usually work well on structured, tabular data and often need manual feature engineering.
*Example: predicting loan defaults, spam detection.*

**Deep Learning (DL)** is a subset of ML that uses multi-layer neural networks (CNNs, RNNs, Transformers). Its key strength is automatic feature learning from raw data like images, audio and text, so it needs less manual feature engineering. The trade-off is that it requires large datasets and significant compute (GPUs).
*Example: face recognition, speech-to-text.*

**Generative AI (GenAI)** is a subset of DL focused on *creating* new content (text, images, code, audio) rather than just classifying or predicting. It learns the underlying distribution of training data and samples from it.
*Examples: LLMs (GPT, Claude), diffusion models (Stable Diffusion), GANs.*

**Key difference in output:** Traditional ML/DL are mostly *discriminative* (e.g., "Is this email spam?"), while GenAI is *generative* (e.g., "Write this email").

**In short:** `AI ⊃ ML ⊃ DL ⊃ GenAI`

| Aspect | Machine Learning | Deep Learning | Generative AI |
|---|---|---|---|
| Scope | Broad field | Subset of ML | Subset of DL |
| Typical models | Decision trees, SVM, regression | CNN, RNN, Transformer | LLMs, diffusion models, GANs |
| Data needs | Small to medium | Large | Very large |
| Output | Predictions / classes | Predictions / classes | New content |

---

## Q2. How would you reduce hallucinations in an AI chatbot?

Hallucinations happen because LLMs predict plausible text, not verified truth. I would use a layered approach:

1. **Retrieval-Augmented Generation (RAG):** Ground answers in a trusted knowledge base. Retrieve relevant documents and instruct the model to answer only from that context.
2. **Prompt design:** Tell the model to say "I don't know" when context is insufficient, and to avoid guessing.
3. **Citations:** Require the bot to cite sources so claims are traceable and verifiable.
4. **Lower temperature:** Reduces randomness and creative drift for factual tasks.
5. **Verification layer:** Use a second pass or guardrail model to check the answer against retrieved sources (groundedness check).
6. **Tool use:** Delegate calculations, database lookups and live data to APIs instead of relying on model memory.
7. **Fine-tuning:** Train on high-quality, domain-specific data, including examples of correct refusals.
8. **Evaluation and monitoring:** Build test sets, track hallucination rate, collect user feedback, and use human review for high-stakes domains.
9. **Output constraints:** Use structured outputs (JSON schemas) to limit free-form fabrication.

> Combining RAG, grounding checks and clear abstention behavior gives the biggest improvement.

---

## Q3. If an AI model gives biased predictions, how would you detect and reduce the bias?

### Detection

1. **Audit the data:** Check representation across groups (gender, age, region, etc.), label quality and historical bias.
2. **Disaggregated evaluation:** Measure accuracy, precision, recall and false positive/negative rates *per subgroup*, not just overall.
3. **Fairness metrics:** Demographic parity, equalized odds, equal opportunity, and disparate impact ratio.
4. **Tools:** Fairlearn, AIF360, What-If Tool; use SHAP/LIME to see if sensitive attributes or proxies (e.g., zip code) drive predictions.
5. **Counterfactual testing:** Change only a sensitive attribute and check whether the prediction changes.

### Reduction

1. **Pre-processing:** Rebalance or resample data, reweight samples, collect more data for underrepresented groups, and fix biased labels.
2. **In-processing:** Add fairness constraints or regularization to the loss function; use adversarial debiasing.
3. **Post-processing:** Adjust decision thresholds per group or recalibrate outputs.
4. **Remove proxies:** Drop or transform features that correlate with sensitive attributes.
5. **Governance:** Diverse review teams, documentation (model cards), human oversight, and continuous monitoring after deployment, since bias can reappear as data drifts.