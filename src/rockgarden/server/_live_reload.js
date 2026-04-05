(function() {
  var overlay = null;

  function connect() {
    var es = new EventSource('/_rockgarden/events');
    es.addEventListener('reload', function() {
      if (overlay) overlay.remove();
      location.reload();
    });
    es.addEventListener('error-build', function() {
      if (!overlay) {
        overlay = document.createElement('div');
        overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;padding:8px 16px;background:#dc2626;color:white;font-family:monospace;font-size:14px;z-index:99999;text-align:center;';
      }
      overlay.textContent = 'Build error \u2014 check terminal';
      document.body.appendChild(overlay);
    });
    es.onerror = function() {
      es.close();
      setTimeout(connect, 2000);
    };
  }

  connect();
})();
