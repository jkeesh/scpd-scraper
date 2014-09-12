// Much inspiration from http://izaakschroeder.wordpress.com/2012/01/31/lucidchart-javascript-breaking-limits-with-ajax-hijacking/
var oldopen = XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function() {
  console.log("Begin custom `open`");

  // We want to give ourselves full access on all courses
  // HTML5CourseDetails is part of the url on the ajax request that fetches
  // the course details which includes user access, name, description, etc.
  if (arguments[1].indexOf("HTML5CourseDetails") != -1) {
    console.log("Fetching course details...Overriding XMLHttpRequest methods.");
    var oldsend = this.send;

    // The only reason we need to override `send` is because we also need to
    // override `onreadystatechange`. The code that sets that method is defined
    // *after* the call to `open` (this method), so to override it, it has to
    // be set here.
    this.send = function() {
      console.log("Begin custom `send`");
      var oldready = this.onreadystatechange;
      this.onreadystatechange = function() {
        console.log("Begin custom `onreadystatechange`");

        // For some reason, the first request returns an empty string as the
        // response, so just wrap this in a try/catch.
        try {
          // Set our access to FullAccess
          var json = JSON.parse(this.response);
          json["CourseAccessStatus"] = "FullAccess";
          json = JSON.stringify(json);

          // `response` and `responseText` are read-only, but this trick lets
          // us override it.

          // Also, these are deprecated now supposedly
          // (see http://stackoverflow.com/questions/6825191/what-are-definegetter-and-definesetter-functions,
          // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/__defineGetter__)
          this.__defineGetter__("response", function() {
            return json;
          });

          this.__defineGetter__("responseText", function() {
            return json;
          });
        } catch(e) {
          console.log("ERROR PARSING JSON");
          console.log(this.response);
        }
        
        console.log("End custom `onreadystatechange`");

        // Call the original `onreadystatechange` method
        return oldready.apply(this, arguments);
      }

      console.log("End custom `send`");

      // Call the original `send` method
      return oldsend.apply(this, arguments);
    }
  }
  console.log("End custom `open`");

  // Call the original `open` method
  return oldopen.apply(this, arguments);
}