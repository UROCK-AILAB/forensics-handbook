// 목차에서 잘린 제목을 마우스를 올리면 전체로 보여 준다.
(function () {
    function addTitles() {
        document.querySelectorAll('.chapter a, .chapter-link-wrapper > span').forEach(function (el) {
            if (!el.title) el.title = el.textContent.trim();
        });
    }
    document.addEventListener('DOMContentLoaded', function () {
        addTitles();
        var box = document.querySelector('mdbook-sidebar-scrollbox');
        if (box) new MutationObserver(addTitles).observe(box, { childList: true, subtree: true });
    });
})();
