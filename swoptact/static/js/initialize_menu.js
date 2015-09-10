$(document).ready(function () {
    $("#user-menu").menu();
    $("#user-menu").hide();
    $("#user-menu-link img").on("click", function() { $("#user-menu").toggle(); });
    $("#user-menu").on("mouseleave", function() { $("#user-menu").hide(); });
});
