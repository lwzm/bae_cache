// Generated by CoffeeScript 1.11.1
(function() {
  $("ul li a").one("mouseover", function() {
    var $a;
    $a = $(this);
    return $.ajax({
      url: location.pathname + "?type=repr",
      type: "POST",
      data: $a.attr("href").slice(1),
      success: function(data) {
        return $a.attr("title", data);
      }
    });
  });

}).call(this);
