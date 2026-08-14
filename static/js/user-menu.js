(function () {
    document.addEventListener('DOMContentLoaded', function () {
        var toggle = document.querySelector('[data-user-menu-toggle]');
        var dropdown = document.querySelector('[data-user-menu-dropdown]');
        if (!toggle || !dropdown) {
            return;
        }

        function close() {
            dropdown.classList.remove('is-open');
            toggle.setAttribute('aria-expanded', 'false');
        }

        toggle.addEventListener('click', function (event) {
            event.stopPropagation();
            var isOpen = dropdown.classList.toggle('is-open');
            toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });

        document.addEventListener('click', function (event) {
            if (!dropdown.contains(event.target) && event.target !== toggle) {
                close();
            }
        });

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') {
                close();
            }
        });
    });
})();
