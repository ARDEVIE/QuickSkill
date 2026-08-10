(function () {
    function getCookie(name) {
        const match = document.cookie.match(new RegExp("(^|; )" + name + "=([^;]*)"));
        return match ? decodeURIComponent(match[2]) : null;
    }

    function setToggleIcon(button, theme) {
        button.textContent = theme === "dark" ? "☀️" : "🌙";
        button.setAttribute("aria-label", theme === "dark" ? "Включить светлую тему" : "Включить тёмную тему");
    }

    document.addEventListener("DOMContentLoaded", function () {
        const toggle = document.querySelector("[data-theme-toggle]");
        if (!toggle) {
            return;
        }

        const root = document.documentElement;
        setToggleIcon(toggle, root.getAttribute("data-theme"));

        toggle.addEventListener("click", function () {
            const nextTheme = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
            const themeUrl = toggle.getAttribute("data-theme-url");

            if (!themeUrl) {
                return;
            }

            fetch(themeUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: "theme=" + encodeURIComponent(nextTheme),
            })
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
                    if (data.ok) {
                        root.setAttribute("data-theme", data.theme);
                        setToggleIcon(toggle, data.theme);
                    }
                })
                .catch(function () {
                    /* theme sync is non-critical, ignore network errors */
                });
        });
    });
})();
