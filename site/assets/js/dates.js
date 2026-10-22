
  (function ($) {
    if (!$) {
      return;
    }
    var monthNames = document.documentElement.lang === "zh-CN" ? ["1月","2月","3月","4月","5月","6月","7月","8月","9月","10月","11月","12月"] : ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
    function getMonthAbbr(month) {
      var monthIndex;
      if (!month) {
        return "";
      }
      if (isNaN(parseInt(month, 10))) {
        return month;
      }
      monthIndex = parseInt(month, 10) - 1;
      return monthNames[monthIndex] || month;
    }
    function buildRibbon(year, month, day, yearClass) {
      return $("<time>")
        .addClass("date-as-calendar inline-flex size0_6x")
        .append($("<span>").addClass("day").text(day || ""))
        .append($("<span>").addClass("month").text(getMonthAbbr(month)))
        .append($("<span>").addClass(yearClass || "year").text(year || ""));
    }
    window.reload_time = function () {
      $(".date-ul.tbc li").each(function () {
        var $item = $(this);
        var $em = $item.find("em").first();
        var parts;
        var dateText;
        var contentText;
        var container;
        if ($item.data("dateEnhanced") || !$em.length) {
          return;
        }
        dateText = $em.text();
        parts = dateText.split(".");
        contentText = $item.html().replace($em.prop("outerHTML"), "").replace(/^\s*-\s*/, "").trim();
        container = $("<div>")
          .addClass("container")
          .append(buildRibbon(parts[0], parts[1], parts[2], "year"))
          .append($("<div>").addClass("content-div").html(contentText));
        $item.html(container).data("dateEnhanced", true);
      });
    };
    window.reload_time2 = function () {
      $(".date-ul.tbc2 li").each(function () {
        var $item = $(this);
        var $emElements = $item.find("em");
        var parts1;
        var parts2;
        var contentText;
        var container;
        if ($item.data("dateEnhanced") || $emElements.length !== 2) {
          return;
        }
        parts1 = $emElements.first().text().split(".");
        parts2 = $emElements.last().text().split(".");
        contentText = $item.html()
          .replace($emElements.first().prop("outerHTML"), "")
          .replace($emElements.last().prop("outerHTML"), "")
          .replace(/^\s*-\s*/, "")
          .trim();
        container = $("<div>")
          .addClass("container")
          .append(buildRibbon(parts1[0], parts1[1], parts1[2], "year"))
          .append("<div style='width: 10px; text-align: center;'> - </div>")
          .append(buildRibbon(parts2[0], parts2[1], parts2[2], "year2"))
          .append($("<div>").addClass("content-div").html(contentText));
        $item.html(container).data("dateEnhanced", true);
      });
    };
    $(function () {
      window.reload_time();
      window.reload_time2();
    });
  })(window.jQuery);
