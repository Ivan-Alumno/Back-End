document.addEventListener('DOMContentLoaded', () => {
    const password = document.getElementById('id_password1');
    const confirmation = document.getElementById('id_password2');
    if (!password || !confirmation) {
        return;
    }

    const rules = {
        length: document.querySelector('[data-password-rule="length"]'),
        numeric: document.querySelector('[data-password-rule="numeric"]'),
        match: document.querySelector('[data-password-rule="match"]'),
    };

    const updateRule = (rule, isValid) => {
        if (!rule) {
            return;
        }
        rule.classList.toggle('is-met', isValid);
        rule.classList.toggle('is-unmet', !isValid);
    };

    const updatePasswordFeedback = () => {
        const value = password.value;
        const confirmationValue = confirmation.value;
        const passwordsMatch = confirmationValue.length > 0 && confirmationValue === value;

        updateRule(rules.length, value.length >= 8);
        updateRule(rules.numeric, value.length > 0 && !/^\d+$/.test(value));
        updateRule(rules.match, passwordsMatch);
        rules.match.textContent = passwordsMatch
            ? rules.match.dataset.messageMatch
            : confirmationValue.length > 0
                ? rules.match.dataset.messageMismatch
                : rules.match.dataset.messagePending;
    };

    password.addEventListener('input', updatePasswordFeedback);
    confirmation.addEventListener('input', updatePasswordFeedback);
    updatePasswordFeedback();
});
