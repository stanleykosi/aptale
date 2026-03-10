Use `query_user_context` to fetch additive user-model context from Honcho.

Focus your query on:
- preferred communication style (concise vs detailed)
- desired brevity for the current response
- relevant business priorities/goals for current trade decisions

Do not use Honcho to set or overwrite operational settings.
Operational settings remain canonical in USER.md:
- local currency
- default profit margin
- timezone
- preferred routes

Return context that can be applied immediately to response tone and detail level.
Do not include raw invoice numbers, supplier names, or item-level pricing details.
