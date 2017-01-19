// Generated by CoffeeScript 1.11.1
(function() {
  var $input, $output, $prompt, focus_input, history, historyPos;

  $input = $("#input");

  $output = $("#output");

  $prompt = $("#prompt");

  history = [];

  historyPos = 0;

  focus_input = function() {
    this.scroll(0, document.body.scrollHeight);
    return $input.focus();
  };

  $("html").click(function(e) {
    if (e.eventPhase === Event.AT_TARGET) {
      return focus_input();
    }
  });

  $("#submit").submit(function(e) {
    var input, txt;
    e.preventDefault();
    input = $input.val();
    txt = $output.text() + $prompt.text() + input;
    if (input && input !== history[history.length - 1]) {
      history.push(input);
    }
    historyPos = history.length;
    $prompt.text("");
    $output.text(txt);
    $.ajax({
      type: "POST",
      data: input,
      success: function(data) {
        var prompt;
        prompt = data ? ">>> " : "... ";
        $prompt.text(prompt);
        if (data !== "\n") {
          data = "\n" + data;
        }
        $output.text(txt + data);
        return focus_input();
      }
    });
    $input.val("");
    return focus_input();
  });

  $input.keydown(function(e) {
    var code;
    code = e.keyCode;
    if (code === 38 || code === 40) {
      e.preventDefault();
      if (code === 38 && historyPos > 0) {
        historyPos--;
      } else if (code === 40 && historyPos < history.length) {
        historyPos++;
      }
      return $input.val(history[historyPos]);
    }
  });

  focus_input();

}).call(this);