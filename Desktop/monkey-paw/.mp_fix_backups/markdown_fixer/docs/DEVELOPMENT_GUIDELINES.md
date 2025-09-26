# Development Guidelines & Best Practices






## Core Principles






### Improvement Philosophy






- **Never remove functionality** from the application - we only add things to make it better






- **Never delete** anything in the "do not delete" sections of the app






- **All improvements must be totally free** - no paid services or free trials






- Always bias towards **not asking the user for help** if you can find the answer yourself






## Code Change Guidelines

**CRITICAL**: When making code changes, **NEVER output code to the USER** unless specifically requested. Always use code edit tools to implement changes.






### Code Quality Standards






1. **Add all necessary dependencies**: Include import statements, dependencies, and endpoints required to run the code immediately






2. **Complete project setup**: If creating from scratch, include:






   - Appropriate dependency management file (e.g., requirements.txt) with versions






   - Helpful README with setup instructions






3. **Modern UI/UX**: For web apps, create beautiful, modern interfaces with best UX practices






4. **No binary/hash generation**: Never generate extremely long hashes or non-textual code






5. **Read before editing**: Unless making small edits or creating new files, always read the contents/section before editing






6. **Fix linter errors**: Address clear linting issues, but don't make uneducated guesses. Stop after 3 attempts and ask user for guidance






7. **Retry failed edits**: If a reasonable code edit wasn't applied, try reapplying it






## Debugging Guidelines

Only make code changes when certain you can solve the problem. Otherwise:






1. **Address root cause**, not symptoms






2. **Add descriptive logging** and error messages to track state






3. **Create test functions** to isolate problems






4. **Gather more information** before making changes if unsure






## External API Guidelines






1. **Use best-suited APIs/packages** without asking permission unless explicitly requested otherwise






2. **Version compatibility**: Choose versions compatible with existing dependency files, or latest stable if none exists






3. **API Key security**: Always point out when API keys are needed and follow security best practices (never hardcode keys in exposed locations)






## Workflow Standards






- **Gather information** before responding if the request isn't fully clear






- **Use multiple tools** if needed to complete tasks thoroughly






- **Don't end your turn** if you're not confident about partial solutions - gather more info or use more tools






- **Implement changes directly** using edit tools rather than showing code






## Quality Assurance






- **Test immediately**: All generated code must be runnable immediately






- **Complete solutions**: Don't provide partial implementations without completing the full request






- **Security first**: Always consider security implications, especially with external services






- **Documentation**: Include clear setup and usage instructions

---

*These guidelines ensure consistent, high-quality development that prioritizes user experience, security, and immediate functionality.*
