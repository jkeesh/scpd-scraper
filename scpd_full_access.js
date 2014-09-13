// Much inspiration from http://izaakschroeder.wordpress.com/2012/01/31/lucidchart-javascript-breaking-limits-with-ajax-hijacking/
(function() {
  var _send = XMLHttpRequest.prototype.send;

  /**
   * Modifies the response of the ajax request to give full access to the user.
   * Note that `this` is the XMLHttpRequest instance.
   */
  function giveFullAccess() {
    try {
      var json = JSON.parse(this.response);
    } catch(e) {
      // Response was not JSON, so we don't care about it
      return;
    }

    // Set our access to FullAccess
    json["CourseAccessStatus"] = "FullAccess";
    json = JSON.stringify(json);

    // `response` and `responseText` are read-only, but this trick lets
    // us override them. Even though it seems we are creating a property,
    // `defineProperty` lets us modify existing properties, too.
    Object.defineProperty(this, "response", {
      get: function() {
        return json;
      }
    });

    Object.defineProperty(this, "responseText", {
      get: function() {
        return json;
      }
    });
  }

  /**
   * `onreadystatechange` is a property, so it's not accessible
   * on the prototype directly. This means we need to modify it
   * inside a prototype method. We do this in `send` (as opposed
   * to `open`) because Angular (which SCPD uses) sets this method
   * *after* the call to `open`, but *before* the call to `send`.
   */
  XMLHttpRequest.prototype.send = function() {
    var _onreadystatechange = this.onreadystatechange;

    this.onreadystatechange = function() {
      // Checking for "CourseAccessStatus" in the string is a simple way of
      // seeing if this is a response we want to modify.
      if (this.response.indexOf("CourseAccessStatus") != -1) {
        giveFullAccess.call(this);
      }

      return _onreadystatechange.apply(this, arguments);
    }

    return _send.apply(this, arguments);
  };
})();
