def build_prompt(
    user_message: str,
    intent: str,
    customer_context: dict,
    rag_context: str = "",
) -> list[dict]:

    system_prompt = """You are a helpful and friendly Delta Air Lines customer assistant.
You have access to the customer's account information and Delta's official policies.
Always be polite, concise, and accurate.
If you don't know something, say so honestly — never make up information.
Always address the customer by their first name."""

    context_parts = []

    context_parts.append(
        f"Customer Information:\n"
        f"- Name: {customer_context['name']}\n"
        f"- Tier: {customer_context['tier']}\n"
        f"- Miles Balance: {customer_context['miles_balance']:,.0f} miles\n"
        f"- Member Since: {customer_context['member_since']}"
    )

    if rag_context:
        context_parts.append(f"Relevant Delta Policy Information:\n{rag_context}")

    full_context = "\n\n".join(context_parts)

    user_content = f"{full_context}\n\nCustomer Question: {user_message}"

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_content},
    ]
